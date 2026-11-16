"""
aleph_core/verification/ast_smt.py
Extractor de contratos Hoare/Dafny desde AST (decoradores y docstrings) y constructor simbólico dual
(Z3 SMT nativo + Evaluador Relacional Simbólico Pure-Python para entornos air-gapped sin z3-solver).
Soporta intrínsecos matemáticos (len, abs, min, max, int, bool), expresiones ternarias (IfExp) y cadenas relacionales.
"""
import ast
import threading
from typing import Dict, List, Tuple, Any, Optional, Callable

try:
    import z3
    HAS_Z3 = True
except ImportError:
    z3 = None
    HAS_Z3 = False

_THREAD_LOCAL_SOLVER = threading.local()


def prove_formula_unsat(formula: Any, timeout_ms: int = 200) -> Optional[bool]:
    """
    Verifica si una fórmula Z3 es insatisfactible (UNSAT) usando un z3.Solver()
    thread-local con push()/pop() y timeout acotado.
    Retorna True si UNSAT, False si SAT, o None si UNKNOWN o z3-solver no está disponible.
    """
    if not HAS_Z3 or z3 is None:
        return None
    if isinstance(formula, bool):
        formula = z3.BoolVal(formula)
    solver = getattr(_THREAD_LOCAL_SOLVER, "solver", None)
    if solver is None:
        solver = z3.Solver()
        _THREAD_LOCAL_SOLVER.solver = solver
    solver.set("timeout", max(1, int(timeout_ms)))
    solver.push()
    try:
        solver.add(formula)
        res = solver.check()
        if res == z3.unsat:
            return True
        if res == z3.sat:
            return False
        return None
    finally:
        solver.pop()

class ASTContractExtractor:
    """Extrae precondiciones, poscondiciones e invariantes desde AST (decoradores y docstrings)."""
    @staticmethod
    def extract_from_ast(func_node: ast.FunctionDef) -> Tuple[List[str], List[str], List[str]]:
        preconditions: List[str] = []
        postconditions: List[str] = []
        invariants: List[str] = []

        for decorator in func_node.decorator_list:
            if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
                dec_name = decorator.func.id
                if dec_name == "requires" and decorator.args:
                    arg = decorator.args[0]
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        preconditions.append(arg.value)
                elif dec_name == "ensures" and decorator.args:
                    arg = decorator.args[0]
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        postconditions.append(arg.value)
                elif dec_name == "invariant" and decorator.args:
                    arg = decorator.args[0]
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        invariants.append(arg.value)

        docstring = ast.get_docstring(func_node)
        if docstring:
            for line in docstring.splitlines():
                line = line.strip()
                if line.lower().startswith("requires:"):
                    preconditions.append(line.split(":", 1)[1].strip())
                elif line.lower().startswith("ensures:"):
                    postconditions.append(line.split(":", 1)[1].strip())
                elif line.lower().startswith("invariant:"):
                    invariants.append(line.split(":", 1)[1].strip())

        return preconditions, postconditions, invariants

class SMTExpressionBuilder:
    """
    Compilador de expresiones AST a fórmulas SMT.
    Si Z3 está presente, emite nodos z3.ExprRef; si no está presente, emite árboles de expresiones
    simbólicas evaluables por el Solver Relacional acotado de El Aleph.
    """
    def __init__(
        self,
        var_env: Dict[str, Any],
        use_bitvectors: bool = False,
        bv_bits: int = 32,
        name_resolver: Optional[Callable[[str], str]] = None
    ):
        self.var_env = var_env
        self.use_bitvectors = use_bitvectors
        self.bv_bits = bv_bits
        self.name_resolver = name_resolver

    def get_var(self, name: str) -> Any:
        if name not in self.var_env:
            if HAS_Z3:
                if self.use_bitvectors:
                    self.var_env[name] = z3.BitVec(name, self.bv_bits)
                else:
                    self.var_env[name] = z3.Int(name)
            else:
                self.var_env[name] = ("VAR", name)
        return self.var_env[name]

    def parse_expr_string(self, expr_str: str, resolver: Optional[Callable[[str], str]] = None) -> Any:
        old_resolver = self.name_resolver
        if resolver is not None:
            self.name_resolver = resolver
        try:
            tree = ast.parse(expr_str, mode="eval")
            return self.compile_node(tree.body)
        finally:
            self.name_resolver = old_resolver

    def compile_node(self, node: ast.AST) -> Any:
        if not HAS_Z3:
            return self._compile_symbolic(node)
        return self._compile_z3(node)

    def _compile_symbolic(self, node: ast.AST) -> Any:
        if isinstance(node, ast.Constant):
            return ("CONST", node.value)
        elif isinstance(node, ast.Name):
            var_name = self.name_resolver(node.id) if self.name_resolver else node.id
            self.get_var(var_name)
            return ("VAR", var_name)
        elif isinstance(node, ast.UnaryOp):
            op_val = self._compile_symbolic(node.operand)
            if isinstance(node.op, ast.Not):
                return ("NOT", op_val)
            elif isinstance(node.op, ast.USub):
                return ("NEG", op_val)
            elif isinstance(node.op, ast.UAdd):
                return op_val
            elif isinstance(node.op, ast.Invert):
                return ("BITNOT", op_val)
        elif isinstance(node, ast.BinOp):
            left = self._compile_symbolic(node.left)
            right = self._compile_symbolic(node.right)
            if isinstance(node.op, ast.Pow):
                if (
                    isinstance(node.right, ast.Constant)
                    and isinstance(node.right.value, int)
                    and not isinstance(node.right.value, bool)
                    and 0 <= node.right.value <= 8
                ):
                    exp = node.right.value
                    if exp == 0:
                        return ("CONST", 1)
                    if exp == 1:
                        return left
                    acc = left
                    for _ in range(exp - 1):
                        acc = ("BINOP", "*", acc, left)
                    return acc
            op_map = {
                ast.Add: "+",
                ast.Sub: "-",
                ast.Mult: "*",
                ast.Div: "//",
                ast.FloorDiv: "//",
                ast.Mod: "%",
                ast.BitAnd: "&",
                ast.BitOr: "|",
                ast.BitXor: "^",
                ast.LShift: "<<",
                ast.RShift: ">>",
            }
            for k, sym in op_map.items():
                if isinstance(node.op, k):
                    return ("BINOP", sym, left, right)
        elif isinstance(node, ast.BoolOp):
            vals = [self._compile_symbolic(v) for v in node.values]
            return ("BOOLOP", "AND" if isinstance(node.op, ast.And) else "OR", vals)
        elif isinstance(node, ast.Compare):
            left = self._compile_symbolic(node.left)
            conds = []
            curr_l = left
            for op, comp in zip(node.ops, node.comparators):
                curr_r = self._compile_symbolic(comp)
                if isinstance(op, ast.Eq):
                    conds.append(("CMP", "==", curr_l, curr_r))
                elif isinstance(op, ast.NotEq):
                    conds.append(("CMP", "!=", curr_l, curr_r))
                elif isinstance(op, ast.Lt):
                    conds.append(("CMP", "<", curr_l, curr_r))
                elif isinstance(op, ast.LtE):
                    conds.append(("CMP", "<=", curr_l, curr_r))
                elif isinstance(op, ast.Gt):
                    conds.append(("CMP", ">", curr_l, curr_r))
                elif isinstance(op, ast.GtE):
                    conds.append(("CMP", ">=", curr_l, curr_r))
                elif isinstance(op, ast.IsNot) and isinstance(comp, ast.Constant) and comp.value is None:
                    conds.append(("CMP", "!=", curr_l, ("CONST", 0)))
                elif isinstance(op, ast.Is) and isinstance(comp, ast.Constant) and comp.value is None:
                    conds.append(("CMP", "==", curr_l, ("CONST", 0)))
                elif isinstance(op, ast.In) and isinstance(curr_l, tuple) and curr_l[0] == "CONST" and isinstance(curr_l[1], str):
                    d_name = ast.unparse(comp)
                    k_name = curr_l[1]
                    has_v = self.get_var(f"{d_name}_has_{k_name}")
                    conds.append(("CMP", "==", has_v, ("CONST", True)))
                elif isinstance(op, ast.NotIn) and isinstance(curr_l, tuple) and curr_l[0] == "CONST" and isinstance(curr_l[1], str):
                    d_name = ast.unparse(comp)
                    k_name = curr_l[1]
                    has_v = self.get_var(f"{d_name}_has_{k_name}")
                    conds.append(("CMP", "==", has_v, ("CONST", False)))
                curr_l = curr_r
            return conds[0] if len(conds) == 1 else ("BOOLOP", "AND", conds)
        elif isinstance(node, ast.IfExp):
            return ("IFEXP", self._compile_symbolic(node.test), self._compile_symbolic(node.body), self._compile_symbolic(node.orelse))
        elif isinstance(node, ast.Subscript):
            if isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, str):
                d_name = node.value.id if isinstance(node.value, ast.Name) else "d"
                k_name = node.slice.value
                self.get_var(f"{d_name}_has_{k_name}")
                self.get_var(f"{d_name}_val_{k_name}")
                return ("VAR", f"{d_name}_val_{k_name}")
            arr_name = node.value.id if isinstance(node.value, ast.Name) else "arr"
            self.get_var(f"{arr_name}_len")
            return ("SUBSCRIPT", arr_name, self._compile_symbolic(node.slice))
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            fn_id = node.func.id
            if fn_id == "len" and node.args:
                arg = node.args[0]
                if isinstance(arg, ast.Name):
                    return self.get_var(f"{arg.id}_len")
                return ("CONST", 0)
            elif fn_id == "abs" and len(node.args) == 1:
                x_expr = self._compile_symbolic(node.args[0])
                return ("IFEXP", ("CMP", ">=", x_expr, ("CONST", 0)), x_expr, ("NEG", x_expr))
            elif fn_id == "max" and len(node.args) >= 2:
                acc = self._compile_symbolic(node.args[0])
                for nxt in node.args[1:]:
                    r_expr = self._compile_symbolic(nxt)
                    acc = ("IFEXP", ("CMP", ">=", acc, r_expr), acc, r_expr)
                return acc
            elif fn_id == "min" and len(node.args) >= 2:
                acc = self._compile_symbolic(node.args[0])
                for nxt in node.args[1:]:
                    r_expr = self._compile_symbolic(nxt)
                    acc = ("IFEXP", ("CMP", "<=", acc, r_expr), acc, r_expr)
                return acc
            elif fn_id == "int" and len(node.args) == 1:
                return self._compile_symbolic(node.args[0])
            elif fn_id == "bool" and len(node.args) == 1:
                x_expr = self._compile_symbolic(node.args[0])
                return ("CMP", "!=", x_expr, ("CONST", 0))
        elif isinstance(node, ast.Attribute):
            attr_full = f"{ast.unparse(node.value)}_{node.attr}"
            return self.get_var(attr_full)
        raise NotImplementedError(f"Nodo AST no soportado: {ast.dump(node)}")

    def _coerce_z3_int(self, expr: Any) -> Any:
        if isinstance(expr, z3.BoolRef):
            return z3.If(expr, z3.IntVal(1), z3.IntVal(0))
        if isinstance(expr, z3.BitVecRef):
            return z3.BV2Int(expr, is_signed=True)
        return expr

    def _coerce_z3_bv(self, expr: Any) -> Any:
        if isinstance(expr, z3.BoolRef):
            return z3.If(expr, z3.BitVecVal(1, self.bv_bits), z3.BitVecVal(0, self.bv_bits))
        if isinstance(expr, z3.ArithRef):
            return z3.Int2BV(expr, self.bv_bits)
        return expr

    def _compile_z3(self, node: ast.AST) -> Any:
        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool):
                return z3.BoolVal(node.value)
            elif isinstance(node.value, int):
                return z3.BitVecVal(node.value, self.bv_bits) if self.use_bitvectors else z3.IntVal(node.value)
            elif node.value is None:
                return z3.IntVal(0)
        elif isinstance(node, ast.Name):
            var_name = self.name_resolver(node.id) if self.name_resolver else node.id
            return self.get_var(var_name)
        elif isinstance(node, ast.UnaryOp):
            operand = self._compile_z3(node.operand)
            if isinstance(node.op, ast.Not):
                return z3.Not(operand)
            elif isinstance(node.op, ast.USub):
                return -operand
            elif isinstance(node.op, ast.UAdd):
                return operand
            elif isinstance(node.op, ast.Invert):
                if self.use_bitvectors:
                    return ~self._coerce_z3_bv(operand)
                op_int = self._coerce_z3_int(operand)
                return -(op_int + z3.IntVal(1))
        elif isinstance(node, ast.BinOp):
            left = self._compile_z3(node.left)
            right = self._compile_z3(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            elif isinstance(node.op, ast.Sub):
                return left - right
            elif isinstance(node.op, ast.Mult):
                return left * right
            elif isinstance(node.op, (ast.Div, ast.FloorDiv)):
                return left / right
            elif isinstance(node.op, ast.Mod):
                return z3.SMod(left, right) if self.use_bitvectors else (left % right)
            elif isinstance(node.op, (ast.BitAnd, ast.BitOr, ast.BitXor, ast.LShift, ast.RShift)):
                if self.use_bitvectors:
                    lb = self._coerce_z3_bv(left)
                    rb = self._coerce_z3_bv(right)
                    if isinstance(node.op, ast.BitAnd):
                        return lb & rb
                    elif isinstance(node.op, ast.BitOr):
                        return lb | rb
                    elif isinstance(node.op, ast.BitXor):
                        return lb ^ rb
                    elif isinstance(node.op, ast.LShift):
                        return lb << rb
                    else:
                        return lb >> rb
                else:
                    lb = z3.Int2BV(self._coerce_z3_int(left), 64)
                    rb = z3.Int2BV(self._coerce_z3_int(right), 64)
                    if isinstance(node.op, ast.BitAnd):
                        bv_res = lb & rb
                    elif isinstance(node.op, ast.BitOr):
                        bv_res = lb | rb
                    elif isinstance(node.op, ast.BitXor):
                        bv_res = lb ^ rb
                    elif isinstance(node.op, ast.LShift):
                        bv_res = lb << rb
                    else:
                        bv_res = lb >> rb
                    return z3.BV2Int(bv_res, is_signed=True)
            elif isinstance(node.op, ast.Pow):
                if (
                    isinstance(node.right, ast.Constant)
                    and isinstance(node.right.value, int)
                    and not isinstance(node.right.value, bool)
                    and 0 <= node.right.value <= 8
                ):
                    exp = node.right.value
                    if exp == 0:
                        return z3.BitVecVal(1, self.bv_bits) if self.use_bitvectors else z3.IntVal(1)
                    base_val = self._coerce_z3_bv(left) if self.use_bitvectors else self._coerce_z3_int(left)
                    if exp == 1:
                        return base_val
                    acc = base_val
                    for _ in range(exp - 1):
                        acc = acc * base_val
                    return acc
        elif isinstance(node, ast.BoolOp):
            values = [self._compile_z3(v) for v in node.values]
            return z3.And(*values) if isinstance(node.op, ast.And) else z3.Or(*values)
        elif isinstance(node, ast.Compare):
            # `'clave' in dict` / `'clave' not in dict`: el string constante de la izquierda
            # no es una expresión SMT; se modela vía la variable booleana `<dict>_has_<clave>`.
            is_membership = (
                len(node.ops) == 1
                and isinstance(node.ops[0], (ast.In, ast.NotIn))
                and isinstance(node.left, ast.Constant)
                and isinstance(node.left.value, str)
            )
            left = None if is_membership else self._compile_z3(node.left)
            conditions = []
            curr_left = left
            for op, comparator in zip(node.ops, node.comparators):
                curr_right = self._compile_z3(comparator)
                if isinstance(op, ast.Eq):
                    cond = (curr_left == curr_right)
                elif isinstance(op, ast.NotEq):
                    cond = (curr_left != curr_right)
                elif isinstance(op, ast.Lt):
                    cond = (curr_left < curr_right)
                elif isinstance(op, ast.LtE):
                    cond = (curr_left <= curr_right)
                elif isinstance(op, ast.Gt):
                    cond = (curr_left > curr_right)
                elif isinstance(op, ast.GtE):
                    cond = (curr_left >= curr_right)
                elif isinstance(op, ast.IsNot) and isinstance(comparator, ast.Constant) and comparator.value is None:
                    cond = (curr_left != z3.IntVal(0))
                elif isinstance(op, ast.Is) and isinstance(comparator, ast.Constant) and comparator.value is None:
                    cond = (curr_left == z3.IntVal(0))
                elif isinstance(op, ast.In) and isinstance(node.left, ast.Constant) and isinstance(node.left.value, str):
                    d_name = ast.unparse(comparator)
                    k_name = node.left.value
                    has_v = self.get_var(f"{d_name}_has_{k_name}")
                    cond = (has_v == z3.BoolVal(True))
                elif isinstance(op, ast.NotIn) and isinstance(node.left, ast.Constant) and isinstance(node.left.value, str):
                    d_name = ast.unparse(comparator)
                    k_name = node.left.value
                    has_v = self.get_var(f"{d_name}_has_{k_name}")
                    cond = (has_v == z3.BoolVal(False))
                else:
                    raise NotImplementedError(f"Comparación {op} no soportada")
                conditions.append(cond)
                curr_left = curr_right
            return z3.And(*conditions) if len(conditions) > 1 else conditions[0]
        elif isinstance(node, ast.IfExp):
            return z3.If(self._compile_z3(node.test), self._compile_z3(node.body), self._compile_z3(node.orelse))
        elif isinstance(node, ast.Subscript):
            if isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, str):
                d_name = node.value.id if isinstance(node.value, ast.Name) else "d"
                k_name = node.slice.value
                self.get_var(f"{d_name}_has_{k_name}")
                return self.get_var(f"{d_name}_val_{k_name}")
            arr_name = node.value.id if isinstance(node.value, ast.Name) else "arr"
            elem_sort = z3.BitVecSort(self.bv_bits) if self.use_bitvectors else z3.IntSort()
            arr_var = z3.Array(arr_name, elem_sort, elem_sort)
            return z3.Select(arr_var, self._compile_z3(node.slice))
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            fn_id = node.func.id
            if fn_id == "len" and node.args:
                arg = node.args[0]
                if isinstance(arg, ast.Name):
                    return self.get_var(f"{arg.id}_len")
                return z3.Int("len_expr")
            elif fn_id == "abs" and len(node.args) == 1:
                x = self._compile_z3(node.args[0])
                zero = z3.BitVecVal(0, self.bv_bits) if self.use_bitvectors else z3.IntVal(0)
                return z3.If(x >= zero, x, -x)
            elif fn_id == "max" and len(node.args) >= 2:
                acc = self._compile_z3(node.args[0])
                for nxt in node.args[1:]:
                    r = self._compile_z3(nxt)
                    acc = z3.If(acc >= r, acc, r)
                return acc
            elif fn_id == "min" and len(node.args) >= 2:
                acc = self._compile_z3(node.args[0])
                for nxt in node.args[1:]:
                    r = self._compile_z3(nxt)
                    acc = z3.If(acc <= r, acc, r)
                return acc
            elif fn_id == "int" and len(node.args) == 1:
                return self._compile_z3(node.args[0])
            elif fn_id == "bool" and len(node.args) == 1:
                x = self._compile_z3(node.args[0])
                zero = z3.BitVecVal(0, self.bv_bits) if self.use_bitvectors else z3.IntVal(0)
                return x != zero
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "get" and node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
            d_name = ast.unparse(node.func.value)
            k_name = node.args[0].value
            default_val = self._compile_z3(node.args[1]) if len(node.args) > 1 else (z3.BitVecVal(0, self.bv_bits) if self.use_bitvectors else z3.IntVal(0))
            has_v = self.get_var(f"{d_name}_has_{k_name}")
            val_v = self.get_var(f"{d_name}_val_{k_name}")
            return z3.If(has_v == z3.BoolVal(True), val_v, default_val)
        elif isinstance(node, ast.Attribute):
            attr_full_name = f"{ast.unparse(node.value)}_{node.attr}"
            return self.get_var(attr_full_name)
        raise NotImplementedError(f"Nodo AST no soportado: {ast.dump(node)}")
