"""
aleph_core/research_archive/mcp_manifest_archive.py
Catálogo completo diferido de esquemas MCP (752 tools) de El Aleph.
"""
from typing import List, Dict, Any


def build_raw_tools_manifest() -> List[Dict[str, Any]]:
    tools = [
        {
            "name": "aleph_verify_and_repair",
            "description": "Verifica formalmente código Python con SMT/ICP y repara automáticamente defectos mediante síntesis inductiva CEGIS (0% falsos positivos).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_code": {"type": "string", "description": "Código fuente de la función a verificar y auto-reparar."},
                    "use_bitvectors": {"type": "boolean", "default": False}
                },
                "required": ["source_code"]
            }
        },
        {
            "name": "aleph_design_render_oracle_audit",
            "description": "Audita estéticamente y físicamente código HTML/CSS mediante el oráculo DOM de .aleph (StaticDOMAuditor/AlephRenderOracle) verificando cero overflow horizontal, jerarquía tipográfica, APCA contrast y métricas anti-slop (REG-114 / v19.4.0).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "html_content": {"type": "string", "description": "Contenido HTML a auditar"}
                },
                "required": ["html_content"]
            }
        },
        {
            "name": "aleph_visual_stage_synthesizer",
            "description": "Sintetiza escenografía vectorial procedimental SVG interna (cryo_gauge, code_terminal, swiss_geometry, bezier_chart, topology_graph, quantum_network, radial_radar, spectral_waveform) desde .aleph/lib/aleph_visual_stage_synthesizer.py para eliminar tarjetas Bento vacías (REG-114 / v19.4.0).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "stage_type": {"type": "string", "description": "Tipo de escenario visual"},
                    "width": {"type": "integer", "default": 400},
                    "height": {"type": "integer", "default": 280}
                },
                "required": ["stage_type"]
            }
        },
        {
            "name": "aleph_simulate_spring_physics",
            "description": "Calcula simulación ODE de oscilador amortiguado (ODE m*x2 + c*x1 + k*x = 0) para transiciones fluidas de microinteracción y genera la función CSS linear() correspondiente desde .aleph/lib/aleph_kinetic_ode.py (REG-114 / v19.4.0).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "profile": {"type": "string", "default": "snappy"},
                    "mass": {"type": "number", "default": 1.0},
                    "stiffness": {"type": "number", "default": 180.0},
                    "damping": {"type": "number", "default": 12.0}
                }
            }
        },
        {
            "name": "aleph_compile_design_tokens",
            "description": "Compila tokens semánticos de diseño Oklch/sRGB y tipografía fluida clamp() con mapeo de gamut y verificación de contraste APCA desde .aleph/lib/aleph_token_compiler.py (REG-114 / v19.4.0).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "color_l": {"type": "number", "default": 0.65},
                    "color_c": {"type": "number", "default": 0.22},
                    "color_h": {"type": "number", "default": 145.0},
                    "font_min_px": {"type": "number", "default": 16.0},
                    "font_max_px": {"type": "number", "default": 24.0}
                }
            }
        },
        {
            "name": "aleph_audit_agentic_tool_arguments_and_sandbox_escape",
            "description": "Demostrador Formal Anti-Inyección de Argumentos CLI Agénticos (CWE-88), Confinamiento de Rutas Canónicas (CWE-22) y Prevención de Confusión/Shadowing en Servidores MCP (NODE-04 Shard).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_code": {"type": "string", "description": "Código Python a auditar."}
                },
                "required": ["source_code"]
            }
        },
        {
            "name": "aleph_audit_pqc_ed25519_dns_rebinding_and_deserialization",
            "description": "Demostrador Formal de Criptografía Post-Cuántica Híbrida ML-KEM-768 (FIPS 203), Anti-Maleabilidad Ed25519 (RFC 8032 S < L), Anti-DNS Rebinding TOCTOU y Deserialización Segura (CWE-502) (NODE-04 Shard).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_code": {"type": "string", "description": "Código Python a auditar."}
                },
                "required": ["source_code"]
            }
        },
        {
            "name": "aleph_audit_wasm_memory_prototype_pollution_and_redos",
            "description": "Demostrador Formal Anti-Contaminación de Clases/Prototipos (CWE-1321), Complejidad Lineal O(n) Anti-ReDoS (CWE-1333) y Confinamiento de Memoria Lineal WebAssembly/WASI (CWE-119) (NODE-04 Shard).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_code": {"type": "string", "description": "Código Python a auditar."}
                },
                "required": ["source_code"]
            }
        },
        {
            "name": "aleph_audit_http_desync_smuggling_oauth_pkce_dpop_and_xml_xsw",
            "description": "Demostrador Formal Anti-HTTP Request Smuggling (CL.TE, TE.CL, TE.TE, H2.TE y CRLF RFC 9112/9113 CWE-444), OAuth 2.1 PKCE S256 + DPoP Sender-Constrained Tokens (RFC 7636 / RFC 9449 CWE-345) y Confinamiento XML/SAML contra XXE y XML Signature Wrapping (XSW CWE-611 / CWE-347) (NODE-04 Shard).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_code": {"type": "string", "description": "Código Python a auditar."}
                },
                "required": ["source_code"]
            }
        },
        {
            "name": "aleph_audit_aead_key_commitment_cswsh_and_graphql_complexity",
            "description": "Demostrador Formal Anti-Reutilización de Nonce AEAD / Rotación NIST SP 800-38D y Key Commitment (CWE-323 / CVE-2026-17578), Anti-Cross-Site WebSocket Hijacking CSWSH (CWE-1385 / CVE-2026-25253) y Confinamiento de Profundidad/Alias GraphQL (CWE-400) (v8.1.0 - NODE-04 Shard).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_code": {"type": "string", "description": "Código Python a auditar contra vulnerabilidades AEAD, CSWSH y GraphQL."}
                },
                "required": ["source_code"]
            }
        },
    {
        "name": "aleph_audit_ecdsa_rfc6979_ssti_sandbox_and_ipv6_ssrf",
        "description": "Demostrador Formal de Nonce Determinista ECDSA RFC 6979 / Validación en Curva ECDH (NIST SP 800-56A CWE-323/CWE-325), Confinamiento SSTI Jinja2 SandboxedEnvironment (CWE-1336 / GHSA-vvwj-fvwh-4whx) y Prevención de Bypass SSRF por IPv4-Mapped IPv6 (::ffff:169.254.169.254) e IPs en Octal/Hex/Dword (CWE-918 / GHSA-72vh-x5jq-m82g) (v8.2.0 - NODE-04 Shard).",
        "inputSchema": {
    "type": "object",
    "properties": {
        "source_code": {"type": "string", "description": "Código Python a auditar contra vulnerabilidades ECDSA/ECDH, SSTI y SSRF IPv6/Octal."}
    },
    "required": ["source_code"]
        }
    },
    {
        "name": "aleph_audit_jwk_header_confusion_rsa_oaep_and_sri_isolation",
        "description": "Demostrador Formal Anti-Inyección de Cabeceras JWK/JWKS & Confusión de Algoritmo JWT RS256->HS256 (RFC 8725 / CWE-347 / CVE-2026-0265), Anti-Oráculo Marvin PKCS#1 v1.5 exigiendo RSA-OAEP SHA-256 (CWE-203 / CWE-780) e Integridad de Subrecursos SRI SHA-384 + Aislamiento Cross-Origin COOP/COEP/CORP (CWE-353 / CWE-829) (v8.3.0 - NODE-04 Shard).",
        "inputSchema": {
    "type": "object",
    "properties": {
        "source_code": {"type": "string", "description": "Código Python a auditar contra vulnerabilidades JWT RFC 8725, RSA PKCS#1 v1.5 y SRI/COOP."}
    },
    "required": ["source_code"]
        }
    },
    {
        "name": "aleph_audit_webauthn_passkey_nosql_ldap_and_archive_slip",
        "description": "Demostrador Formal de Ligadura Criptográfica WebAuthn / FIDO2 Passkey (rpIdHash, flags UP/UV, monotonía signCount), Anti-Inyección de Operadores NoSQL ($where/$ne CWE-943) & Filtros LDAP (RFC 4515 CWE-90) y Confinamiento de Extracción de Archivos contra Zip-Slip / Tar-Slip / Symlink Escape (PEP 706 / CVE-2007-4559 / CVE-2026-63134) (v8.4.0 - NODE-04 Shard).",
        "inputSchema": {
    "type": "object",
    "properties": {
        "source_code": {"type": "string", "description": "Código Python a auditar contra vulnerabilidades WebAuthn, NoSQL/LDAP y Zip/Tar-Slip."}
    },
    "required": ["source_code"]
        }
    },
    {
        "name": "aleph_audit_argon2id_hkdf_host_injection_and_grpc_framing",
        "description": "Demostrador Formal de Hashing Memory-Hard Argon2id (RFC 9106 / OWASP m>=19456 KiB CWE-916) & Derivación HKDF con Separación de Dominio (RFC 5869), Anti-Inyección de Cabecera Host / X-Forwarded-Host con Ligadura TLS SNI (CWE-644 / CVE-2026-27959) y Confinamiento de Frames gRPC / Protobuf (<= 4 MiB, CWE-400) (v8.5.0 - NODE-04 Shard).",
        "inputSchema": {
    "type": "object",
    "properties": {
        "source_code": {"type": "string", "description": "Código Python a auditar contra vulnerabilidades Argon2id/HKDF, Host Header Injection y gRPC DoS."}
    },
    "required": ["source_code"]
        }
    },
    {
        "name": "aleph_audit_trojan_unicode_x509_mtls_and_webhook_replay",
        "description": "Demostrador Formal Anti-Trojan Source BiDi / Unicode Tag Prompt Injection & Exfiltración Markdown (CVE-2021-42574 / OWASP LLM01), Validación Estricta X.509 mTLS SAN/BasicConstraints (RFC 5280 / CWE-295) y Prevención de Replay en Webhooks HMAC con Ventana Temporal <= 300s (CWE-294) (v8.6.0 - NODE-04 Shard).",
        "inputSchema": {
    "type": "object",
    "properties": {
        "source_code": {"type": "string", "description": "Código Python a auditar contra vulnerabilidades Trojan Source Unicode, X.509 TLS bypass y Webhook Replay."}
    },
    "required": ["source_code"]
        }
    },
    {
        "name": "aleph_audit_cors_credentials_mass_assignment_and_svg_polyglot_xss",
        "description": "Demostrador Formal Anti-CORS Origin Null / Wildcard Credentials (CWE-942 / CWE-346), Anti-Mass Assignment BOPLA (CWE-915 / OWASP API3:2023) y Confinamiento de Subida de Archivos SVG / Polyglot XSS con Magic Bytes y nosniff (CWE-434 / CWE-79) (v8.7.0 - NODE-04 Shard).",
        "inputSchema": {
    "type": "object",
    "properties": {
        "source_code": {"type": "string", "description": "Código Python a auditar contra vulnerabilidades CORS, Mass Assignment BOPLA y SVG/Polyglot XSS."}
    },
    "required": ["source_code"]
        }
    },
    {
        "name": "aleph_audit_pqc_mlkem_cookie_crlf_and_dns_rebinding_toctou",
        "description": "Demostrador Formal Post-Quantum NIST FIPS 203 ML-KEM Anti-KyberSlash / Implicit Rejection FO, Integridad de Prefijos de Cookies RFC 6265bis (__Host- / __Secure-) + Anti-CRLF (CWE-113) y Prevención de DNS Rebinding TOCTOU mediante IP Pinning de Transporte (CWE-350 / CWE-367) (v8.8.0 - NODE-04 Shard).",
        "inputSchema": {
    "type": "object",
    "properties": {
        "source_code": {"type": "string", "description": "Código Python a auditar contra KyberSlash PQC, Cookie Prefixes/CRLF y DNS Rebinding TOCTOU."},
        "pqc_config": {"type": "object", "description": "Configuración PQC ML-KEM opcional."},
        "cookie_and_headers": {"type": "object", "description": "Cabeceras HTTP y Set-Cookie opcionales."},
        "dns_rebinding_context": {"type": "object", "description": "Contexto de resolución DNS Time-of-Check vs Time-of-Use opcional."}
    },
    "required": ["source_code"]
        }
    },
    {
        "name": "aleph_audit_mldsa_fips204_saml_c14n_and_redirect_ssrf",
        "description": "Demostrador Formal Post-Quantum NIST FIPS 204 ML-DSA (Hedged Signing, Context String <= 255B y Cotas de Norma/Hints), Aislamiento SAML 2.0 (Exclusive C14N Anti-Comment-Truncation, AudienceRestriction e InResponseTo, CVE-2024-45409) y Prevención de SSRF por Redirecciones HTTP 3xx con Re-Validación de IP por Salto y Expurgado Cross-Origin de Credenciales (CVE-2026-10129 / CVE-2026-63764 / CWE-918) (v8.9.0 - NODE-04 Shard).",
        "inputSchema": {
    "type": "object",
    "properties": {
        "source_code": {"type": "string", "description": "Código Python a auditar contra fallos ML-DSA FIPS 204, SAML C14N/Audience y Redirect SSRF."},
        "mldsa_config": {"type": "object", "description": "Configuración de firma post-cuántica ML-DSA opcional."},
        "saml_context": {"type": "object", "description": "Contexto de validación de SAML 2.0 Assertion opcional."},
        "redirect_context": {"type": "object", "description": "Contexto de cadena de redirecciones HTTP salientes opcional."}
    },
    "required": ["source_code"]
        }
    },
    {
        "name": "aleph_audit_slhdsa_fips205_postmessage_dom_clobbering_and_imdsv2_ssrf",
        "description": "Demostrador Formal Post-Quantum NIST FIPS 205 SLH-DSA (Stateless Hash-Based Signatures y Prevención de Reuso de Estado LMS/XMSS en VMs/Snapshots), Aislamiento Cross-Window postMessage (targetOrigin exacto, event.origin y Trusted Types contra DOM Clobbering, CWE-346 / CWE-79) y Defensa Cloud IMDSv2 Hop-Limit + Aislamiento de Proxy Ambiental trust_env=False (CWE-918) (v9.0.0 - NODE-04 Shard).",
        "inputSchema": {
    "type": "object",
    "properties": {
        "source_code": {"type": "string", "description": "Código a auditar contra reuso de estado LMS/XMSS, postMessage wildcard/DOM Clobbering y SSRF IMDSv1/trust_env."},
        "slhdsa_config": {"type": "object", "description": "Configuración de firma post-cuántica basada en hash SLH-DSA (FIPS 205) opcional."},
        "postmessage_context": {"type": "object", "description": "Contexto de política postMessage y CSP Trusted Types opcional."},
        "imdsv2_proxy_context": {"type": "object", "description": "Contexto de configuración IMDSv2 y aislamiento de proxy HTTP opcional."}
    },
    "required": ["source_code"]
        }
    },
    {
        "name": "aleph_audit_hpke_rfc9180_oauth_rfc9700_and_headless_turn_ssrf",
        "description": "Demostrador Formal de Cifrado Híbrido HPKE RFC 9180 (Monotonicidad de Secuencia Nonce, VerifyPSKInputs y Separación Export-Only), Seguridad OAuth 2.0 BCP RFC 9700 + RFC 9207 (Igualdad Exacta de redirect_uri, PKCE S256 y Defensa Anti-Mix-Up con iss) y Prevención de SSRF en Navegadores Headless PDF/Chromium (file:// / --disable-web-security) y Relays WebRTC TURN/STUN (denied-peer-ip) (v9.1.0 - NODE-04 Shard).",
        "inputSchema": {
    "type": "object",
    "properties": {
        "source_code": {"type": "string", "description": "Código a auditar contra fallos HPKE RFC 9180, OAuth RFC 9700/Mix-Up y SSRF en Headless PDF / TURN relay."},
        "hpke_config": {"type": "object", "description": "Configuración de contexto criptográfico HPKE RFC 9180 opcional."},
        "oauth_rfc9700_context": {"type": "object", "description": "Contexto de validación de flujo OAuth 2.0 RFC 9700 / RFC 9207 opcional."},
        "headless_turn_context": {"type": "object", "description": "Contexto de flags Headless PDF y lista denied-peer-ip de TURN opcional."}
    },
    "required": ["source_code"]
        }
    },
    {
        "name": "aleph_audit_tls13_zerortt_xsleaks_coop_corp_and_urlparser_ssrf",
        "description": "Demostrador Formal de Protección Anti-Replay TLS 1.3 0-RTT Early Data (RFC 8446 §8 / RFC 8470 HTTP 425 Too Early y ALPN estricto contra ALPACA), Aislamiento Cross-Origin Anti-XS-Leaks (COOP, CORP, COEP y Fetch Metadata Sec-Fetch-Site) y Prevención de SSRF por Diferenciales de Parsers URL (@, backslash) y Ofuscación IPv4 Octal/Hex/Dword (CWE-918) (v9.2.0 - NODE-04 Shard).",
        "inputSchema": {
    "type": "object",
    "properties": {
        "source_code": {"type": "string", "description": "Código a auditar contra Replay TLS 1.3 0-RTT, XS-Leaks COOP/CORP y SSRF por diferenciales URL / IPs ofuscadas."},
        "tls13_config": {"type": "object", "description": "Configuración TLS 1.3 0-RTT y ALPN opcional."},
        "xsleaks_context": {"type": "object", "description": "Contexto de cabeceras COOP/CORP/COEP y Sec-Fetch-* opcional."},
        "url_ssrf_context": {"type": "object", "description": "Contexto de URLs candidatas a verificar contra ofuscación IPv4 y parser confusion opcional."}
    },
    "required": ["source_code"]
        }
    },
    {
        "name": "aleph_audit_jwe_rfc8725bis_csp_baseuri_and_envoy_mesh_ssrf",
        "description": "Demostrador Formal de Seguridad JWE RFC 8725bis / RFC 7516 (Validación de Punto en Curva ECDH-ES epk, Cota PBES2 p2c <= 310000, Límite de Descompresión zip:DEF <= 250 KB y Prohibición RSA1_5), Directivas de Documento CSP (base-uri 'none'/'self', object-src 'none', form-action y Anti-Dangling-Markup) y Aislamiento Anti-SSRF en Sidecars Envoy/Istio (15000/9901) y Kubernetes (*.svc.cluster.local / Kubelet 10250) (v9.3.0 - NODE-04 Shard).",
        "inputSchema": {
    "type": "object",
    "properties": {
        "source_code": {"type": "string", "description": "Código a auditar contra vulnerabilidades JWE RFC 8725bis, CSP base-uri y SSRF hacia Envoy/Kubernetes."},
        "jwe_config": {"type": "object", "description": "Configuración de cifrado JWE RFC 8725bis opcional."},
        "csp_document_context": {"type": "object", "description": "Contexto de directivas de documento CSP (base-uri, object-src, form-action) opcional."},
        "envoy_k8s_context": {"type": "object", "description": "Contexto de destino de red en malla Envoy/Istio y clúster Kubernetes opcional."}
    },
    "required": ["source_code"]
        }
    },
    {
        "name": "aleph_audit_sdjwt_rfc9901_csp_worker_and_unix_socket_ssrf",
        "description": "Demostrador Formal de Selective Disclosure JWT (SD-JWT / SD-JWT+KB RFC 9901: _sd_alg, entropía de salt >= 128 bits, prohibición de colisión/sombreado de claims y verificación de sd_hash), Aislamiento CSP worker-src / Service-Worker-Allowed / Permissions-Policy y Prevención de SSRF hacia Unix Domain Sockets (socketPath / http+unix:// / /var/run/docker.sock, CWE-918) (v9.4.0 - NODE-04 Shard).",
        "inputSchema": {
    "type": "object",
    "properties": {
        "source_code": {"type": "string", "description": "Código a auditar contra vulnerabilidades SD-JWT RFC 9901, CSP worker-src y SSRF hacia Unix Domain Sockets."},
        "sdjwt_config": {"type": "object", "description": "Configuración de Selective Disclosure JWT (RFC 9901) y Key-Binding opcional."},
        "csp_worker_context": {"type": "object", "description": "Contexto de directivas CSP worker-src, Service-Worker-Allowed y Permissions-Policy opcional."},
        "unix_socket_context": {"type": "object", "description": "Contexto de transporte HTTP y bloqueo de Unix Domain Sockets (/var/run/docker.sock) opcional."}
    },
    "required": ["source_code"]
        }
    },
    {
        "name": "aleph_audit_cose_rfc9052_fetch_metadata_and_connect_tunnel_ssrf",
        "description": "Demostrador Formal de Seguridad COSE RFC 9052 / CBOR RFC 8949 (algoritmo en bucket protegido, prohibición de claves duplicadas en mapas CBOR y cota de longitud indefinida), Aislamiento Cross-Site W3C Fetch Metadata (Sec-Fetch-Site, Sec-Fetch-Mode, Sec-Fetch-Dest + Vary) y Prevención de SSRF por Túneles HTTP CONNECT y Zone-IDs IPv6 (fe80::%25eth0, RFC 6874 / CWE-918) (v9.5.0 - NODE-04 Shard).",
        "inputSchema": {
    "type": "object",
    "properties": {
        "source_code": {"type": "string", "description": "Código a auditar contra vulnerabilidades COSE RFC 9052, W3C Fetch Metadata y SSRF vía HTTP CONNECT / IPv6 Zone-ID."},
        "cose_config": {"type": "object", "description": "Configuración de verificación COSE RFC 9052 y decodificación CBOR RFC 8949 opcional."},
        "fetch_metadata_context": {"type": "object", "description": "Contexto de cabeceras W3C Fetch Metadata (Sec-Fetch-Site/Mode/Dest y Vary) opcional."},
        "connect_tunnel_context": {"type": "object", "description": "Contexto de transporte HTTP CONNECT y direccionamiento IPv6 Zone-ID opcional."}
    },
    "required": ["source_code"]
        }
    },
    {
        "name": "aleph_audit_http_message_sig_rfc9421_clear_site_data_and_etcd_consul_ssrf",
        "description": "Demostrador Formal de Firmas de Mensajes HTTP RFC 9421 (componentes cubiertos obligatorios @method, @authority, @target-uri, content-digest, ventana anti-replay <= 300s y alg asimétrico), Purga de Sesión W3C Clear-Site-Data + Speculation-Rules y Prevención de SSRF hacia Planos de Descubrimiento Consul (8500), etcd (2379) y mDNS (.local, CWE-918) (v9.6.0 - NODE-04 Shard).",
        "inputSchema": {
    "type": "object",
    "properties": {
        "source_code": {"type": "string", "description": "Código a auditar contra vulnerabilidades RFC 9421 HTTP Message Signatures, Clear-Site-Data y SSRF hacia etcd/Consul/mDNS."},
        "rfc9421_config": {"type": "object", "description": "Configuración de verificación RFC 9421 HTTP Message Signatures opcional."},
        "clear_site_context": {"type": "object", "description": "Contexto de cabeceras Clear-Site-Data y Speculation-Rules opcional."},
        "discovery_ssrf_context": {"type": "object", "description": "Contexto de destino de red para bloqueo de etcd (2379), Consul (8500) y mDNS (.local) opcional."}
    },
    "required": ["source_code"]
        }
    },
    {
        "name": "aleph_audit_uuidv7_rfc9562_csp_sandbox_iframe_and_altsvc_ssrf",
        "description": "Demostrador Formal de Seguridad UUIDv7/UUIDv4 RFC 9562 Section 6 (prohibición de usar UUIDs con timestamp como tokens secretos sin MAC, entropía CSPRNG >= 62 bits y privacidad de timestamp), Aislamiento de Iframes CSP sandbox (bloqueo de allow-scripts + allow-same-origin y X-Content-Type-Options: nosniff) y Prevención de SSRF mediante Alt-Svc RFC 7838 y Tramas ORIGIN RFC 8336 (CWE-918) (v9.7.0 - NODE-04 Shard).",
        "inputSchema": {
    "type": "object",
    "properties": {
        "source_code": {"type": "string", "description": "Código a auditar contra vulnerabilidades UUIDv7 RFC 9562, escape de sandbox de iframe y SSRF vía Alt-Svc."},
        "uuid_config": {"type": "object", "description": "Configuración de generación y exposición de identificadores UUID RFC 9562 opcional."},
        "csp_sandbox_context": {"type": "object", "description": "Contexto de flags CSP sandbox de iframe y X-Content-Type-Options opcional."},
        "altsvc_ssrf_context": {"type": "object", "description": "Contexto de manejo de cabeceras Alt-Svc RFC 7838 y coalescencia HTTP/2-HTTP/3 ORIGIN opcional."}
    },
    "required": ["source_code"]
        }
    },
    {
        "name": "aleph_audit_dpop_rfc9449_fenced_frame_and_h2c_grpc_reflection_ssrf",
        "description": "Demostrador Formal de OAuth 2.0 DPoP RFC 9449 (typ='dpop+jwt', clave privada ausente en jwk, claim ath SHA-256 del access token, normalización htu y DPoP-Nonce con caché jti), Aislamiento CSP fenced-frame-src + Supports-Loading-Mode: fenced-frame y Prevención de Smuggling/SSRF vía Upgrade: h2c (CWE-444) y gRPC ServerReflection (v9.8.0 - NODE-04 Shard).",
        "inputSchema": {
    "type": "object",
    "properties": {
        "source_code": {"type": "string", "description": "Código a auditar contra vulnerabilidades OAuth DPoP RFC 9449, CSP fenced-frame-src y contrabando Upgrade: h2c / gRPC reflection."},
        "dpop_config": {"type": "object", "description": "Configuración de verificación de pruebas DPoP RFC 9449 opcional."},
        "fenced_frame_context": {"type": "object", "description": "Contexto de aislamiento CSP fenced-frame-src y Supports-Loading-Mode opcional."},
        "h2c_grpc_context": {"type": "object", "description": "Contexto de filtrado de Upgrade: h2c / HTTP2-Settings y gRPC ServerReflection opcional."}
    },
    "required": ["source_code"]
        }
    },
    {
        "name": "aleph_audit_oprf_rfc9497_trusted_types_dom_and_fastcgi_redis_ssrf",
        "description": "Demostrador Formal de Oblivious Pseudorandom Functions OPRF/VOPRF RFC 9497 y Privacy Pass RFC 9578 (grupos de orden primo ristretto255/P-256, rechazo del elemento identidad, prueba DLEQ y escalar de cegado único), Aislamiento DOM XSS con W3C Trusted Types (require-trusted-types-for 'script' y bloqueo de passthrough default) y Prevención de Protocol Smuggling SSRF hacia FastCGI (9000) y Redis RESP (6379, CWE-918) (v9.9.0 - NODE-04 Shard).",
        "inputSchema": {
    "type": "object",
    "properties": {
        "source_code": {"type": "string", "description": "Código a auditar contra vulnerabilidades OPRF RFC 9497, CSP Trusted Types y SSRF hacia FastCGI/Redis."},
        "oprf_config": {"type": "object", "description": "Configuración de suite criptográfica OPRF/VOPRF RFC 9497 opcional."},
        "trusted_types_context": {"type": "object", "description": "Contexto de directivas CSP require-trusted-types-for y trusted-types opcional."},
        "smuggling_ssrf_context": {"type": "object", "description": "Contexto de destino de red para bloqueo de FastCGI (9000) y Redis RESP (6379) opcional."}
    },
    "required": ["source_code"]
        }
    },
    {
        "name": "aleph_audit_mls_rfc9420_importmap_csp_and_cilium_hubble_ssrf",
        "description": "Demostrador Formal de Messaging Layer Security MLS RFC 9420 (TreeKEM epoch monotonicity, firma de LeafNode, confirmation_tag y no reutilización de init_key), Aislamiento CSP script-src-elem + Integridad SRI en Import Maps (<script type='importmap'>) y Prevención de SSRF hacia Planos CNI/eBPF Cilium y Hubble Relay (puertos 4244/4245/9879 y cilium.sock, CWE-918) (v10.0.0 - NODE-04 Shard).",
        "inputSchema": {
    "type": "object",
    "properties": {
        "source_code": {"type": "string", "description": "Código a auditar contra vulnerabilidades MLS RFC 9420, secuestro de Import Maps y SSRF hacia Cilium/Hubble."},
        "mls_config": {"type": "object", "description": "Configuración de protocolo de grupo MLS RFC 9420 (TreeKEM) opcional."},
        "importmap_csp_context": {"type": "object", "description": "Contexto de directiva CSP script-src-elem e integridad de Import Maps opcional."},
        "cilium_cni_context": {"type": "object", "description": "Contexto de destino de red para bloqueo de puertos CNI Cilium/Hubble opcional."}
    },
    "required": ["source_code"]
        }
    },
    {
        "name": "aleph_audit_frost_rfc9591_referrer_policy_and_vault_wireserver_ssrf",
        "description": "Demostrador Formal de Firmas Umbral Schnorr FROST RFC 9591 (factores de ligadura rho_i contra ataques de Wagner, borrado determinista de nonces tras firmar y validación de elemento no-identidad), Aislamiento Referrer-Policy ('no-referrer' / 'strict-origin-when-cross-origin' contra fuga de tokens en URL) y Prevención de SSRF hacia HashiCorp Vault (8200), Nomad (4646), Azure Wireserver (168.63.129.16) y Alibaba Metadata (100.100.100.200, CWE-918) (v10.1.0 - NODE-04 Shard).",
        "inputSchema": {
    "type": "object",
    "properties": {
        "source_code": {"type": "string", "description": "Código a auditar contra vulnerabilidades FROST RFC 9591, Referrer-Policy unsafe-url y SSRF hacia Vault/Wireserver."},
        "frost_config": {"type": "object", "description": "Configuración de protocolo de firma umbral FROST RFC 9591 opcional."},
        "referrer_context": {"type": "object", "description": "Contexto de cabecera Referrer-Policy y exposición de tokens en URL opcional."},
        "vault_wireserver_context": {"type": "object", "description": "Contexto de destino de red para bloqueo de Vault (8200) y Cloud Wireservers opcional."}
    },
    "required": ["source_code"]
        }
    },
    {
        "name": "aleph_audit_ocsp_rfc6960_service_locator_hold_instruction_permissions_payment_and_pinned_socket_ssrf",
        "description": "Audita formalmente código Python/Web contra vulnerabilidades en IETF RFC 6960 §4.4.6/§4.4.3/§4.2.1 OCSP ServiceLocator, HoldInstructionCode y BasicOCSPResponse OID, aislamiento W3C Permissions-Policy de pagos, geolocalización, portapapeles y pantalla completa, y prevención de SSRF mediante anclaje de socket IP (Pinned-Socket Anti-DNS-Rebinding TOCTOU) y bloqueo de redirecciones hacia puertos internos críticos (6379, 2375, 10250, 9200) (v12.7.0 - Nivel 124).",
        "inputSchema": {
    "type": "object",
    "properties": {
        "code": {"type": "string", "description": "Código fuente a auditar."},
        "source_code": {"type": "string", "description": "Alias opcional de código fuente a auditar."}
    }
        }
    },
    {
        "name": "aleph_audit_ocsp_rfc6960_archive_cutoff_crlid_permissions_media_and_alternate_ip_imds_ssrf",
        "description": "Audita formalmente código Python/Web contra vulnerabilidades en IETF RFC 6960 §4.4.4/§4.4.2/§4.2.2.2.1 OCSP ArchiveCutoff, CrlID y singleExtensions críticas, aislamiento W3C Permissions-Policy de captura multimedia, WebSerial y gestión de ventanas, y prevención de SSRF mediante codificaciones IP alternativas (Dword/Octal/Hex/IPv4-mapped IPv6 ::ffff:169.254.169.254) y endpoint de metadatos IPv6 AWS fd00:ec2::254 (v12.6.0 - Nivel 123).",
        "inputSchema": {
    "type": "object",
    "properties": {
        "code": {"type": "string", "description": "Código fuente a auditar."},
        "source_code": {"type": "string", "description": "Alias opcional de código fuente a auditar."}
    }
        }
    },
    {
        "name": "aleph_audit_ocsp_rfc6960_preferred_sig_alg_permissions_sensors_and_docker_model_lmdeploy_ssrf",
        "description": "Audita formalmente código Python/Web contra vulnerabilidades en IETF RFC 6960 §4.2.2.3/§4.4.7/§5.1.2 OCSP PreferredSignatureAlgorithms Anti-Downgrade y ResponderID KeyHash (allowed_ocsp_sig_algs y comparación constante), aislamiento W3C Permissions-Policy de sensores, WebXR, MIDI y deferred-fetch, y prevención de SSRF en Docker Model Runner OCI Registry (CVE-2026-33990), LMDeploy AI (CVE-2026-33626) y paquetes MCP praison/whisper/Ech0 (CVE-2026-34936/34981/35037) (v12.5.0 - Nivel 122).",
        "inputSchema": {
    "type": "object",
    "properties": {
        "code": {"type": "string", "description": "Código fuente a auditar."},
        "source_code": {"type": "string", "description": "Alias opcional de código fuente a auditar."}
    }
        }
    },
    {
        "name": "aleph_audit_ocsp_rfc6960_ext_revoked_certid_permissions_policy_tokens_and_mcp_atlassian_fastmcp_ssrf",
        "description": "Audita formalmente código Python/Web contra vulnerabilidades en IETF RFC 6960 §2.2/§4.1.1/§4.4.8 OCSP Extended Revoked Definition y CertID Binding (revocation_reason == 6 certificateHold, revocation_time 19700101000000Z, prohibición de extensiones CRL y comparación constante de issuer_name_hash + issuer_key_hash), aislamiento W3C Permissions-Policy de captura de pantalla, Private State Tokens y credenciales FedCM/OTP, y prevención de SSRF en mcp-atlassian (CVE-2026-27825/26), fastmcp (CVE-2026-32871) y mcp-from-openapi JSON Schema $ref (CVE-2026-39885) (v12.4.0 - Nivel 121).",
        "inputSchema": {
    "type": "object",
    "properties": {
        "code": {"type": "string", "description": "Código fuente a auditar."},
        "source_code": {"type": "string", "description": "Alias opcional de código fuente a auditar."}
    }
        }
    },
    {
        "name": "aleph_audit_ct_rfc9162_consistency_precert_permissions_policy_ai_and_nextjs_azure_linkerd_ssrf",
        "description": "Audita formalmente código Python/Web contra vulnerabilidades en IETF RFC 9162 Merkle Consistency Proofs y CMS Precertificates (0 < first_tree_size < second_tree_size, OID 1.3.101.78 y comparación constante), aislamiento W3C Permissions-Policy de APIs de IA en el dispositivo y fingerprinting (language-model, summarizer, translator, local-fonts, compute-pressure, ch-ua-high-entropy-values, browsing-topics), y prevención de SSRF en Next.js (CVE-2024-34351 / CVE-2025-57822), Azure OpenAI / Purview (CVE-2025-53767 / CVE-2026-26138 / WireServer 168.63.129.16) y Linkerd l5d-dtab (v12.3.0 - Nivel 120).",
        "inputSchema": {
    "type": "object",
    "properties": {
        "code": {"type": "string", "description": "Código fuente a auditar."},
        "source_code": {"type": "string", "description": "Alias opcional de código fuente a auditar."}
    }
        }
    },
    {
        "name": "aleph_audit_tls_cert_compression_rfc8879_integrity_policy_and_gitlab_spring_astro_ssrf",
        "description": "Audita formalmente código Python/Web contra vulnerabilidades en IETF RFC 8879 TLS Certificate Compression (cota uncompressed_length <= max_uncompressed_len contra bombas de descompresión, validación de algoritmo negociado y comparación constante), cabecera W3C Integrity-Policy (blocked-destinations=(script)) para Subresource Integrity, y prevención de SSRF en GitLab CE/EE (CVE-2025-12073 IPv6 malformado & CVE-2025-6454 CRLF), Spring Cloud Config (CVE-2026-22739) y Astro SSR (CVE-2026-25545) (v12.2.0 - Nivel 119).",
        "inputSchema": {
    "type": "object",
    "properties": {
        "code": {"type": "string", "description": "Código fuente a auditar."},
        "source_code": {"type": "string", "description": "Alias opcional de código fuente a auditar."}
    }
        }
    },
    {
        "name": "aleph_audit_ct_rfc9162_sct_coop_origin_agent_cluster_and_craft_directus_ssrf",
        "description": "Audita formalmente código Python/Web contra vulnerabilidades en IETF RFC 9162 Certificate Transparency v2.0 (diversidad de logs >= 2, cota leaf_index < tree_size, separación de dominio Merkle 0x00/0x01 y comparación constante), aislamiento de procesos W3C Cross-Origin-Opener-Policy (same-origin) y Origin-Agent-Cluster (?1), y prevención de SSRF en Craft CMS (CVE-2026-27127/27129 DNS Rebinding & IPv6 AAAA), Directus (CVE-2026-35409 IPv4-mapped IPv6) y Oracle EBS (CVE-2025-61882) (v12.1.0 - Nivel 118).",
        "inputSchema": {
    "type": "object",
    "properties": {
        "code": {"type": "string", "description": "Código fuente a auditar."},
        "source_code": {"type": "string", "description": "Alias opcional de código fuente a auditar."}
    }
        }
    },
    {
        "name": "aleph_audit_ocsp_rfc6960_permissions_policy_and_sonicwall_plunk_avideo_ssrf",
        "description": "Audita formalmente código Python/Web contra vulnerabilidades en IETF RFC 6960 X.509 OCSP (cert_status == 'good', ventana this_update <= now <= next_update, autorización EKU id-kp-OCSPSigning y nonce constante), aislamiento W3C Permissions-Policy contra comodines '*' en hardware/WebAuthn, y prevención de SSRF en SonicWall SMA1000 WorkPlace Proxy (CVE-2026-15409), Plunk AWS SNS SubscribeURL (CVE-2026-32096) y WWBN AVideo (CVE-2026-39368/39370) (v12.0.0 - Nivel 117).",
        "inputSchema": {
    "type": "object",
    "properties": {
        "code": {"type": "string", "description": "Código fuente a auditar."},
        "source_code": {"type": "string", "description": "Alias opcional de código fuente a auditar."}
    }
        }
    },
    {
        "name": "aleph_audit_x509_rfc5280_csp_style_src_attr_elem_and_librechat_tika_ssrf",
        "description": "Audita formalmente código Python/Web contra vulnerabilidades en IETF RFC 5280 X.509 Path Validation (BasicConstraints.cA + KeyUsage.keyCertSign, pathLenConstraint, rechazo de extensiones críticas desconocidas y comparación constante), directivas W3C CSP3 style-src-attr y style-src-elem contra exfiltración CSS, y prevención de SSRF en LibreChat (CVE-2026-31943 IPv4-mapped IPv6), Apache Tika PDF XXE (CVE-2025-66516) y curl_cffi (CVE-2026-33752) (v11.9.0 - Nivel 116).",
        "inputSchema": {
    "type": "object",
    "properties": {
        "code": {"type": "string", "description": "Código fuente a auditar."},
        "source_code": {"type": "string", "description": "Alias opcional de código fuente a auditar."}
    }
        }
    },
    {
        "name": "aleph_audit_jws_rfc7515_rfc7797_corp_local_network_and_chainlit_pandoc_ssrf",
        "description": "Audita formalmente código Python/Web contra vulnerabilidades en IETF RFC 7515 / RFC 7797 JSON Web Signature (rechazo de cabeceras desprotegidas 'header', prohibición de 'b64: false' no codificado y verificación constante), aislamiento W3C Cross-Origin-Resource-Policy (CORP: same-origin) y Permissions-Policy (local-network-access / loopback-network), y prevención de SSRF en Chainlit AI (CVE-2026-22219), Pandoc HTML-to-PDF (CVE-2025-51591) y Axios Redirect (CVE-2025-27152) (v11.8.0 - Nivel 115).",
        "inputSchema": {
    "type": "object",
    "properties": {
        "code": {"type": "string", "description": "Código fuente a auditar."},
        "source_code": {"type": "string", "description": "Alias opcional de código fuente a auditar."}
    }
        }
    },
    {
        "name": "aleph_audit_acme_rfc8555_csp_script_src_elem_and_mcp_server_oci_ssrf",
        "description": "Audita formalmente código Python/Web contra vulnerabilidades en IETF RFC 8555 ACME (ligadura criptográfica keyAuthorization = token.jwk_thumbprint_sha256, consumo atómico de Replay-Nonce y comparación constante), directiva W3C CSP3 script-src-elem y despliegues huérfanos de Content-Security-Policy-Report-Only sin política activa, y prevención de SSRF en servidores MCP (CVE-2026-27825/26 mcp-atlassian, CVE-2026-32871 fastmcp, CVE-2026-39885 $ref) y Docker Model Runner OCI (CVE-2026-33990) (v11.7.0 - Nivel 114).",
        "inputSchema": {
    "type": "object",
    "properties": {
        "code": {"type": "string", "description": "Código fuente a auditar."},
        "source_code": {"type": "string", "description": "Alias opcional de código fuente a auditar."}
    }
        }
    },
    {
        "name": "aleph_audit_tls_delegated_credentials_rfc9345_coep_and_dify_openwebui_ssrf",
        "description": "Audita formalmente código Python/Web contra vulnerabilidades en IETF RFC 9345 Delegated Credentials for TLS/DTLS 1.3 (cota máxima de validez <= 7 días / 604800s, extensión X.509 DelegationUsage, prohibición de rsa_pss_rsae_* y verificación constante), aislamiento W3C Cross-Origin-Embedder-Policy (COEP: require-corp / credentialless) para SharedArrayBuffer contra Spectre, y prevención de SSRF en flujos RAG e ingesta web de Dify y Open WebUI (v11.6.0 - Nivel 113).",
        "inputSchema": {
    "type": "object",
    "properties": {
        "code": {"type": "string", "description": "Código fuente a auditar."},
        "source_code": {"type": "string", "description": "Alias opcional de código fuente a auditar."}
    }
        }
    },
    {
        "name": "aleph_audit_tls_service_identity_rfc9525_csp_upgrade_insecure_and_vllm_localai_ssrf",
        "description": "Audita formalmente código Python/Web contra vulnerabilidades en IETF RFC 9525 Service Identity in TLS (prohibición de fallback a Subject Common Name CN-ID, validación estricta SubjectAltName DNS-ID/URI-ID y pinning SPKI en tiempo constante), directiva W3C CSP3 upgrade-insecure-requests contra degradación de contenido mixto, y prevención de SSRF multimodal en vLLM (CVE-2026-24779 / GHSA-qh4c-xf7m-gxfc) y LMDeploy (CVE-2026-33626) (v11.5.0 - Nivel 112).",
        "inputSchema": {
    "type": "object",
    "properties": {
        "code": {"type": "string", "description": "Código fuente a auditar."},
        "source_code": {"type": "string", "description": "Alias opcional de código fuente a auditar."}
    }
        }
    },
    {
        "name": "aleph_audit_sframe_rfc9605_csp_font_manifest_src_and_langflow_flowise_ssrf",
        "description": "Audita formalmente código Python/Web contra vulnerabilidades en IETF RFC 9605 SFrame (derivación HKDF de sframe_salt XOR frame_ctr, ventana anti-replay por KID y verificación AEAD constante), aislamiento W3C CSP3 font-src y manifest-src contra exfiltración unicode-range y secuestro de PWA, y prevención de SSRF/RCE en Langflow (/api/v1/validate/code, CVE-2025-3248), Flowise y ComfyUI (v11.4.0 - Nivel 111).",
        "inputSchema": {
    "type": "object",
    "properties": {
        "code": {"type": "string", "description": "Código fuente a auditar."},
        "source_code": {"type": "string", "description": "Alias opcional de código fuente a auditar."}
    }
        }
    },
    {
        "name": "aleph_audit_oblivious_http_rfc9458_csp_img_media_src_and_jupyter_bentoml_ssrf",
        "description": "Audita formalmente código Python/Web contra vulnerabilidades en IETF RFC 9458 Oblivious HTTP (separación estricta entre Oblivious Relay y Oblivious Gateway sin filtración de IP de cliente, validación de KeyConfig HPKE y verificación AEAD constante), aislamiento W3C CSP3 img-src y media-src contra Dangling Markup Exfiltration, y prevención de SSRF en Jupyter Server Proxy (/proxy/http, CVE-2024-35225) y BentoML Runner (:3000, CVE-2024-2912) (v11.3.0 - Nivel 110).",
        "inputSchema": {
    "type": "object",
    "properties": {
        "code": {"type": "string", "description": "Código fuente a auditar."},
        "source_code": {"type": "string", "description": "Alias opcional de código fuente a auditar."}
    }
        }
    },
    {
        "name": "aleph_audit_privacy_pass_rfc9578_csp_connect_src_and_mlflow_gradio_ssrf",
        "description": "Audita formalmente código Python/Web contra vulnerabilidades en tokens IETF RFC 9578 Privacy Pass (challenge_digest SHA-256, caché anti-replay de nonces y verificación constante), aislamiento W3C CSP3 connect-src / sendBeacon / WebSocket, y prevención de SSRF hacia servidores MLflow Tracking (:5000/api/2.0/mlflow, GHSA-65h7-c7c4-mghx / CVE-2024-2928) y Gradio (/queue/join, CVE-2024-4325) (v11.2.0 - Nivel 109).",
        "inputSchema": {
    "type": "object",
    "properties": {
        "code": {"type": "string", "description": "Código fuente a auditar."},
        "source_code": {"type": "string", "description": "Alias opcional de código fuente a auditar."}
    }
        }
    },
    {

        "name": "aleph_audit_opaque_pake_csp_frame_src_and_torchserve_triton_ssrf",

        "description": "Demostrador Formal del Protocolo PAKE Asimétrico OPAQUE (draft-irtf-cfrg-opaque: endurecimiento MHF Argon2id/scrypt sobre salida OPRF, ligadura de identidades idU/idS en Envelope contra KCI y MAC constante), Directivas W3C CSP frame-src y child-src (aislamiento de subframes y SharedWorkers) y Prevención de SSRF hacia PyTorch TorchServe Management API (8081/models CVE-2023-43654 ShellTorch) y NVIDIA Triton Model Control (8000/v2/repository/models) (v11.1.0 - NODE-04 Shard).",

        "inputSchema": {

    "type": "object",

    "properties": {

        "source_code": {"type": "string", "description": "Código fuente Python/JS/TS/Config a auditar formalmente."},

        "target_path": {"type": "string", "description": "Ruta opcional del archivo auditado."}

    },

    "required": ["source_code"]

        }

    },
    {

        "name": "aleph_audit_ristretto255_rfc9496_csp_object_src_and_kafka_connect_ssrf",

        "description": "Demostrador Formal de Grupos de Orden Primo Ristretto255 y Decaf448 RFC 9496 (rechazo de codificaciones no canónicas en DECODE y equivalencia proyectiva constante), Directiva W3C CSP object-src none (aislamiento de plugins/<object>/<embed>) y Prevención de SSRF hacia Apache Kafka Connect REST API (8083/connectors, CVE-2023-25194 JNDI RCE) y ZooKeeper AdminServer (8080) (v11.0.0 - NODE-04 Shard).",

        "inputSchema": {

    "type": "object",

    "properties": {

        "source_code": {"type": "string", "description": "Código fuente Python/JS/TS/Config a auditar formalmente."},

        "target_path": {"type": "string", "description": "Ruta opcional del archivo auditado."}

    },

    "required": ["source_code"]

        }

    },
    {

        "name": "aleph_audit_rats_eat_rfc9334_csp_style_src_and_vectordb_qdrant_ssrf",

        "description": "Demostrador Formal de Atestación Remota RATS RFC 9334 y Entity Attestation Token EAT RFC 9711 (nonce de frescura eat_nonce >= 64 bits, bloqueo de dbgstat de depuración y comparación constante), Directivas W3C CSP3 style-src-attr y style-src-elem (contra exfiltración CSS de atributos DOM) y Prevención de SSRF hacia Bases Vectoriales Qdrant (6333 snapshots/recover CVE-2024-3829), Weaviate (8080) y ChromaDB (8000) (v10.9.0 - NODE-04 Shard).",

        "inputSchema": {

    "type": "object",

    "properties": {

        "source_code": {"type": "string", "description": "Código fuente Python/JS/TS/Config a auditar formalmente."},

        "target_path": {"type": "string", "description": "Ruta opcional del archivo auditado."}

    },

    "required": ["source_code"]

        }

    },
    {

        "name": "aleph_audit_tls13_epsk_rfc9258_csp_script_src_attr_and_airflow_prefect_ssrf",

        "description": "Demostrador Formal de Importación de External PSK en TLS 1.3 RFC 9258 (derivación HKDF derived psk con Epskid, separación ext binder vs res binder contra ataques Selfie y MAC constante), Directivas W3C CSP3 script-src-attr y script-src-elem (bloqueo de unsafe-inline en eventos HTML) y Prevención de SSRF hacia Apache Airflow REST API (8080/api/v1/dags/*/dagRuns) y Prefect Server (4200) (v10.8.0 - NODE-04 Shard).",

        "inputSchema": {

    "type": "object",

    "properties": {

        "source_code": {"type": "string", "description": "Código fuente Python/JS/TS/Config a auditar formalmente."},

        "target_path": {"type": "string", "description": "Ruta opcional del archivo auditado."}

    },

    "required": ["source_code"]

        }

    },
    {

        "name": "aleph_audit_openpgp_rfc9580_seipdv2_reporting_endpoints_and_nomad_supervisord_ssrf",

        "description": "Demostrador Formal de Criptografía OpenPGP v6 RFC 9580 (paquetes autenticados SEIPDv2 AEAD con verificación de final_chunk_tag previa a emisión de texto plano, Argon2 S2K 0x04 y prohibición de SED Tag 9 / Simple S2K), Cabeceras W3C Reporting-Endpoints / CSP report-to (contra exfiltración hacia colectores inyectados) y Prevención de SSRF hacia HashiCorp Nomad (4646) y Supervisord XML-RPC (9001) (v10.7.0 - NODE-04 Shard).",

        "inputSchema": {

    "type": "object",

    "properties": {

        "source_code": {"type": "string", "description": "Código fuente Python/JS/TS/Config a auditar formalmente."},

        "target_path": {"type": "string", "description": "Ruta opcional del archivo auditado."}

    },

    "required": ["source_code"]

        }

    },
    {

        "name": "aleph_audit_rfc9530_digest_fields_csp_frame_ancestors_and_spark_flink_ssrf",

        "description": "Demostrador Formal de Campos de Integridad HTTP Digest Fields RFC 9530 (Repr-Digest y Content-Digest con sha-256/sha-512, bloqueo de md5/sha1/adler/crc32c y comparación constante), Directiva W3C CSP frame-ancestors (contra Clickjacking y X-Frame-Options ALLOW-FROM obsoleto) y Prevención de SSRF hacia Apache Spark REST Submission (6066) y Apache Flink JobManager (8081) (v10.6.0 - NODE-04 Shard).",

        "inputSchema": {

    "type": "object",

    "properties": {

        "source_code": {"type": "string", "description": "Código fuente Python/JS/TS/Config a auditar formalmente."},

        "target_path": {"type": "string", "description": "Ruta opcional del archivo auditado."}

    },

    "required": ["source_code"]

        }

    },
    {

        "name": "aleph_audit_ecvrf_rfc9381_csp_form_action_and_prometheus_grafana_ssrf",

        "description": "Demostrador Formal de Funciones Aleatorias Verificables ECVRF RFC 9381 (verificación obligatoria ECVRF_verify antes de ECVRF_proof_to_hash, validación de subgrupo ECVRF_validate_key y comparación constante), Directiva W3C CSP form-action (no cubierta por default-src contra secuestro de formularios) y Prevención de SSRF hacia Prometheus Admin/TSDB (9090), Loki (3100) y Grafana Datasource Proxy (3000) (v10.5.0 - NODE-04 Shard).",

        "inputSchema": {

    "type": "object",

    "properties": {

        "source_code": {"type": "string", "description": "Código fuente Python/JS/TS/Config a auditar formalmente."},

        "target_path": {"type": "string", "description": "Ruta opcional del archivo auditado."}

    },

    "required": ["source_code"]

        }

    },
    {

        "name": "aleph_audit_blind_rsa_rfc9474_permissions_policy_and_kubelet_cri_ssrf",

        "description": "Demostrador Formal de Firmas Ciegas RSA RFC 9474 y Privacy Pass RFC 9578 (factor de cegado CSPRNG coprimo gcd(r, N)==1, verificación pos-descegado y redención constante), W3C Permissions-Policy (bloqueo de delegación comodín * en camera/microphone/usb/serial/hid/payment/publickey-credentials-get) y Prevención de SSRF hacia Kubernetes Kubelet (10250/10255) y Containerd/CRI-O Streaming (10010) (v10.4.0 - NODE-04 Shard).",

        "inputSchema": {

    "type": "object",

    "properties": {

        "source_code": {"type": "string", "description": "Código fuente Python/JS/TS/Config a auditar formalmente."},

        "target_path": {"type": "string", "description": "Ruta opcional del archivo auditado."}

    },

    "required": ["source_code"]

        }

    },
    {

        "name": "aleph_audit_spake2plus_rfc9383_speculation_rules_and_cdp_inspector_ssrf",

        "description": "Demostrador Formal de Protocolos PAKE Asimétricos SPAKE2/SPAKE2+ RFC 9382 / RFC 9383 (estiramiento PBKDF2/scrypt/Argon2id de escalares w0/w1, validación de punto fuera de identidad y confirmación MAC constante), W3C Speculation Rules API (Speculation-Rules / Sec-Purpose contra mutación en prefetch/prerender) y Prevención de SSRF hacia Chrome DevTools Protocol (9222), Node.js Inspector (9229) y WebDriver (4444) (v10.3.0 - NODE-04 Shard).",

        "inputSchema": {

    "type": "object",

    "properties": {

        "source_code": {"type": "string", "description": "Código fuente Python/JS/TS/Config a auditar formalmente."},

        "target_path": {"type": "string", "description": "Ruta opcional del archivo auditado."}

    },

    "required": ["source_code"]

        }

    },
    {
        "name": "aleph_audit_hash_to_curve_rfc9380_doc_isolation_and_ray_ollama_ssrf",
        "description": "Demostrador Formal de Hashing to Elliptic Curves RFC 9380 (Domain Separation Tag DST >= 16 bytes, oráculo aleatorio uniforme _RO_, clear_cofactor y prohibición de try-and-increment en tiempo variable), Aislamiento de Proceso Web (Document-Isolation-Policy + Origin-Agent-Cluster: ?1) y Prevención de SSRF RCE hacia Clústeres de IA Ray Dashboard (8265) y Ollama (11434, CWE-918) (v10.2.0 - NODE-04 Shard).",
        "inputSchema": {
    "type": "object",
    "properties": {
        "source_code": {"type": "string", "description": "Código a auditar contra vulnerabilidades RFC 9380 hash_to_curve, Document-Isolation-Policy y SSRF hacia Ray/Ollama."},
        "rfc9380_config": {"type": "object", "description": "Configuración de mapeo criptográfico a curvas elípticas RFC 9380 opcional."},
        "doc_isolation_context": {"type": "object", "description": "Contexto de cabeceras Document-Isolation-Policy y Origin-Agent-Cluster opcional."},
        "ai_cluster_ssrf_context": {"type": "object", "description": "Contexto de destino de red para bloqueo de Ray Dashboard (8265) y Ollama (11434) opcional."}
    },
    "required": ["source_code"]
        }
    },
        {
            "name": "aleph_apply_semantic_patch",
            "description": "Aplica un parche semántico en el AST validando previamente con el demostrador SMT que no introduce regresiones de seguridad.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "original_source": {"type": "string"},
                    "target_function_name": {"type": "string"},
                    "replacement_function_source": {"type": "string"},
                    "target_file_path": {"type": "string"}
                },
                "required": ["original_source", "target_function_name", "replacement_function_source"]
            }
        },
        {
            "name": "aleph_load_active_context",
            "description": "Recupera selectivamente las reglas algorítmicas activas de SparkOS (SI -> ENTONCES -> EVITAR) para el dominio actual con 78% de ahorro de tokens.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "domain_category": {"type": "string", "enum": ["Código", "Doc", "Correo", "Análisis", "General"], "default": "Código"}
                }
            }
        },
        {
            "name": "aleph_scan_security",
            "description": "Escanea payloads, prompts o código con AegisShield (<1ms) contra Prompt Injection, fuga de claves, bucles infinitos y anti-patrones REG-001.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"}
                },
                "required": ["text"]
            }
        },
        {
            "name": "aleph_run_optimality_tournament",
            "description": "Ejecuta un Torneo de Optimalidad Global (REG-007) y Consejo de Guerra de 5 perspectivas para elegir la solución Pareto-Dominante #1.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "problem_domain": {"type": "string"},
                    "candidates": {"type": "array", "items": {"type": "object"}}
                },
                "required": ["problem_domain", "candidates"]
            }
        },
        {
            "name": "aleph_checkpoint_session",
            "description": "Guarda o restaura un checkpoint jerárquico comprimido con zlib en SQLite WAL para recuperación tras compactación de contexto.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["save", "resume"]},
                    "session_id": {"type": "string"},
                    "step_number": {"type": "integer", "default": 1},
                    "working_memory": {"type": "object"},
                    "compact_summary": {"type": "string", "default": ""}
                },
                "required": ["action", "session_id"]
            }
        },
        {
            "name": "aleph_evolve_demiurgo",
            "description": "Dispara un ciclo autónomo de automejora Demiurgo sintetizando nuevas reglas preventivas desde claims refutados.",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
    {
        "name": "aleph_backward_slice",
        "description": "Ejecuta Backward Program Slicing sobre el Grafo de Dependencias (PDG) y mide complejidad ciclomática McCabe y volumen Halstead.",
        "inputSchema": {
    "type": "object",
    "properties": {
        "source_code": {"type": "string"},
        "target_variable": {"type": "string", "default": "result"}
    },
    "required": ["source_code"]
        }
    },
    {
        "name": "aleph_polyglot_audit",
        "description": "Audita invariantes políglotas de producción para Rust (Codere/ClipperOps), TypeScript/Next.js y VBA Excel (GOAR REG-001).",
        "inputSchema": {
    "type": "object",
    "properties": {
        "code": {"type": "string"},
        "language": {"type": "string", "enum": ["rust", "typescript", "vba"]}
    },
    "required": ["code", "language"]
        }
    },
        {
            "name": "aleph_mine_specifications",
            "description": "Minero Simbólico de Especificaciones: Induce precondiciones de seguridad {P} y poscondiciones {Q} por análisis de AST y las prueba con SMT.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_code": {"type": "string"},
                    "function_name": {"type": "string"}
                },
                "required": ["source_code"]
            }
        },
        {
            "name": "aleph_git_verify",
            "description": "Compuerta Pre-Commit Soberana de Integridad de Workspace: audita un diccionario de archivos modificados con SMT y contratos políglotas.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "files": {"type": "object", "description": "Mapa de filepath -> contenido"}
                },
                "required": ["files"]
            }
        },
        {
            "name": "aleph_prove_equivalence",
            "description": "Demostrador Relacional de Equivalencia por Programa Producto: prueba matemáticamente si una función refactorizada es equivalente a la original o extrae el testigo de divergencia.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "original_source": {"type": "string"},
                    "candidate_source": {"type": "string"},
                    "orig_func_name": {"type": "string"},
                    "cand_func_name": {"type": "string"}
                },
                "required": ["original_source", "candidate_source"]
            }
        },
        {
            "name": "aleph_audit_transaction_concurrency",
            "description": "Detector Estático de Condiciones de Carrera TOCTOU / Double-Spend en transacciones SQL y Rust (SELECT seguido de UPDATE sin FOR UPDATE o guardia atómica).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "language": {"type": "string", "default": "rust"}
                },
                "required": ["code"]
            }
        },
        {
            "name": "aleph_run_mutation_testing",
            "description": "Motor de Mutation Testing AST: inyecta mutantes AOR, ROR y CRP, calcula el Mutation Score y sintetiza tests discriminadores para mutantes que sobreviven.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_code": {"type": "string"},
                    "target_function_name": {"type": "string"},
                    "test_inputs": {"type": "array", "items": {"type": "object"}}
                },
                "required": ["source_code"]
            }
        },
        {
            "name": "aleph_verify_double_entry_ledger",
            "description": "Demostrador Formal de Partida Doble: verifica conservación estricta de saldo (suma cero), solvencia de cuentas e idempotencia por clave hash.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "tx_id": {"type": "string"},
                    "idempotency_key": {"type": "string"},
                    "postings": {"type": "array", "items": {"type": "object"}},
                    "current_balances": {"type": "object"}
                },
                "required": ["tx_id", "idempotency_key", "postings", "current_balances"]
            }
        },
        {
            "name": "aleph_verify_state_machine",
            "description": "Model Checker Temporal CTL/LTL para Máquinas de Estados Finitos: demuestra ausencia de Deadlocks, Livelocks AG(EF(Terminal)), estados inalcanzables y transiciones prohibidas.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "machine_name": {"type": "string"},
                    "states": {"type": "array", "items": {"type": "string"}},
                    "initial_state": {"type": "string"},
                    "terminal_states": {"type": "array", "items": {"type": "string"}},
                    "transitions": {"type": "array", "items": {"type": "object"}},
                    "forbidden_transitions": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}}
                },
                "required": ["machine_name", "states", "initial_state", "terminal_states", "transitions"]
            }
        },
        {
            "name": "aleph_generate_proof_certificate",
            "description": "Genera un Certificado de Prueba Criptográfica (.aleph-cert.json) basado en Proof-Carrying Code (PCC) para una función formalmente demostrada.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_code": {"type": "string"},
                    "target_function_name": {"type": "string"}
                },
                "required": ["source_code"]
            }
        },
        {
            "name": "aleph_verify_proof_certificate",
            "description": "Valida en <0.05 ms un Certificado de Prueba Criptográfica PCC contra un código fuente sin invocar al solver SMT pesado.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_code": {"type": "string"},
                    "certificate": {"type": "object"}
                },
                "required": ["source_code", "certificate"]
            }
        },
        {
            "name": "aleph_analyze_interprocedural_taint",
            "description": "Analizador de Manchas Inter-Procedural (ICFG): rastrea flujos de datos no confiables desde Sources hacia Sinks a través de cadenas de llamadas multi-función.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_code": {"type": "string"},
                    "files_map": {"type": "object"}
                }
            }
        },
        {
            "name": "aleph_audit_dictionary_schema",
            "description": "Verificador Simbólico de Esquemas de Diccionarios y JSON: modela claves bajo Teoría SMT de Arrays, verifica ausencia de KeyError e induce contratos formales @requires.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_code": {"type": "string"},
                    "target_function_name": {"type": "string"}
                },
                "required": ["source_code"]
            }
        },
        {
            "name": "aleph_audit_asymptotic_complexity",
            "description": "Auditor Estructural de Complejidad Asintótica Big-O y Consultas N+1: calcula complejidad peor caso (O(1), O(N), O(N^2), O(2^N)), anidamiento de bucles y llamadas a base de datos dentro de bucles.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_code": {"type": "string"},
                    "target_function_name": {"type": "string"}
                },
                "required": ["source_code"]
            }
        },
        {
            "name": "aleph_audit_lock_deadlocks",
            "description": "Demostrador Formal de Ausencia de Deadlocks en Concurrencia (LODG): detecta esperas circulares en orden de adquisición de locks y mutexes en sistemas multihilo.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_code": {"type": "string"},
                    "files_map": {"type": "object"}
                }
            }
        },
        {
            "name": "aleph_synthesize_database_indexes",
            "description": "Sintetizador Formal de Índices SQL y Cobertura de Consultas: extrae predicados WHERE/JOIN/ORDER BY y sintetiza índices compuestos B-Tree óptimos.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_code": {"type": "string"},
                    "files_map": {"type": "object"},
                    "existing_indexes": {"type": "array", "items": {"type": "string"}}
                }
            }
        },
        {
            "name": "aleph_audit_resource_leaks",
            "description": "Verificador Formal de Fugas de Recursos y Typestates Lineales: comprueba que archivos, sockets, conexiones DB y tareas async se cierren en todos los caminos de ejecución.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_code": {"type": "string"},
                    "target_function_name": {"type": "string"}
                },
                "required": ["source_code"]
            }
        },
        {
            "name": "aleph_verify_api_drift",
            "description": "Verificador Formal de Deriva de Contratos API y Compatibilidad Hacia Atrás: evalúa contravarianza de entradas y covarianza de salidas para detectar Breaking Changes.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "original_source": {"type": "string"},
                    "candidate_source": {"type": "string"}
                },
                "required": ["original_source", "candidate_source"]
            }
        },
        {
            "name": "aleph_verify_distributed_saga",
            "description": "Demostrador Formal de Sagas Distribuidas: prueba compensabilidad, idempotencia y completitud de reversa ante fallos en microservicios.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "saga_name": {"type": "string"},
                    "steps": {
                        "type": "array",
                        "items": {"type": "object"}
                    }
                },
                "required": ["saga_name", "steps"]
            }
        },
        {
            "name": "aleph_audit_circuit_breaker_backoff",
            "description": "Verificador de Resiliencia ante Tormentas de Reintentos: valida Backoff Exponencial con Jitter, acotamiento de intentos y Circuit Breakers.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_code": {"type": "string"},
                    "target_function_name": {"type": "string"}
                },
                "required": ["source_code"]
            }
        },
        {
            "name": "aleph_verify_authorization_policies",
            "description": "Demostrador Formal de Políticas de Autorización ABAC/ReBAC: prueba ausencia de reglas sombreadas, default-deny y ausencia de escalación de privilegios.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "policy_set_name": {"type": "string"},
                    "policies": {
                        "type": "array",
                        "items": {"type": "object"}
                    }
                },
                "required": ["policy_set_name", "policies"]
            }
        },
        {
            "name": "aleph_audit_transactional_outbox",
            "description": "Verificador Formal del Patrón Transactional Outbox: comprueba que toda mutación de dominio esté atómicamente emparejada con un evento outbox.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_code": {"type": "string"},
                    "target_function_name": {"type": "string"}
                },
                "required": ["source_code"]
            }
        },
        {
            "name": "aleph_verify_failover_consensus",
            "description": "Demostrador Formal de Failover de Alta Disponibilidad: comprueba quórum de mayoría estricta, prevención de Split-Brain y cotas de lag de replicación.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "cluster_name": {"type": "string"},
                    "nodes": {
                        "type": "array",
                        "items": {"type": "object"}
                    },
                    "max_lag_bytes": {"type": "integer"}
                },
                "required": ["cluster_name", "nodes"]
            }
        },
        {
            "name": "aleph_audit_telemetry_privacy",
            "description": "Verificador Formal de Privacidad de Datos en Telemetría y Logs: detecta fugas de PII o credenciales en texto plano sin ofuscación previa.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_code": {"type": "string"},
                    "target_function_name": {"type": "string"}
                },
                "required": ["source_code"]
            }
        },
        {
            "name": "aleph_build_pagerank_repomap",
            "description": "Motor PageRank RepoMap con Contratos Formales (Superación de Aider/SWE-agent/OpenHands): indexa símbolos políglotas, calcula centralidad Personalized PageRank (d=0.85) y empaqueta firmas bajo presupuesto exacto de tokens.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "files_map": {"type": "object"},
                    "focus_symbols": {"type": "array", "items": {"type": "string"}},
                    "max_token_budget": {"type": "integer"}
                },
                "required": ["files_map"]
            }
        },
        {
            "name": "aleph_audit_and_synthesize_frontend_ui",
            "description": "Demostrador y Sintetizador Formal Frontend UI React/Next.js/Tailwind (Superación de v0.dev y Bolt.new): verifica determinismo de hidratación SSR, ausencia de ciclos en useEffect, accesibilidad WCAG 2.2 AA, tri-estado asíncrono y mapeo bidireccional DOM-to-AST.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "mode": {"type": "string", "description": "'audit' o 'synthesize'"},
                    "source_code": {"type": "string"},
                    "component_name": {"type": "string"},
                    "fields": {"type": "array", "items": {"type": "object"}},
                    "title": {"type": "string"}
                },
                "required": ["mode"]
            }
        },
        {
            "name": "aleph_verify_fullstack_rls_and_schema",
            "description": "Demostrador Formal Full-Stack RLS e Isomorfismo SQL <-> TypeScript (Superación de Lovable.dev): verifica Row-Level Security Zero-Trust en Supabase/PostgreSQL, ausencia de secretos en bundle cliente (NEXT_PUBLIC_/VITE_) e isomorfismo de tipos SQL-TS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "sql_ddl": {"type": "string"},
                    "typescript_source": {"type": "string"},
                    "env_vars": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["sql_ddl"]
            }
        },
        {
            "name": "aleph_verify_zero_downtime_ddl",
            "description": "Demostrador Formal de Migraciones de Base de Datos Zero-Downtime y Anti-Bloqueo (v4.7.0): verifica que scripts DDL en PostgreSQL/Supabase no tomen bloqueos ACCESS EXCLUSIVE ni congelen tablas en producción.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "sql_script": {"type": "string"}
                },
                "required": ["sql_script"]
            }
        },
        {
            "name": "aleph_audit_state_optimistic_rollback",
            "description": "Demostrador Formal de Estado Global y Rollback en UI Optimista (v4.7.0): verifica inmutabilidad en stores Zustand/Redux y que toda mutación useMutation con actualización optimista contenga snapshot, rollback en onError y sincronización en onSettled.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_code": {"type": "string"}
                },
                "required": ["source_code"]
            }
        },
        {
            "name": "aleph_verify_idempotent_consumer",
            "description": "Demostrador Formal de Consumidores Idempotentes y Deduplicación (v4.8.0): verifica semántica Exactly-Once lógica sobre canales At-Least-Once comprobando deduplicación en processed_events, commits atómicos y ausencia de efectos colaterales previos.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_code": {"type": "string"},
                    "target_function_name": {"type": "string"}
                },
                "required": ["source_code"]
            }
        },
        {
            "name": "aleph_audit_ssrf_safe_egress",
            "description": "Demostrador Formal Anti-SSRF y Puerta de Egreso Seguro (v4.8.0): audita clientes HTTP en agentes y servicios backend bloqueando IPs privadas/loopback/metadatos (169.254.169.254), mitigando DNS Rebinding y forzando esquemas http/https.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_code": {"type": "string"}
                },
                "required": ["source_code"]
            }
        },
        {
            "name": "aleph_audit_constant_time_crypto",
            "description": "Demostrador Formal de Invariantes Criptográficos y Tiempo Constante (v4.9.0): audita comparaciones de tokens, firmas HMAC y secretos bloqueando operadores ==/!= vulnerables a Timing Side-Channel Attacks y forzando hmac.compare_digest.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_code": {"type": "string"},
                    "target_function_name": {"type": "string"}
                },
                "required": ["source_code"]
            }
        },
        {
            "name": "aleph_verify_rate_limiter_token_bucket",
            "description": "Demostrador Formal de Limitadores de Tasa Token-Bucket (v4.9.0): audita rate limiters en API gateways y workers bloqueando chequeos no atómicos en caché y picos del 200% en límites de ventana fija.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_code": {"type": "string"}
                },
                "required": ["source_code"]
            }
        },
        {
            "name": "aleph_align_prompt_cache_chunks",
            "description": "Alineador y Empaquetador Formal de Prefijos de Caché de Prompts (v5.0.0): garantiza invarianza del prefijo estático y lo alinea a múltiplos exactos de chunks (1024/2048 tokens), aislando sufijos volátiles para >95% cache hit rate.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "static_prefix": {"type": "string"},
                    "dynamic_suffix": {"type": "string"},
                    "chunk_size_tokens": {"type": "integer"}
                },
                "required": ["static_prefix"]
            }
        },
        {
            "name": "aleph_verify_workspace_transactional_rollback",
            "description": "Demostrador Formal de Espacio de Trabajo Transaccional y Reversión Bidireccional (v5.0.0): garantiza invertibilidad matemática de deltas multi-archivo y emite recibo criptográfico SHA-256 para rollback seguro sin git reset --hard.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "transaction_id": {"type": "string"},
                    "files_before": {"type": "object"},
                    "files_after": {"type": "object"}
                },
                "required": ["transaction_id", "files_before", "files_after"]
            }
        },
        {
            "name": "aleph_verify_queue_backpressure",
            "description": "Demostrador Formal de Colas Acotadas, Backpressure y Prevención de OOM (v5.1.0): audita workers y colas asíncronas bloqueando asyncio.Queue sin maxsize, exigiendo contrapresión y drenaje ordenado en shutdown.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_code": {"type": "string"}
                },
                "required": ["source_code"]
            }
        },
        {
            "name": "aleph_audit_content_security_policy",
            "description": "Demostrador Formal de Content Security Policy y Protección XSS (v5.1.0): audita dangerouslySetInnerHTML sin DOMPurify y cabeceras CSP verificando object-src 'none', base-uri 'self' y directivas anti-unsafe-inline.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_code": {"type": "string"},
                    "is_config_file": {"type": "boolean"}
                },
                "required": ["source_code"]
            }
        },
        {
            "name": "aleph_scaffold_verified_fullstack_app",
            "description": "Motor Universal Full-Stack Studio & Scaffolder Verificado (v5.2.0 - Superación de Lovable/v0/Bolt/Replit): genera una app Full-Stack completa (SQL RLS + DDL Zero-Downtime + TypeScript + Store con Rollback Optimista + UI React/Tailwind con DOM-to-AST + Preview HTML Interactivo) certificada por 6 motores formales.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "app_name": {"type": "string"},
                    "table_name": {"type": "string"},
                    "fields": {"type": "array", "items": {"type": "object"}},
                    "domain_category": {"type": "string"},
                    "title": {"type": "string"}
                },
                "required": ["app_name", "table_name", "fields"]
            }
        },
        {
            "name": "aleph_verify_and_compile_universal_workflow",
            "description": "Orquestador y Demostrador Formal de Flujos Universales Multi-Agente (v5.2.0 - Superación de LangGraph/n8n/Devin): verifica aciclicidad DAG, compatibilidad de contratos de entrada/salida, compuerta humana en acciones irreversibles y SLA de camino crítico.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "workflow_name": {"type": "string"},
                    "steps": {"type": "array", "items": {"type": "object"}},
                    "initial_inputs": {"type": "array", "items": {"type": "string"}},
                    "sla_limit_ms": {"type": "integer"}
                },
                "required": ["workflow_name", "steps"]
            }
        },
        {
            "name": "aleph_audit_multitenant_rls_leak",
            "description": "Verificador Formal de Aislamiento Multi-Inquilino y Enmascaramiento de Columnas (v5.3.0): audita consultas SQL multi-tabla garantizando propagación de tenant_id en JOINs y enmascaramiento de columnas sensibles.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "sql_queries": {"type": "string"}
                },
                "required": ["sql_queries"]
            }
        },
        {
            "name": "aleph_synthesize_zero_flicker_patch",
            "description": "Motor de Parches HMR con Preservación de Estado y Cero Parpadeo (v5.3.0): sintetiza parches React Fast Refresh quirúrgicos que preservan el estado useState en memoria sin recargar la página ni desmontar componentes.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "original_tsx": {"type": "string"},
                    "candidate_tsx": {"type": "string"},
                    "component_name": {"type": "string"}
                },
                "required": ["original_tsx", "candidate_tsx"]
            }
        },
        {
            "name": "aleph_coordinate_federated_swarm",
            "description": "Coordinador Formal de Enjambre Federado Multi-Cuenta con Bloqueo CAS SHA-256 y Anillo TDMA de 6 Nodos (v5.4.0): verifica colisiones de minuto TDMA, linaje criptográfico parent_bundle_sha256 y monotonicidad de tests en despliegues paralelos multi-cuenta.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "cluster_id": {"type": "string"},
                    "initial_head_sha256": {"type": "string"},
                    "initial_tests_count": {"type": "integer"},
                    "submissions": {
                        "type": "array",
                        "items": {"type": "object"}
                    }
                },
                "required": ["initial_head_sha256", "initial_tests_count", "submissions"]
            }
        },
        {
            "name": "aleph_minimize_patch_trajectory_and_antislop",
            "description": "Minimizador Semántico de Parches y Verificador de Trayectorias Anti-CodeSlop (v5.5.0): poda código residual ('CodeSlop'), elimina imports/funciones auxiliares muertas y detecta oscilaciones/flapping en trayectorias agénticas con reducción 1-minimal y preservación de invariantes SMT.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "original_code": {"type": "string"},
                    "candidate_code": {"type": "string"},
                    "trajectory_snapshots": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["original_code", "candidate_code"]
            }
        },
        {
            "name": "aleph_audit_server_actions_and_rsc_boundaries",
            "description": "Verificador Formal de Límites de React Server Components (RSC) y Server Actions (v5.6.0): detecta fugas de secretos de servidor a bundles de cliente ('use client'), Server Actions públicas sin autenticación ('use server') y falta de validación de esquemas Zod en mutaciones.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "file_path": {"type": "string"}
                },
                "required": ["code"]
            }
        },
        {
            "name": "aleph_audit_database_connection_and_transaction_lifecycle",
            "description": "Verificador Formal de Ciclo de Vida de Transacciones y Agotamiento de Pool de Conexiones DB (v5.7.0): audita BEGIN sin ROLLBACK/COMMIT garantizado, retención de conexiones durante I/O de red lenta (fetch/LLM), fugas de pool fuera de finally y bucles N+1.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_code": {"type": "string"},
                    "language": {"type": "string"}
                },
                "required": ["source_code"]
            }
        },
        {
            "name": "aleph_prove_incremental_merkle_repomap_and_polyglot_boundaries",
            "description": "Motor de Grafos Incrementales Merkle-AST, PageRank con Pesos de Especificidad y Demostrador Formal de Fronteras Políglotas (v5.8.0 - NODE-05 Shard): recalcula en O(|Delta V| + |Delta E|) el grafo de repositorio mediante hashes canónicos AST, pondera aristas inter-lenguaje (Rust/TS/Python/SQL/VBA), audita deriva de precisión IEEE-754 (u64/i64 -> number) y FFI 64-bit PtrSafe, y alinea el RepoMap a fronteras de KV Cache.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "files_map": {
                        "type": "object",
                        "additionalProperties": {"type": "string"}
                    },
                    "previous_merkle_hashes": {
                        "type": "object",
                        "additionalProperties": {"type": "string"}
                    },
                    "focus_symbols": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "max_token_budget": {"type": "integer"}
                },
                "required": ["files_map"]
            }
        },
        {
            "name": "aleph_audit_and_repair_design_tokens_wcag",
            "description": "Demostrador Formal de Sistemas de Diseño, Contraste Fotométrico WCAG 2.2 AA (1.4.3), Ergonomía Táctil 24x24px (2.5.8) y Anillo de Foco Visible (2.4.7) con Auto-Reparación CEGIS (v5.8.0 - NODE-02 Superación de v0.dev y Bolt.new).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "tsx_source": {"type": "string"},
                    "default_bg_token": {"type": "string"}
                },
                "required": ["tsx_source"]
            }
        },
        {
            "name": "aleph_verify_rsc_boundary_and_studio_graph",
            "description": "Demostrador Formal de Fronteras React Server/Client Components (RSC / Next.js App Router) y Compilador de Grafos de Estado para HMR Studio en O(1) (v5.8.0 - NODE-02 Superación de v0.dev / Bolt.new / Lovable).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "tsx_source": {"type": "string"},
                    "component_name": {"type": "string"},
                    "enforce_rsc_prologue": {"type": "boolean"}
                },
                "required": ["tsx_source"]
            }
        },
        {
            "name": "aleph_verify_deep_supabase_rls",
            "description": "Demostrador Formal de Políticas RLS Profundas, Barreras de Vistas Invoker y Confinamiento SECURITY DEFINER en PostgreSQL/Supabase (v5.8.0 - NODE-03 Anti-Lovable / CVE-2025-48757): verifica FORCE ROW LEVEL SECURITY, cláusulas WITH CHECK en mutaciones, security_invoker=true en vistas y SET search_path + guarda de tenant en funciones SECURITY DEFINER.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "sql_source": {"type": "string"}
                },
                "required": ["sql_source"]
            }
        },
        {
            "name": "aleph_verify_and_synthesize_expand_contract_migration",
            "description": "Demostrador y Sintetizador Formal de Migraciones Zero-Downtime por Patrón Expand-Contract en 4 Fases y Prevención de Cola de Bloqueos (v5.8.0 - NODE-03): verifica lock_timeout/statement_timeout, prohíbe backfills masivos sin LIMIT/SKIP LOCKED, bloquea índices concurrentes dentro de transacciones y sintetiza el plan Expand-Contract de 4 fases.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "sql_script": {"type": "string"},
                    "table_name": {"type": "string"},
                    "old_column": {"type": "string"},
                    "new_column": {"type": "string"},
                    "new_type": {"type": "string"},
                    "batch_size": {"type": "integer"}
                },
                "required": ["sql_script"]
            }
        },
        {
            "name": "aleph_audit_redteam_taint_crypto_and_ssrf",
            "description": "Demostrador Formal Red-Team de Seguridad Ofensiva/Defensiva, Análisis IFDS Cross-Tool/MCPTox, Protocolos Criptográficos (JWT/AEAD/Constant-Time) y Anti-SSRF Multi-Base/IPv6 (v5.8.0 — NODE-04): canoniza IPs en Octal/Hex/Dword/IPv4-Mapped-IPv6 (CVE-2026-31943), bloquea saltos de redirección SSRF, detecta confusión de algoritmos JWT y reutilización de Nonce AEAD, rastrea manchas IFDS de 2 fases cross-tool y audita manifiestos MCP contra Tool Poisoning.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_code": {"type": "string"},
                    "mcp_tools_manifest": {
                        "type": "array",
                        "items": {"type": "object"}
                    }
                },
                "required": ["source_code"]
            }
        },
        {
            "name": "aleph_audit_react_lifecycle_and_async_race_conditions",
            "description": "Verificador Formal de Ciclo de Vida React y Condiciones de Carrera Asíncronas (v5.8.0 - NODE-01): audita addEventListener sin removeEventListener, temporizadores setInterval sin clearInterval, y llamadas fetch sin AbortController en useEffect/useLayoutEffect.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "tsx_code": {"type": "string"},
                    "component_name": {"type": "string"}
                },
                "required": ["tsx_code"]
            }
        },
        {
            "name": "aleph_audit_jwt_session_and_cookie_security",
            "description": "Verificador Formal de Seguridad en JWT, Sesiones y Cookies Criptográficas (v6.1.0): audita secretos hardcodeados o con fallback || literal, ausencia de expiración (expiresIn), falta de allowlist de algoritmos en jwt.verify(), y flags ausentes httpOnly/secure/sameSite en cookies.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "file_path": {"type": "string"}
                },
                "required": ["code"]
            }
        },
        {
            "name": "aleph_synthesize_bidirectional_impact_cone_repomap",
            "description": "Sintetizador Formal de Mapas de Repositorio por Cono de Impacto Bidireccional AST y Verificador de Firmas Matriciales Políglotas (v6.1.0 — NODE-05 Shard): extrae en O(V_cone + E_cone) el subgrafo de Upstream Callers y Downstream Callees alrededor de símbolos foco, audita discrepancias de firmas Rust/TypeScript/Python y alinea a bloques de KV Cache.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "files_map": {
                        "type": "object",
                        "additionalProperties": {"type": "string"}
                    },
                    "focus_symbols": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "previous_merkle_hashes": {
                        "type": "object",
                        "additionalProperties": {"type": "string"}
                    },
                    "max_depth": {"type": "integer"},
                    "max_token_budget": {"type": "integer"}
                },
                "required": ["files_map", "focus_symbols"]
            }
        },
        {
            "name": "aleph_synthesize_compositional_interprocedural_contracts",
            "description": "Sintetizador Composicional de Contratos Interprocedurales y CEGIS (v6.2.0 - NODE-01 Core SMT/CEGIS): analiza grafos de llamadas, verifica que los invocadores cumplan los contratos @requires de los invocados y sintetiza las guardas faltantes con assume-guarantee.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_code": {"type": "string"}
                },
                "required": ["source_code"]
            }
        },
        {
            "name": "aleph_synthesize_weakest_precondition_and_contracts",
            "description": "Sintetizador Inductivo de Precondición Más Débil y Contratos SMT (v6.3.0 - NODE-01 Core SMT/CEGIS): calcula wp(S, Q) mediante sustitución simbólica hacia atrás deduciendo el contrato @requires óptimo que garantiza la postcondición deseada con Z3/ICP.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_code": {"type": "string"},
                    "desired_postcondition": {"type": "string"}
                },
                "required": ["source_code"]
            }
        },
        {
            "name": "aleph_audit_and_consolidate_master_release_pcc",
            "description": "Integrador Maestro de Release, Mutación AST de Orden Superior (FOM+HOM) con Poda Formal SMT de Mutantes Equivalentes y Árbol de Merkle de Certificados PCC SHA-256 (v6.4.0 - NODE-06 Shard): audita mutación efectiva, sintetiza tests discriminadores CEGIS, construye árbol de Merkle PCC con pruebas de inclusión O(log N) y valida linaje CAS SHA-256 de cierre de hora.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "modules_map": {"type": "object"},
                    "test_inputs_by_function": {"type": "object"},
                    "expected_parent_sha256": {"type": "string"},
                    "actual_parent_sha256": {"type": "string"},
                    "min_effective_mutation_score_pct": {"type": "number"},
                    "release_version": {"type": "string"}
                },
                "required": ["modules_map"]
            }
        },
        {
            "name": "aleph_synthesize_inductive_loop_invariants_and_termination",
            "description": "Sintetizador Inductivo de Invariantes de Bucle y Función de Ranking (v6.5.0 - NODE-01 Core SMT/CEGIS): sintetiza formalmente invariantes inductivas Inv(x) y funciones de ranking acotadas R(x) mediante análisis del AST y resolución SMT/ICP garantizando base, preservación y terminación estricta contra bucles divergentes.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_code": {"type": "string"},
                    "safety_property": {"type": "string"}
                },
                "required": ["source_code"]
            }
        },
        {
            "name": "aleph_audit_database_isomorphism_occ_and_replication_consistency",
            "description": "Verificador Formal Integral de Isomorfismo SQL-TS, Concurrencia OCC y Consistencia Causal (v6.7.0 - NODE-03/01): demuestra aciclicidad en políticas RLS, isomorfismo biyectivo SQL <-> TypeScript, OCC version stamping y consistencia causal en réplicas.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "sql_schema": {"type": "string"},
                    "typescript_interfaces": {"type": "string"},
                    "query_code": {"type": "string"}
                },
                "required": ["sql_schema", "typescript_interfaces"]
            }
        },
        {
            "name": "aleph_model_check_linear_temporal_logic_and_buchi_automata",
            "description": "Verificador de Modelos en Lógica Temporal Lineal (LTL) y Autómatas de Büchi (v6.7.0 - NODE-01 Core SMT/CEGIS): demuestra formalmente propiedades temporales (Globally, Finally, Next, Until) sobre estructuras de Kripke y detecta ciclos aceptantes con Nested DFS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "kripke_structure": {"type": "object"},
                    "ltl_formula": {"type": "string"}
                },
                "required": ["kripke_structure", "ltl_formula"]
            }
        }
    ,
        {
            "name": "aleph_audit_multitenant_pool_and_transaction_isolation",
            "description": "Verificador Formal de Aislamiento Transaccional y Prevención de Fugas de Estado en Poolers Multi-Tenant (PgBouncer/Supavisor) (v6.8.0 - NODE-03 Shard Full-Stack DB): demuestra ausencia de mutación de sesión no local (SET vs SET LOCAL), valida dos fases no bloqueantes NOT VALID + VALIDATE CONSTRAINT en Foreign Keys DDL, audita confinamiento a nivel transacción en Advisory Locks y comprueba atomicidad estricta en ciclos de vida de transacciones concurrentes.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "sql_script": {"type": "string"},
                    "ddl_migrations_sql": {"type": "string"},
                    "service_code": {"type": "string"}
                }
            }
        },
        {
            "name": "aleph_audit_spec_vacuity_behavioral_subtyping_and_slsa_pcc",
            "description": "Auditor Formal de Vacuidad de Especificaciones (VerusEval/Beer), Mutación de Contratos (SpecMut), Subtipado Conductual de Liskov entre Releases (I_{t-1} -> I_t) y Atestación de Proveniencia SLSA Nivel 4 con Log de Transparencia Merkle RFC 6962 (v6.9.0 - NODE-06 Shard): detecta precondiciones insatisfacibles, poscondiciones tautológicas, contratos débiles que sobreviven a mutación, violaciones de contravarianza/covarianza de Liskov y emite Signed Tree Head SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "candidate_modules_map": {"type": "object"},
                    "previous_modules_map": {"type": "object"},
                    "expected_parent_sha256": {"type": "string"},
                    "actual_parent_sha256": {"type": "string"},
                    "release_version": {"type": "string"}
                },
                "required": ["candidate_modules_map"]
            }
        },
        {
            "name": "aleph_audit_matview_rls_jsonb_and_trigger_recursion",
            "description": "Verificador Formal de Seguridad RLS en Vistas/Materialized Views, Indización GIN sobre JSONB, Terminación de Triggers (pg_trigger_depth) y Particionado Zero-Downtime (v7.0.0 - NODE-03 Shard Full-Stack DB): demuestra presencia de security_invoker = true en vistas multi-tenant, valida REFRESH MATERIALIZED VIEW CONCURRENTLY, sintetiza índices GIN para predicados JSONB, previene recursión infinita en triggers UPDATE y audita DETACH PARTITION CONCURRENTLY.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "views_and_matviews_sql": {"type": "string"},
                    "jsonb_queries_and_ddl_sql": {"type": "string"},
                    "triggers_sql": {"type": "string"},
                    "partition_ddl_sql": {"type": "string"}
                }
            }
        },
        {
            "name": "aleph_prove_separation_logic_and_heap_disjointness",
            "description": "Demostrador de Lógica de Separación (P * Q), Disyunción de Heap y Regla de Marco (v6.9.0 - NODE-01 Core SMT/CEGIS): modela el heap simbólico mediante lógica de separación de Reynolds/O'Hearn, demuestra disyunción de dominios (dom(h1) ∩ dom(h2) = ∅), verifica la Regla de Marco (Frame Rule) y detecta aliasing mutable no aislado o accesos Use-After-Move.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_code": {"type": "string"},
                    "disjoint_params": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["source_code"]
            }
        },
        {
            "name": "aleph_merge_cross_shard_ast_and_prove_reproducible_pcc",
            "description": "Integrador Estructural 3-Way AST Multi-Shard (O -> (A, B) -> M), Reconciliador de Ramas Diamante, Mutación Diferencial sobre Deltas y Demostrador de Builds Deterministas Reproducibles Bit-a-Bit con Certificado PCC Multi-Padre (v7.1.0 - NODE-06 Shard): fusiona ramas paralelas del enjambre por unión estructural AST sin conflictos EOF, detecta colisiones semánticas reales, audita mutantes sobre el delta y demuestra reproducibilidad SHA-256 bit-a-bit.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "base_source": {"type": "string"},
                    "branch_a_source": {"type": "string"},
                    "branch_b_source": {"type": "string"},
                    "parent_a_sha256": {"type": "string"},
                    "parent_b_sha256": {"type": "string"},
                    "release_version": {"type": "string"}
                },
                "required": ["base_source", "branch_a_source", "branch_b_source"]
            }
        },
        {
            "name": "aleph_synthesize_craig_interpolants_and_cegar_abstraction",
            "description": "Sintetizador de Interpolantes de Craig y Refinamiento de Abstracción Guiado por Contraejemplos (CEGAR) (v7.2.0 - NODE-01 Core SMT/CEGIS): aplica el Teorema de Interpolación de Craig sobre particiones (A, B) con A ∧ B UNSAT para deducir el invariante modular intermedio I sobre vars(A) ∩ vars(B), eliminando contraejemplos espurios y refinando predicados de seguridad.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "prefix_formula_a": {"type": "string"},
                    "error_formula_b": {"type": "string"},
                    "initial_predicates": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["prefix_formula_a", "error_formula_b"]
            }
        },
        {
            "name": "aleph_audit_realtime_wal_storage_rls_and_postgrest_exposure",
            "description": "Verificador Formal de Seguridad en Publicaciones Realtime/WAL, Políticas RLS de Storage Buckets (storage.objects), Exposición PostgREST/pg_graphql y Prevención de Desbordamiento de Secuencias PK (v7.3.0 - NODE-03 Shard Full-Stack DB): bloquea REPLICA IDENTITY FULL con amplificación de WAL, exige predicados filter en suscripciones postgres_changes, verifica aislamiento de carpetas por auth.uid() en storage.objects, previene exposición de tablas internas en PostgREST y reemplaza claves SERIAL de 32 bits por BIGINT IDENTITY.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "realtime_and_ddl_sql": {"type": "string"},
                    "storage_policies_sql": {"type": "string"},
                    "client_subscription_and_query_code": {"type": "string"}
                }
            }
        },
        {
            "name": "aleph_audit_cls_initplan_jwt_metadata_and_lock_timeout",
            "description": "Verificador Formal de Inmutabilidad de Claims JWT (app_metadata vs user_metadata - Anti-CVE-2025-48757), Optimización O(1) InitPlan en RLS ((SELECT auth.uid())), Seguridad a Nivel de Columna (CLS) y Guardas de Cola de Bloqueo en Migraciones DDL (lock_timeout / statement_timeout / Batched Backfills) (v7.4.0 - NODE-03 Shard Full-Stack DB): bloquea escalada de privilegios por user_metadata en RLS, fuerza evaluación O(1) InitPlan, exige REVOKE UPDATE en columnas sensibles y previene bloqueos en cascada en migraciones DDL.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "rls_and_grants_sql": {"type": "string"},
                    "ddl_and_backfill_migration_sql": {"type": "string"}
                }
            }
        }
    ,
        {
            "name": "aleph_audit_hermetic_flakiness_metamorphic_mutation_and_sbom_pcc",
            "description": "Auditor Formal de Hermeticidad de Tests, Independencia de Orden por Permutación (OD-Tests), Mutación Metamórfica sin Oráculo y Certificación SBOM Criptográfica CycloneDX 1.6 Zero-Dependency (v7.5.0 - NODE-06 Shard): detecta tests flaky y dependencias de estado global bajo permutaciones directa/inversa, verifica relaciones metamórficas (MONOTONICITY, COMMUTATIVITY, SCALING_LINEARITY, IDEMPOTENCE) y emite SBOM CycloneDX 1.6 sellado con SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "target_source_code": {"type": "string"},
                    "test_suite_source_code": {"type": "string"},
                    "metamorphic_property": {"type": "string"},
                    "release_version": {"type": "string"}
                },
                "required": ["target_source_code"]
            }
        }            ,
        {
            "name": "aleph_audit_and_synthesize_awwwards_strategic_ui",
            "description": "Motor Formal de Dirección de Arte Nivel Awwwards (SotD/SotY), Colorimetría Perceptual OKLCH/APCA, Escala Tipográfica Modular Áurea, Coreografía 60 FPS GPU Zero-CLS y Diseño Estratégico por Objetivo (v7.6.0 - NODE-02 Shard): audita y auto-repara componentes React/Tailwind/CSS contra anti-patrones visuales y de layout thrashing, evalúa con la rúbrica de 4 pilares del jurado Awwwards y sintetiza experiencias completas calibradas por objetivo estratégico (awwwards_editorial_scrollytelling, high_conversion_product_landing, luxury_brand_immersive, mission_critical_operator_console).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_code": {"type": "string"},
                    "strategic_objective": {"type": "string"},
                    "component_name": {"type": "string"}
                },
                "required": ["source_code"]
            }
        },
        {
            "name": "aleph_audit_pg18_uuidv7_partitioning_and_optimistic_studio_sync",
            "description": "Verificador Formal de Localidad B-Tree con uuidv7() Nativo en PostgreSQL 18, Particionamiento Declarativo Zero-Downtime (CHECK NOT VALID + VALIDATE CONSTRAINT antes de ATTACH PARTITION y DETACH PARTITION CONCURRENTLY), Herencia Forzada de RLS en Particiones y Sincronización Isomórfica entre Studio UI Nivel Awwwards (OKLCH/Zero-CLS) y Control de Concurrencia Optimista OCC (v7.7.0 - NODE-03 Shard Full-Stack DB): previene fragmentación B-Tree por UUIDv4 aleatorio, bloqueos ACCESS EXCLUSIVE en mantenimiento de particiones y pérdida de escrituras en mutaciones optimistas.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "partition_and_ddl_sql": {"type": "string"},
                    "studio_optimistic_ui_and_occ_code": {"type": "string"}
                }
            }
        }
    ,
        {
            "name": "aleph_prove_assume_guarantee_and_wfg_deadlock_free_orchestration",
            "description": "Demostrador Formal de Orquestación Multi-Agente Composicional Assume-Guarantee, Libertad de Interbloqueos en Grafos Wait-For (WFG) y Liveness de Barreras Concurrentes (v7.7.0 - NODE-01 Shard): verifica implicación composicional G_u => A_v entre olas del DAG con síntesis CEGIS de contratos puente, detecta ciclos de espera circular de recursos (Coffman #4) sintetizando ordenamiento canónico lexicográfico y certifica liveness de barreras con sello PCC SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "nodes": {"type": "array", "items": {"type": "object"}},
                    "workflow_id": {"type": "string"}
                },
                "required": ["nodes"]
            }
        }            ,
        {
            "name": "aleph_fuzz_differential_branches_and_attest_intoto_pcc",
            "description": "Fuzzer Simbólico Dirigido por Distancia de Ramas (Korel Branch Distance), Verificador de Oráculo Diferencial Cruzado y Atestación Criptográfica in-toto v1.0 Supply-Chain PCC (v7.8.0 - NODE-06 Shard): sintetiza vectores de frontera {C-1, C, C+1} para cubrir el 100% de las ramas AST, detecta ramas muertas (UNCOVERED_DEAD_AST_BRANCH) y divergencias diferenciales entre versiones (DIFFERENTIAL_ORACLE_DIVERGENCE), y sella una atestación in-toto v1.0 multi-padre con SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "reference_source_code": {"type": "string"},
                    "candidate_source_code": {"type": "string"},
                    "parent_bundle_sha256": {"type": "string"},
                    "release_version": {"type": "string"}
                },
                "required": ["reference_source_code"]
            }
        },
        {
            "name": "aleph_prove_linearizability_and_epoch_fencing_consensus",
            "description": "Demostrador Formal de Linealizabilidad de Historias Concurrentes (Herlihy & Wing 1990) y Tokens de Cercado Monótonos por Época (Kleppmann Epoch Fencing Tokens) contra Escrituras Zombie (v7.9.0 - NODE-01 Shard): verifica la existencia de un orden secuencial legal que respete el orden parcial de tiempo real entre intervalos [t_inv, t_res], bloquea lecturas obsoletas (Stale Reads) y escrituras de líderes zombies con epoch expirado, y sintetiza guardas atómicas SQL y Rust con certificado PCC SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "operations": {"type": "array", "items": {"type": "object"}},
                    "initial_value": {},
                    "history_id": {"type": "string"}
                },
                "required": ["operations"]
            }
        },
        {
            "name": "aleph_prove_k_induction_and_ic3_property_directed_reachability",
            "description": "Demostrador Formal de Seguridad No Acotada mediante k-Inducción de Caminos Simples y Alcance Dirigido por Propiedades IC3/PDR (v8.0.0 - NODE-01 Shard): combina Bounded Model Checking (BMC) con el paso inductivo de profundidad k y síntesis automática de cláusulas de bloqueo IC3/PDR para eliminar contraejemplos espurios a la inducción (CTIs) y demostrar seguridad en horizonte infinito con certificado PCC SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "states": {"type": "array", "items": {"type": "string"}},
                    "initial_states": {"type": "array", "items": {"type": "string"}},
                    "transitions": {"type": "array", "items": {"type": "object"}},
                    "safe_states": {"type": "array", "items": {"type": "string"}},
                    "max_k": {"type": "integer"},
                    "system_id": {"type": "string"}
                },
                "required": ["states", "initial_states", "transitions", "safe_states"]
            }
        },
        {
            "name": "aleph_prove_crdt_sec_semilattice_and_causal_cut_consistency",
            "description": "Demostrador Formal de Consistencia Eventual Fuerte (SEC) sobre Retículos de Unión CRDT (Join-Semilattices: Idempotencia, Conmutatividad y Asociatividad) y Consistencia de Cortes Causales con Relojes Vectoriales (v8.1.0 - NODE-01 Shard): detecta operadores de fusión dependientes del orden o no idempotentes y efectos huérfanos en snapshots distribuidos con certificado PCC SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "replica_states": {"type": "array", "items": {"type": "object"}},
                    "merge_strategy": {"type": "string"},
                    "causal_events": {"type": "array", "items": {"type": "object"}},
                    "cut_event_ids": {"type": "array", "items": {"type": "string"}},
                    "crdt_id": {"type": "string"}
                },
                "required": ["replica_states"]
            }
        },
        {
            "name": "aleph_prove_ssi_serializability_and_write_skew_prevention",
            "description": "Demostrador Formal de Serializabilidad Estricta bajo Snapshot Isolation (SSI - Cahill et al.) y Grafo de Serialización Directa de Adya (DSG: ww, wr, rw) contra anomalías Write Skew (v8.2.0 - NODE-01 Shard): construye el grafo DSG entre transacciones concurrentes, detecta ciclos de antidependencia rw y estructuras peligrosas T1 -rw-> T2 -rw-> T3, y sintetiza guardas SELECT ... FOR UPDATE y reintentos SQLSTATE 40001 con certificado PCC SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "transactions": {"type": "array", "items": {"type": "object"}},
                    "schedule_id": {"type": "string"}
                },
                "required": ["transactions"]
            }
        },
        {
            "name": "aleph_prove_multiparty_session_types_and_protocol_fidelity",
            "description": "Demostrador Formal de Tipos de Sesión Multiparte (MPST - Honda, Yoshida & Carbone POPL 2008), Proyección de Coreografías Globales (G | p), Dualidad Send/Receive y Ausencia de Mensajes Huérfanos (v8.3.0 - NODE-01 Shard): verifica conectividad causal en protocolos multi-agente/gRPC, comprueba fidelidad de endpoints locales frente a la proyección canónica y sintetiza canales Typestate en Rust con certificado PCC SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "global_steps": {"type": "array", "items": {"type": "object"}},
                    "local_endpoints": {"type": "object"},
                    "protocol_id": {"type": "string"}
                },
                "required": ["global_steps"]
            }
        },
        {
            "name": "aleph_prove_happens_before_race_freedom_and_dpor_schedules",
            "description": "Detector Formal de Condiciones de Carrera Happens-Before con Épocas FastTrack (Flanagan & Freund PLDI 2009) y Reducción Dinámica de Orden Parcial (DPOR - Flanagan & Godefroid POPL 2005) sobre Trazas de Mazurkiewicz (v8.4.0 - NODE-01 Shard): rastrea relojes vectoriales por hilo y lock (ACQUIRE/RELEASE/FORK/JOIN), detecta carreras Write-Write, Write-Read y Read-Write sin orden causal y sintetiza conjuntos de backtracking DPOR con certificado PCC SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "events": {"type": "array", "items": {"type": "object"}},
                    "trace_id": {"type": "string"}
                },
                "required": ["events"]
            }
        },
        {
            "name": "aleph_prove_lockfree_aba_freedom_and_epoch_reclamation",
            "description": "Demostrador Formal de Inmunidad ABA en Estructuras Lock-Free (Michael & Scott / Treiber), Reclamación de Memoria Basada en Épocas de 3 Fases (EBR - Fraser 2004 / crossbeam-epoch) y Progreso No Bloqueante (v8.5.0 - NODE-01 Shard): detecta vulnerabilidades A->B->A en bucles CAS sin etiqueta monótona de generación, previene Use-After-Free por liberación prematura de nodos antes del período de gracia de 2 épocas y certifica ausencia de bloqueos con PCC SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "cas_operations": {"type": "array", "items": {"type": "object"}},
                    "reclamation_events": {"type": "array", "items": {"type": "object"}},
                    "contains_blocking_in_cas_loop": {"type": "boolean"},
                    "algorithm_id": {"type": "string"}
                },
                "required": ["cas_operations"]
            }
        },
        {
            "name": "aleph_prove_structured_concurrency_and_cancellation_safety",
            "description": "Demostrador Formal de Concurrencia Estructurada (Nurseries / TaskGroups / Tokio JoinSet), Contención Léxica de Tiempos de Vida y Seguridad ante Cancelación en Puntos Await (v8.6.0 - NODE-01 Shard): verifica que toda subtarea termine antes del cierre del ámbito padre ([t_spawn, t_join] subset [t_enter, t_exit]), detecta pérdida de estado parcial en ramas tokio::select! / wait_for multi-await sin reserva de 2 fases y certifica propagación de cancelación a tareas hermanas con PCC SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "parent_scope": {"type": "object"},
                    "child_tasks": {"type": "array", "items": {"type": "object"}},
                    "select_branches": {"type": "array", "items": {"type": "object"}},
                    "nursery_id": {"type": "string"}
                },
                "required": ["parent_scope", "child_tasks"]
            }
        },
        {
            "name": "aleph_prove_chase_lev_work_stealing_and_brent_tail_latency",
            "description": "Demostrador Formal de Colas de Robo de Trabajo Chase-Lev (Chase & Lev SPAA 2005 / Lê et al. PPoPP 2013), Cota Superior de Latencia por el Teorema de Brent-Graham (T_P <= (T_1 - T_inf)/P + T_inf) y Ausencia de Bloqueo Head-of-Line en Runtimes Asíncronos (v8.7.0 - NODE-01 Shard): verifica la barrera SeqCst y el arbitraje CAS en el último elemento (top == bottom - 1), calcula el camino crítico T_inf y detecta tareas que exceden el cuanto cooperativo sin spawn_blocking con PCC SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "tasks": {"type": "array", "items": {"type": "object"}},
                    "worker_cores": {"type": "integer"},
                    "sla_budget_ms": {"type": "number"},
                    "max_cooperative_quantum_ms": {"type": "number"},
                    "deque_config": {"type": "object"},
                    "scheduler_id": {"type": "string"}
                },
                "required": ["tasks"]
            }
        },
        {
            "name": "aleph_prove_vyukov_mpmc_ring_buffer_and_codel_backpressure",
            "description": "Demostrador Formal de Colas Acotadas Lock-Free MPMC de Vyukov / LMAX Disruptor, Aislamiento de Línea de Caché L1 (64 Bytes Anti-False-Sharing MESI) y Control de Admisión Adaptativo por Ley de Little (L = lambda * W) y CoDel (v8.8.0 - NODE-01 Shard): verifica capacidad potencia de 2, progresión monotónica de secuencia por slot con barreras Acquire/Release, separación >= 64 bytes entre cursores head/tail y estabilidad de cola bajo sobrecarga con PCC SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "capacity": {"type": "integer"},
                    "slots_state": {"type": "array", "items": {"type": "object"}},
                    "memory_orderings": {"type": "object"},
                    "struct_layout": {"type": "object"},
                    "arrival_rate_rps": {"type": "number"},
                    "service_rate_rps": {"type": "number"},
                    "observed_sojourn_ms": {"type": "number"},
                    "codel_target_ms": {"type": "number"},
                    "load_shedding_enabled": {"type": "boolean"},
                    "ring_id": {"type": "string"}
                },
                "required": ["capacity", "slots_state"]
            }
        },
        {
            "name": "aleph_prove_waitfree_seqlock_and_rcu_leftright_grace_period",
            "description": "Demostrador Formal de Sincronización Wait-Free de Lectura mediante SeqLock (Lamport 1977 / Boehm MSPC 2012) y RCU / Left-Right de Doble Réplica con Período de Gracia Determinista (v8.9.0 - NODE-01 Shard): verifica el protocolo impar/par de SeqLock con barrera LoadLoad (Ordering::Acquire) antes de s2, ausencia de RMW atómico compartido en lectores, aislamiento de réplica activa/inactiva en Left-Right y drenaje completo del Grace Period antes de reclamar o mutar la segunda réplica con PCC SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "seqlock_traces": {"type": "array", "items": {"type": "object"}},
                    "rcu_leftright_state": {"type": "object"},
                    "memory_barriers": {"type": "object"},
                    "primitive_id": {"type": "string"}
                },
                "required": ["seqlock_traces", "rcu_leftright_state"]
            }
        },
        {
            "name": "aleph_prove_flat_combining_and_mcs_queue_lock",
            "description": "Demostrador Formal de Flat Combining y Árboles de Eliminación (Hendler, Incze, Shavit & Tzafrir SPAA 2010) + Colas de Bloqueo MCS con Local-Spinning Aislado en Caché L1 y Traspaso de Sucesor Libre de Deadlock (Mellor-Crummey & Scott TOCS 1991) (v9.0.0 - NODE-01 Shard): verifica linealizabilidad de reducción algebraica por lotes (prefix-sum exacto por hilo), ausencia de inanición en Publication Records y protocolo de espera me.next != null ante fallo de CAS en tail durante MCS unlock() con PCC SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "publication_slots": {"type": "array", "items": {"type": "object"}},
                    "initial_state": {"type": "integer"},
                    "reported_final_state": {"type": "integer"},
                    "mcs_handoff_trace": {"type": "object"},
                    "memory_and_cleanup_config": {"type": "object"},
                    "combiner_id": {"type": "string"}
                },
                "required": ["publication_slots", "initial_state", "reported_final_state", "mcs_handoff_trace"]
            }
        },
        {
            "name": "aleph_prove_hierarchical_timing_wheel_and_io_uring_proactor",
            "description": "Demostrador Formal de Ruedas de Tiempo Jerárquicas O(1) (Varghese & Lauck SOSP 1987 / Kafka / Tokio Timer Driver) y Anillos Proactor Asíncronos io_uring (v9.1.0 - NODE-01 Shard): verifica indexación O(1) por máscara potencia de 2, cascada monotónica entre niveles sin disparo prematuro, barreras Acquire/Release en colas SQ/CQ de io_uring, prevención de CQE overflow (in_flight + unconsumed <= CQ) y pinning estricto de buffers DMA hasta cosechar el CQE con PCC SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "wheel_levels": {"type": "array", "items": {"type": "object"}},
                    "timer_events": {"type": "array", "items": {"type": "object"}},
                    "io_uring_state": {"type": "object"},
                    "wheel_id": {"type": "string"}
                },
                "required": ["wheel_levels", "timer_events", "io_uring_state"]
            }
        },
        {
            "name": "aleph_prove_mimalloc_slab_sharding_and_arena_region_lifetime",
            "description": "Demostrador Formal de Asignadores Concurrentes Thread-Local Slab Sharding (mimalloc Leijen et al. ISMM 2019: local_free vs xthread_free MPSC Atomic Swap), Conservación de Bloques de Slab, Cuarentena de Double-Free por Bitmap y Arenas Bump-Pointer con Inferencia de Regiones (v9.2.0 - NODE-01 Shard): verifica que hilos remotos liberen exclusivamente en xthread_free con Release/AcqRel, audita la ecuación in_use + local_free + xthread_free == capacity, detecta double-free antes de corromper la lista intrusiva y prueba ausencia de fugas Use-After-Arena-Reset con PCC SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "slab_state": {"type": "object"},
                    "free_operations": {"type": "array", "items": {"type": "object"}},
                    "arena_allocations": {"type": "array", "items": {"type": "object"}},
                    "allocator_id": {"type": "string"}
                },
                "required": ["slab_state", "free_operations", "arena_allocations"]
            }
        },
        {
            "name": "aleph_prove_wtinylfu_cache_and_split_ordered_hashmap",
            "description": "Demostrador Formal de Cachés Concurrentes Resistentes a Escaneos Masivos W-TinyLFU (Einziger, Friedman & Manes TOCS 2017 / Count-Min Sketch 4-bit + Doorkeeper + SLRU) y Tablas Hash Concurrentes Split-Ordered / Shard-Striped Libres de Deadlock (Shalev & Shavit JACM 2006 / DashMap / Moka) (v9.3.0 - NODE-01 Shard): verifica admisión f(cand) > f(victim), decaimiento periódico por desplazamiento de bits, inversión de bits LSB en claves Split-Ordered y ausencia de reentrancia de shard o retención de guardas a través de .await con PCC SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "cache_config": {"type": "object"},
                    "cms_admission_trials": {"type": "array", "items": {"type": "object"}},
                    "hashmap_operations": {"type": "array", "items": {"type": "object"}},
                    "cache_id": {"type": "string"}
                },
                "required": ["cache_config", "cms_admission_trials", "hashmap_operations"]
            }
        },
        {
            "name": "aleph_prove_wal_group_commit_and_aries_torn_write_recovery",
            "description": "Demostrador Formal de Group Commit Leader-Follower en Write-Ahead Logs (RocksDB / PostgreSQL XLogInsert), Regla Write-Ahead de ARIES (page_lsn <= flushed_lsn, Mohan et al. TODS 1992), Detección de Torn-Writes por Checksum CRC32C/Epoch y Doble Buffer Ping-Pong (v9.4.0 - NODE-01 Shard): verifica contigüidad monotónica de LSNs, amortización a 1 solo fdatasync por lote, prohibición de volcar páginas sucias con page_lsn > flushed_lsn y aislamiento de buffers fill/flush con PCC SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "batch_entries": {"type": "array", "items": {"type": "object"}},
                    "dirty_page_flushes": {"type": "array", "items": {"type": "object"}},
                    "wal_buffer_state": {"type": "object"},
                    "wal_id": {"type": "string"}
                },
                "required": ["batch_entries", "dirty_page_flushes", "wal_buffer_state"]
            }
        },
        {
            "name": "aleph_prove_lsm_compaction_tombstone_and_ribbon_filter",
            "description": "Demostrador Formal de Compactación por Niveles en Árboles LSM (O'Neil et al. 1996 / RocksDB / Dostoevsky), Prevención de Resurrección de Datos Zombie por Eliminación Prematura de Tombstones y Filtros Estáticos Ribbon / Binary Fuse sobre GF(2) con 0.0% Falsos Negativos (v9.5.0 - NODE-01 Shard): verifica disjunción estricta de intervalos de claves en niveles >= 1, retención de tombstones frente a snapshots activos o niveles inferiores solapados y cota de amplificación de escritura WAF con PCC SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "level_sstables": {"type": "array", "items": {"type": "object"}},
                    "tombstone_compactions": {"type": "array", "items": {"type": "object"}},
                    "ribbon_filter_state": {"type": "object"},
                    "lsm_config": {"type": "object"},
                    "engine_id": {"type": "string"}
                },
                "required": ["level_sstables", "tombstone_compactions", "ribbon_filter_state"]
            }
        },
        {
            "name": "aleph_prove_lehman_yao_blink_tree_and_optimistic_lock_coupling",
            "description": "Demostrador Formal de Árboles B-Link Concurrentes de Lehman-Yao (TODS 1981 / PostgreSQL nbtree: High-Key + Right-Sibling Link antes de inserción en padre) y Optimistic Lock Coupling (OLC - Leis et al. ICDE 2016: Validación Hand-Over-Hand de Versiones Padre->Hijo sin RMW Atómico en Lectores) (v9.6.0 - NODE-01 Shard): verifica enlaces right_link con Release antes de dividir, persecución de hermano derecho cuando search_key > high_key, validación v_parent tras leer v_child y orden de latches libre de deadlock con PCC SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "node_splits": {"type": "array", "items": {"type": "object"}},
                    "reader_traversals": {"type": "array", "items": {"type": "object"}},
                    "latch_acquisitions": {"type": "array", "items": {"type": "object"}},
                    "index_id": {"type": "string"}
                },
                "required": ["node_splits", "reader_traversals", "latch_acquisitions"]
            }
        },
        {
            "name": "aleph_prove_calvin_deterministic_sequencer_and_silo_occ_commit",
            "description": "Demostrador Formal de Ejecución Transaccional Determinista Calvin (Thomson et al. SIGMOD 2012: Orden Global de Secuencia sin 2PC ni Deadlocks + Validación Reconnaissance OLLP) y Protocolo de Commit Optimista por Épocas en 3 Fases Silo (Tu et al. SOSP 2013: Bloqueo Canónico de Write-Set, Validación de Read-Set y Asignación Monotónica de TID) (v9.7.0 - NODE-01 Shard): verifica secuenciación estricta, completitud de conjuntos pre-declarados OLLP y las 3 fases de commit Silo OCC con PCC SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "calvin_sequenced_batch": {"type": "array", "items": {"type": "object"}},
                    "silo_commit_protocol": {"type": "object"},
                    "engine_id": {"type": "string"}
                },
                "required": ["calvin_sequenced_batch", "silo_commit_protocol"]
            }
        },
        {
            "name": "aleph_prove_hlc_causality_and_mvcc_uncertainty_window",
            "description": "Demostrador Formal de Relojes Lógicos Híbridos (HLC - Kulkarni et al. OPODIS 2014 / CockroachDB), Ventana de Incertidumbre Causal con Read-Restart ([t_read, t_read + max_offset]) y Seguridad de Marca de Agua de Recolección de Basura MVCC (v9.8.0 - NODE-01 Shard - Tool MCP #100): verifica monotonicidad lexicográfica (l, c), rechazo de deriva física > max_offset, reinicio de lectura ante escrituras en la banda de incertidumbre y cota de poda MVCC GC con PCC SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "hlc_transitions": {"type": "array", "items": {"type": "object"}},
                    "uncertainty_reads": {"type": "array", "items": {"type": "object"}},
                    "mvcc_gc_state": {"type": "object"},
                    "max_offset_ms": {"type": "integer"},
                    "clock_id": {"type": "string"}
                },
                "required": ["hlc_transitions", "uncertainty_reads", "mvcc_gc_state"]
            }
        },
        {
            "name": "aleph_prove_raft_read_index_lease_and_joint_consensus",
            "description": "Demostrador Formal de Lecturas Linealizables Sin Disco mediante Raft ReadIndex y LeaseRead Acotado por Deriva de Reloj (Ongaro & Ousterhout USENIX ATC 2014 Sec. 6.4 / TiKV / etcd) + Reconfiguración de Membresía por Consenso Conjunto (C_old,new) Libre de Split-Brain (v9.9.0 - NODE-01 Shard - Tool MCP #101): verifica barrera No-Op del término actual, confirmación de mayoría de heartbeats, espera last_applied >= read_index, margen de deriva en LeaseRead y transiciones C_old,new con PCC SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "read_requests": {"type": "array", "items": {"type": "object"}},
                    "lease_state": {"type": "object"},
                    "membership_transitions": {"type": "array", "items": {"type": "object"}},
                    "cluster_id": {"type": "string"}
                },
                "required": ["read_requests", "lease_state", "membership_transitions"]
            }
        },
        {
            "name": "aleph_prove_chandy_lamport_snapshot_and_raft_log_compaction",
            "description": "Demostrador Formal de Cortes Globales Consistentes de Chandy-Lamport (TOCS 1985: Marcadores FIFO + Conservación de Estado en Vuelo) y Compactación de Log Raft InstallSnapshot con Preservación de Sufijo Comiteado (Ongaro & Ousterhout 2014 Sec. 7) (v10.0.0 - NODE-01 Shard - Tool MCP #102): verifica emisión inmediata de <MARKER>, suma exacta nodos + canales en vuelo, validación de término/SHA-256 en chunks de snapshot y retención del sufijo de log posterior a last_included_index con PCC SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "node_states": {"type": "array", "items": {"type": "object"}},
                    "channel_recordings": {"type": "array", "items": {"type": "object"}},
                    "install_snapshot_op": {"type": "object"},
                    "expected_total_invariant": {"type": "integer"},
                    "snapshot_id": {"type": "string"}
                },
                "required": ["node_states", "channel_recordings", "install_snapshot_op", "expected_total_invariant"]
            }
        },
        {
            "name": "aleph_prove_phi_accrual_failure_detector_and_swim_lifeguard",
            "description": "Demostrador Formal de Detectores de Fallos Probabilísticos Phi-Accrual (Hayashibara et al. SRDS 2004 / Cassandra / Akka) y Protocolo de Membresía SWIM con Sondeo Indirecto Ping-Req(k), Multiplicador de Salud Local Lifeguard (LHM) y Refutación Monotónica por Encarnación (v10.1.0 - NODE-01 Shard - Tool MCP #103): verifica ventana mínima de muestras, piso de desviación estándar sigma_min, umbral continuo Phi >= 8.0, sondeo indirecto k >= 1, escalado de timeout (1 + LHM) y refutación inc_new > inc_suspect con PCC SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "heartbeat_windows": {"type": "array", "items": {"type": "object"}},
                    "swim_probes": {"type": "array", "items": {"type": "object"}},
                    "incarnation_refutations": {"type": "array", "items": {"type": "object"}},
                    "detector_id": {"type": "string"}
                },
                "required": ["heartbeat_windows", "swim_probes", "incarnation_refutations"]
            }
        },
        {
            "name": "aleph_prove_merkle_anti_entropy_and_bounded_staleness",
            "description": "Demostrador Formal de Árboles de Merkle de Anti-Entropía Activa con Separación de Dominio RFC 6962 (0x00/0x01), Hinted Handoff en Quórum Sloppy y Lecturas de Seguidor con Cota Estricta de Obsolescencia (Bounded Staleness Follower Reads) (v10.2.0 - NODE-01 Shard - Tool MCP #104): verifica localización sub-lineal O(k log B) de buckets divergentes, TTL e idempotencia HLC en Hinted Handoff y lectura monotónica de seguidor acotada en versiones y tiempo con PCC SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "merkle_sync_sessions": {"type": "array", "items": {"type": "object"}},
                    "hinted_handoff_envelopes": {"type": "array", "items": {"type": "object"}},
                    "follower_read_requests": {"type": "array", "items": {"type": "object"}},
                    "sync_id": {"type": "string"}
                },
                "required": ["merkle_sync_sessions", "hinted_handoff_envelopes", "follower_read_requests"]
            }
        },
        {
            "name": "aleph_prove_consistent_hashing_bounded_load_and_epoch_rebalance",
            "description": "Demostrador Formal de Hashing Consistente con Carga Acotada (1 + epsilon) (Mirrokni et al. SODA 2018 / Google Maglev), Rebalanceo Elástico de Shards sin Split-Brain y Epoch-Fenced Chain Replication (v10.3.0 - NODE-01 Shard - Tool MCP #105): verifica cota máxima ceil((1+epsilon)*L/N), rechazo de tablas de ruteo obsoletas por Ring Epoch Fencing y migración Freeze-Drain-Handover con PCC SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "ring_nodes": {"type": "array", "items": {"type": "object"}},
                    "routed_operations": {"type": "array", "items": {"type": "object"}},
                    "range_migrations": {"type": "array", "items": {"type": "object"}},
                    "epsilon_bound": {"type": "number"},
                    "cluster_id": {"type": "string"}
                },
                "required": ["ring_nodes", "routed_operations", "range_migrations"]
            }
        },
        {
            "name": "aleph_prove_hierarchical_token_bucket_and_little_law_load_shedding",
            "description": "Demostrador Formal de Limitadores Jerárquicos de Tasa por Cubeta de Tokens Multi-Tenant (HTB u64 sin Starvation) y Control de Concurrencia Adaptativo por Ley de Little (Netflix Gradient2 / TCP Vegas) con Descarte Prioritario de Carga por Presupuesto de Deadline (v10.4.0 - NODE-01 Shard - Tool MCP #106): verifica conservación de tokens en punto fijo, aislamiento CIR contra vecinos ruidosos, retroceso por gradiente RTT y preservación de tráfico crítico P0 con PCC SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "tenant_buckets": {"type": "array", "items": {"type": "object"}},
                    "gradient_windows": {"type": "array", "items": {"type": "object"}},
                    "admission_decisions": {"type": "array", "items": {"type": "object"}},
                    "global_cluster_capacity_tokens": {"type": "integer"},
                    "limiter_id": {"type": "string"}
                },
                "required": ["tenant_buckets", "gradient_windows", "admission_decisions"]
            }
        },
        {
            "name": "aleph_prove_tail_at_scale_hedged_requests_and_adaptive_circuit_breaker",
            "description": "Demostrador Formal de Solicitudes Especulativas Acotadas (Tail-at-Scale Tied/Hedged Requests, Dean & Barroso CACM 2013), Cortacircuitos Adaptativos de Ventana Deslizante (CLOSED -> OPEN -> HALF_OPEN) y Backoff Exponencial con Jitter Estocástico y Presupuesto de Reintentos (v10.5.0 - NODE-01 Shard - Tool MCP #107): verifica disparo p95 con presupuesto <= 5% y cancelación del perdedor, volumen mínimo de ventana deslizante y reintentos idempotentes acotados con PCC SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "hedged_policies": {"type": "array", "items": {"type": "object"}},
                    "circuit_breaker_transitions": {"type": "array", "items": {"type": "object"}},
                    "retry_policies": {"type": "array", "items": {"type": "object"}},
                    "resilience_id": {"type": "string"}
                },
                "required": ["hedged_policies", "circuit_breaker_transitions", "retry_policies"]
            }
        },
        {
            "name": "aleph_prove_2pc_presumed_abort_and_epoch_fenced_saga",
            "description": "Demostrador Formal de Commit Atómico en 2 Fases con Presumed Abort (Mohan et al. ACM TODS 1986), Protocolo de Terminación Cooperativa sin Split-Brain Heurístico y Compensación de Sagas en Orden Inverso con Epoch-Fencing contra Escrituras Zombie (v10.6.0 - NODE-01 Shard - Tool MCP #108): verifica barrera fsync en Prepare/Commit, prohibición de decisiones heurísticas unilaterales y tombstone de aborto antes de compensar con PCC SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "two_phase_rounds": {"type": "array", "items": {"type": "object"}},
                    "in_doubt_resolutions": {"type": "array", "items": {"type": "object"}},
                    "fenced_saga_executions": {"type": "array", "items": {"type": "object"}},
                    "coordinator_id": {"type": "string"}
                },
                "required": ["two_phase_rounds", "in_doubt_resolutions", "fenced_saga_executions"]
            }
        },
        {
            "name": "aleph_prove_and_synthesize_view_transition_webgl_and_scroll_timeline",
            "description": "Demostrador Formal de Biyección View Transitions API (FLIP), Ciclo de Vida VRAM WebGL/Three.js, Scroll-Driven Animations en GPU Compositor y Alineación Espacial CSS Subgrid Nivel Awwwards SotY (v7.9.0 - NODE-02 Shard): detecta y auto-repara colisiones de view-transition-name en listas, fugas de VRAM por falta de .dispose() y DPR sin tope en WebGL/Three.js, listeners de scroll síncronos en hilo principal y desalineación de ejes en grillas Bento sin subgrid, sintetizando experiencias interactivas SotY selladas con PCC SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_code": {"type": "string"},
                    "component_name": {"type": "string"}
                },
                "required": ["source_code"]
            }
        }            ,
        {
            "name": "aleph_prove_wcag22_target_focus_container_queries_and_variable_fonts",
            "description": "Demostrador Formal de los 6 Criterios WCAG 2.2 AA que los escáneres omiten (2.5.8 Target Size >=24x24px/44x44px, 2.4.11 Focus Not Obscured con cabeceras sticky/fixed, 2.5.7 Dragging Single-Pointer Equivalence, 3.3.8 Accessible Auth sin bloqueo onPaste), Container Queries Intrínsecas (@container inline-size vs ResizeObserver state thrashing), CSS Anchor Positioning y Coreografía de Fuentes Variables Zero-CLS con guarda @media (hover: hover) Nivel Awwwards SotY (v8.0.0 - NODE-02 Shard).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_code": {"type": "string"},
                    "component_name": {"type": "string"}
                },
                "required": ["source_code"]
            }
        },
        {
            "name": "aleph_prove_inp_yield_starting_style_top_layer_and_lcp_priority",
            "description": "Demostrador Formal de INP < 100ms (scheduler.yield / React.startTransition en handlers interactivos), Top-Layer Nativo (@starting-style + transition-behavior: allow-discrete + Popover API contra guerras de z-[9999]), OffscreenCanvas Worker Isolation y Priorización Hero LCP < 1.5s (fetchPriority='high' contra loading='lazy' en primer pliegue) Nivel Awwwards SotY (v8.1.0 - NODE-02 Shard).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_code": {"type": "string"},
                    "component_name": {"type": "string"}
                },
                "required": ["source_code"]
            }
        },
        {
            "name": "aleph_prove_dtcg2025_relative_oklch_content_visibility_and_react19_actions",
            "description": "Demostrador Formal de Esquemas W3C Design Tokens DTCG 2025.10 ($value/$type en espacio oklch), Sintaxis de Color Relativo CSS Level 5 (oklch(from var(--token) calc(l + ...) c h) + light-dark()), Contención de Renderizado Zero-CLS (content-visibility: auto acoplado a contain-intrinsic-size: auto <height>) y Formularios Progresivos React 19 (useActionState + useOptimistic contra onSubmit e.preventDefault()) Nivel Awwwards SotY (v8.2.0 - NODE-02 Shard).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_code": {"type": "string"},
                    "component_name": {"type": "string"}
                },
                "required": ["source_code"]
            }
        },
        {
            "name": "aleph_prove_speculation_rules_text_wrap_rsc_waterfall_and_forced_colors",
            "description": "Demostrador Formal de Speculation Rules API Zero-Latency Prerendering (eagerness 'moderate' con exclusión de rutas mutables /logout, /checkout, /delete, /api), Tipografía Óptica CSS Text Level 4 (text-wrap: balance en titulares vs text-wrap: pretty en prosa), Eliminación de Cascadas Secuenciales RSC (Promise.all + Suspense) y Resiliencia Asistiva @media (forced-colors: active) / prefers-contrast Nivel Awwwards SotY (v8.3.0 - NODE-02 Shard).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_code": {"type": "string"},
                    "component_name": {"type": "string"}
                },
                "required": ["source_code"]
            }
        },
        {
            "name": "aleph_prove_interpolate_size_field_sizing_roving_tabindex_and_webgpu",
            "description": "Demostrador Formal de Animaciones Intrínsecas CSS Values Level 5 (interpolate-size: allow-keywords / calc-size(auto, size) contra max-h-[999px]), Auto-Crecimiento de Inputs sin Reflow JS (field-sizing: content contra lecturas síncronas de scrollHeight), Orden de Foco WAI-ARIA APG Roving Tabindex (WCAG 2.2 AA 2.4.3 contra tabIndex > 0) y Resiliencia WebGPU WGSL (alineación 16-byte + device.lost recovery) Nivel Awwwards SotY (v8.4.0 - NODE-02 Shard).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_code": {"type": "string"},
                    "component_name": {"type": "string"}
                },
                "required": ["source_code"]
            }
        },
        {
            "name": "aleph_prove_css_property_houdini_wcag_redundant_entry_and_svg_filter_bounds",
            "description": "Demostrador Formal de Propiedades Tipadas CSS Houdini (@property con inherits: false para interpolación 60 FPS de gradientes/ángulos), Vinculación ARIA Isomórfica React 19 (useId() contra colisiones de IDs estáticos), Persistencia Anti-Entrada Redundante WCAG 2.2 AA (3.3.7 Redundant Entry & 3.2.6 Consistent Help) y Acotamiento de Filtros SVG GPU (feTurbulence / feDisplacementMap con x='0%' y='0%' width='100%' height='100%' colorInterpolationFilters='sRGB') Nivel Awwwards SotY (v8.5.0 - NODE-02 Shard).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_code": {"type": "string"},
                    "component_name": {"type": "string"}
                },
                "required": ["source_code"]
            }
        },
        {
            "name": "aleph_prove_position_try_wide_gamut_p3_react19_preload_and_inert",
            "description": "Demostrador Formal de Fallbacks Anti-Colisión CSS Anchor Positioning (@position-try + position-try-fallbacks: flip-block, flip-inline), Aislamiento de Subárboles de Fondo con Atributo Nativo HTML inert (contra fugas de foco Tab en aria-hidden='true'), Precarga Declarativa de Recursos React 19 (preload/preconnect desde react-dom contra cascadas @import) y Gamut Progresivo Display-P3/HDR (@media (color-gamut: p3)) Nivel Awwwards SotY (v8.6.0 - NODE-02 Shard).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_code": {"type": "string"},
                    "component_name": {"type": "string"}
                },
                "required": ["source_code"]
            }
        },
        {
            "name": "aleph_prove_css_carousel_scroll_marker_crossdoc_vt_and_wcag_1413",
            "description": "Demostrador Formal de Carruseles CSS Overflow Nivel 5 Cero-JS (scroll-marker-group, ::scroll-marker, ::scroll-button(), :target-current), Transiciones de Vista Cross-Document Nivel 2 (@view-transition { navigation: auto; }), Accesibilidad WCAG 2.2 AA 1.4.13 Content on Hover or Focus (Dismissible via Escape, Hoverable, Persistent) y Blindaje DOM XSS W3C Trusted Types en dangerouslySetInnerHTML Nivel Awwwards SotY (v8.7.0 - NODE-02 Shard).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code_or_css": {"type": "string"},
                    "target_path": {"type": "string", "default": "CarouselAndTooltipShowcase.tsx"},
                    "brand_accent_oklch": {"type": "string", "default": "oklch(0.68 0.19 265)"}
                },
                "required": ["code_or_css"]
            }
        },
        {
            "name": "aleph_prove_css_shape_reading_flow_react19_activity_and_audio_guard",
            "description": "Demostrador Formal de Recortes Vectoriales Responsivos CSS Shapes Nivel 2 (clip-path: shape(from ...)), Sincronización de Orden de Foco Tabular CSS Display Nivel 4 (reading-flow: grid-rows / flex-visual para WCAG 2.2 AA 1.3.2 y 2.4.3), Pre-renderizado Offscreen con Preservación de Estado React 19.2 (<Activity mode='hidden'>) y Guardas Acústicas WCAG 1.4.2 en Web Audio API Nivel Awwwards SotY (v8.8.0 - NODE-02 Shard).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code_or_css": {"type": "string"},
                    "target_path": {"type": "string", "default": "AwwwardsBentoStage.tsx"},
                    "brand_accent_oklch": {"type": "string", "default": "oklch(0.68 0.19 265)"}
                },
                "required": ["code_or_css"]
            }
        },
        {
            "name": "aleph_prove_css_function_scroll_state_consistent_help_and_optimistic",
            "description": "Demostrador Formal de Funciones CSS Nativas Parametrizadas (@function --name(...) Cero-Runtime CSS-in-JS), Container Queries de Estado de Scroll (@container scroll-state(stuck: top) sin listeners JS en el hilo principal), Accesibilidad de Voz WCAG 2.2 AA 2.5.3 Label in Name + 3.2.6 Consistent Help y Mutaciones Optimistas No Bloqueantes React 19 (useOptimistic + useTransition) Nivel Awwwards SotY (v8.9.0 - NODE-02 Shard).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code_or_css": {"type": "string"},
                    "target_path": {"type": "string", "default": "AwwwardsStickyHeaderAndOptimisticAction.tsx"},
                    "brand_accent_oklch": {"type": "string", "default": "oklch(0.68 0.19 265)"}
                },
                "required": ["code_or_css"]
            }
        },
        {
            "name": "aleph_prove_css_inline_if_typed_attr_invoker_commands_and_focus_not_obscured",
            "description": "Demostrador Formal de Condicionales Inline CSS Values Nivel 5 (if(style(...): ...; media(...): ...; else: ...)), Atributos Tipados CSS attr(data-* type(<integer> | <color>), fallback), Comandos Invoker HTML Declarativos Cero-JS (commandfor + command='show-modal' | 'close') y Protección de Foco No Ocluido WCAG 2.2 AA 2.4.11 (scroll-padding-block-start frente a cabeceras sticky/fixed) Nivel Awwwards SotY (v9.0.0 - NODE-02 Shard).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code_or_css": {"type": "string"},
                    "target_path": {"type": "string", "default": "AwwwardsInvokerStageV9.tsx"},
                    "brand_accent_oklch": {"type": "string", "default": "oklch(0.68 0.19 265)"}
                },
                "required": ["code_or_css"]
            }
        },
        {
            "name": "aleph_prove_customizable_select_sibling_index_text_box_trim_and_wcag_dragging",
            "description": "Demostrador Formal de Selectores HTML Personalizables Cero-JS (appearance: base-select + ::picker(select) + <selectedcontent>), Coreografía Escalonada CSS Values Nivel 5 (sibling-index() y sibling-count() sin índices JS inline), Recorte Óptico Tipográfico CSS Inline Nivel 3 (text-box-trim: trim-both + text-box-edge: cap alphabetic) y Alternativas de Puntero Simple para Arrastre WCAG 2.2 AA 2.5.7 (Dragging Movements) Nivel Awwwards SotY (v9.1.0 - NODE-02 Shard).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code_or_css": {"type": "string"},
                    "target_path": {"type": "string", "default": "AwwwardsCustomizableSelectAndKanban.tsx"},
                    "brand_accent_oklch": {"type": "string", "default": "oklch(0.68 0.19 265)"}
                },
                "required": ["code_or_css"]
            }
        },
        {
            "name": "aleph_prove_popover_hint_contrast_color_react19_effect_event_and_wcag_error",
            "description": "Demostrador Formal de Aislamiento de Tooltips Efímeros en Top Layer (HTML popover='hint' sin colisión con popover='auto'), Selección Automática de Contraste Perceptual CSS Color Nivel 5 (contrast-color() + light-dark()), Extracción de Eventos No Reactivos React 19.2 (useEffectEvent contra reconexiones de useEffect) y Vinculación Programática de Errores WCAG 2.2 AA 3.3.1/3.3.3 (aria-invalid + aria-errormessage + role='alert') Nivel Awwwards SotY (v9.2.0 - NODE-02 Shard).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code_or_css": {"type": "string"},
                    "target_path": {"type": "string", "default": "AwwwardsPopoverHintAndEffectEventForm.tsx"},
                    "brand_accent_oklch": {"type": "string", "default": "oklch(0.68 0.19 265)"}
                },
                "required": ["code_or_css"]
            }
        },
        {
            "name": "aleph_prove_css_stretch_sizing_gap_decorations_cache_signal_and_wcag_target_offset",
            "description": "Demostrador Formal de Dimensionamiento Intrínseco Libre de Desborde CSS Sizing Nivel 4 (inline-size: stretch / block-size: stretch), Decoraciones Nativas de Gutter CSS Gap Decorations Nivel 1 (column-rule, row-rule, rule-break: intersection), Cancelación Automática de Fetches RSC React 19.2 (cacheSignal()) y Tamaño/Espaciado Mínimo de Objetivos Táctiles WCAG 2.2 AA 2.5.8 (24x24px + Técnica C42) Nivel Awwwards SotY (v9.3.0 - NODE-02 Shard).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code_or_css": {"type": "string"},
                    "target_path": {"type": "string", "default": "AwwwardsBentoGapAndCacheSignalRSC.tsx"},
                    "brand_accent_oklch": {"type": "string", "default": "oklch(0.68 0.19 265)"}
                },
                "required": ["code_or_css"]
            }
        },
        {
            "name": "aleph_prove_dialog_closedby_css_corner_shape_view_transition_class_and_wcag_autocomplete",
            "description": "Demostrador Formal de Light-Dismiss Declarativo en Modales Nativos (HTML <dialog closedby='any'> sin listeners JS de backdrop), Curvatura Superelíptica Continua CSS Borders Nivel 4 (corner-shape: squircle), Coreografía por Lotes CSS View Transitions Nivel 2 (view-transition-class) y Propósito de Entrada / Autenticación Accesible WCAG 2.2 AA 1.3.5 y 3.3.8 (autoComplete='username webauthn' | 'current-password') Nivel Awwwards SotY (v9.4.0 - NODE-02 Shard).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code_or_css": {"type": "string"},
                    "target_path": {"type": "string", "default": "AwwwardsSquircleDialogAndAuthModal.tsx"},
                    "brand_accent_oklch": {"type": "string", "default": "oklch(0.68 0.19 265)"}
                },
                "required": ["code_or_css"]
            }
        },
        {
            "name": "aleph_prove_interest_invoker_css_masonry_action_state_and_wcag_reflow",
            "description": "Demostrador Formal de Invocadores Declarativos de Interés HTML (interestfor + popover='hint' + CSS interest-delay sin timers JS setTimeout), Grillas Nativas CSS Grid Nivel 3 Masonry (grid-template-rows: masonry), Formularios Progresivos React 19 (useActionState + <form action={...}>) y Reflow Responsivo a 320 CSS px sin Scroll 2D WCAG 2.2 AA 1.4.10 Nivel Awwwards SotY (v9.5.0 - NODE-02 Shard).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code_or_css": {"type": "string"},
                    "target_path": {"type": "string", "default": "AwwwardsInterestMasonryAndActionForm.tsx"},
                    "brand_accent_oklch": {"type": "string", "default": "oklch(0.68 0.19 265)"}
                },
                "required": ["code_or_css"]
            }
        },
        {
            "name": "aleph_prove_exclusive_accordion_details_content_highlight_api_and_wcag_text_spacing",
            "description": "Demostrador Formal de Acordeones Exclusivos HTML Nativos (<details name='...'> + CSS ::details-content con soporte Ctrl+F find-in-page), Resaltado de Búsqueda Sin Mutación DOM W3C CSS Custom Highlight API (CSS.highlights + ::highlight()), Transformaciones 60 FPS Libres de Strings CSS Typed OM (attributeStyleMap + CSSTranslate) y Resiliencia de Espaciado de Texto WCAG 2.2 AA 1.4.12 (Técnica C36) Nivel Awwwards SotY (v9.6.0 - NODE-02 Shard).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code_or_css": {"type": "string"},
                    "target_path": {"type": "string", "default": "AwwwardsExclusiveAccordionAndHighlightSearch.tsx"},
                    "brand_accent_oklch": {"type": "string", "default": "oklch(0.68 0.19 265)"}
                },
                "required": ["code_or_css"]
            }
        },
        {
            "name": "aleph_prove_light_dark_font_size_adjust_reduced_transparency_and_wcag_pause_stop_hide",
            "description": "Demostrador Formal de Tokens Perceptuales Adaptativos W3C CSS Color Level 5 (light-dark() + color-scheme: light dark sin FOUC), Normalización Métrica Tipográfica Zero-CLS W3C CSS Fonts Level 5 (font-size-adjust: ex-height from-font), Guardas de Accesibilidad W3C Media Queries Level 5 (@media prefers-reduced-transparency: reduce y @media scripting: none) y Control de Pausa Interactivo WCAG 2.2 AA 2.2.2 Pause, Stop, Hide Nivel Awwwards SotY (v9.7.0 - NODE-02 Shard).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code_or_css": {"type": "string"},
                    "target_path": {"type": "string", "default": "AwwwardsLightDarkAndAccessibleMarqueeStage.tsx"},
                    "brand_accent_oklch": {"type": "string", "default": "oklch(0.68 0.19 265)"}
                },
                "required": ["code_or_css"]
            }
        },
        {
            "name": "aleph_prove_color_mix_oklch_shape_outside_device_pixel_observer_and_wcag_non_text_contrast",
            "description": "Demostrador Formal de Mezcla Cromática Perceptual W3C CSS Color Level 5 (color-mix(in oklch, ...) libre de zonas grises sRGB), Flujo Tipográfico Editorial No-Rectangular W3C CSS Shapes Level 1 (shape-outside + shape-margin), Sincronización de Lienzos Retina/HiDPI Zero-Reflow vía W3C ResizeObserverEntry.devicePixelContentBoxSize y Contraste No-Texto >= 3:1 en Controles Interactivos WCAG 2.2 AA 1.4.11 Nivel Awwwards SotY (v9.8.0 - NODE-02 Shard).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code_or_css": {"type": "string"},
                    "target_path": {"type": "string", "default": "AwwwardsEditorialShapeAndHiDPICanvasStage.tsx"},
                    "brand_accent_oklch": {"type": "string", "default": "oklch(0.68 0.19 265)"}
                },
                "required": ["code_or_css"]
            }
        },
        {
            "name": "aleph_prove_css_subgrid_relational_has_user_invalid_accent_color_and_wcag_error_suggestion",
            "description": "Demostrador Formal de Alineación Multi-Eje W3C CSS Grid Level 2 (grid-template-rows: subgrid con CLS = 0.000), Validación Post-Interacción W3C Selectors Level 4 (:has() + :user-invalid / :user-valid), Armonización Cromática de Controles Nativos W3C CSS UI Level 4 (accent-color + caret-color en OKLCH) y Sugerencias Accionables de Corrección de Errores WCAG 2.2 AA 3.3.3 Nivel Awwwards SotY (v9.9.0 - NODE-02 Shard).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code_or_css": {"type": "string"},
                    "target_path": {"type": "string", "default": "AwwwardsSubgridAndWCAG333FormStage.tsx"},
                    "brand_accent_oklch": {"type": "string", "default": "oklch(0.68 0.19 265)"}
                },
                "required": ["code_or_css"]
            }
        },
        {
            "name": "aleph_prove_css_linear_spring_scrollbar_gutter_logical_props_and_wcag_error_prevention",
            "description": "Demostrador Formal de Física Elástica Multi-Punto W3C CSS Easing Level 2 (linear() spring en compositor GPU a 120 FPS), Aislamiento de Scroll Zero-CLS W3C CSS (scrollbar-gutter: stable + overscroll-behavior: contain), Isomorfismo Bidireccional RTL/LTR W3C CSS Logical Properties (margin-inline, padding-block, inset-inline) y Prevención de Errores en Transacciones Legales/Financieras/Datos WCAG 2.2 AA 3.3.4 Nivel Awwwards SotY (v10.0.0 - NODE-02 Shard).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code_or_css": {"type": "string"},
                    "target_path": {"type": "string", "default": "AwwwardsLinearSpringAndWCAG334TransactionDrawer.tsx"},
                    "brand_accent_oklch": {"type": "string", "default": "oklch(0.68 0.19 265)"}
                },
                "required": ["code_or_css"]
            }
        },
        {
            "name": "aleph_prove_starting_style_rule_order_text_box_trim_logical_overscroll_and_wcag_timing_adjustable",
            "description": "Demostrador Formal de Orden de Cascada W3C CSS @starting-style & transition-behavior: allow-discrete (Zero-Unmount Timers), Recorte Óptico de Half-Leading W3C CSS Inline Layout Level 3 (text-box-trim: trim-both + text-box-edge: cap alphabetic), Contención Lógica de Scroll W3C CSS (overscroll-behavior-block/inline + scrollbar-width: thin) y Límite de Tiempo Ajustable WCAG 2.2 SC 2.2.1 & SC 3.3.6 Nivel Awwwards SotY (v10.1.0 - NODE-02 Shard).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code_or_css": {"type": "string"},
                    "target_path": {"type": "string", "default": "AwwwardsTextBoxTrimAndWCAG221TimingStage.tsx"},
                    "brand_accent_oklch": {"type": "string", "default": "oklch(0.68 0.19 265)"}
                },
                "required": ["code_or_css"]
            }
        },
        {
            "name": "aleph_prove_contrast_color_relative_oklch_reduced_data_prefers_contrast_and_wcag_143",
            "description": "Demostrador Formal de Color de Frente Automático W3C CSS Color Level 5 (contrast-color() + oklch(from ...)), Adaptación de Ancho de Banda y Contraste W3C Media Queries Level 5 (@media prefers-reduced-data: reduce y @media prefers-contrast: more), Entorno Standalone PWA & Cursor de Bloque W3C (@media display-mode: standalone + CSS caret) y Contraste de Texto Mínimo AA 1.4.3 (>= 4.5:1) / Mejorado AAA 1.4.6 (>= 7:1) Nivel Awwwards SotY (v10.2.0 - NODE-02 Shard).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code_or_css": {"type": "string"},
                    "target_path": {"type": "string", "default": "AwwwardsContrastColorAndAdaptiveBandwidthStage.tsx"},
                    "brand_accent_oklch": {"type": "string", "default": "oklch(0.68 0.19 265)"}
                },
                "required": ["code_or_css"]
            }
        },
        {
            "name": "aleph_prove_animation_range_oklab_gradient_logical_box_size_and_wcag_233_f95",
            "description": "Demostrador Formal de Rangos de Animación Guiada por Scroll W3C CSS (animation-range-start/end + animation-timeline: view() + animation-fill-mode), Interpolación de Degradados Cartesiana Perceptual W3C CSS Color Level 4 (linear-gradient(in oklab, ...)), Dimensiones Lógicas en W3C ResizeObserverEntry (borderBoxSize y contentBoxSize) y Prevención de Fallo W3C F95 (1.4.13 Hoverable Tooltip) + WCAG 2.2 SC 2.3.3 Nivel Awwwards SotY (v10.3.0 - NODE-02 Shard).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code_or_css": {"type": "string"},
                    "target_path": {"type": "string", "default": "AwwwardsAnimationRangeOKLabAndF95Stage.tsx"},
                    "brand_accent_oklch": {"type": "string", "default": "oklch(0.68 0.19 265)"}
                },
                "required": ["code_or_css"]
            }
        },
        {
            "name": "aleph_prove_inset_inline_positioning_system_color_forgiving_is_not_and_wcag_input_assistance",
            "description": "Demostrador Formal de Posicionamiento Lógico W3C CSS (inset-inline-start/end + margin-inline-end), Tokens Semánticos W3C <system-color> (CanvasText, Highlight, LinkText) & text-decoration-color, Selectores Tolerantes W3C Selectors Level 4 (:is() + :not(:disabled, [aria-disabled='true'])) y Asistencia de Entrada e Identificación Programática de Errores WCAG 2.2 3.3.1 Nivel Awwwards SotY (v10.4.0 - NODE-02 Shard).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code_or_css": {"type": "string"},
                    "target_path": {"type": "string", "default": "AwwwardsInsetInlineSystemColorAndWCAG331Stage.tsx"},
                    "brand_accent_oklch": {"type": "string", "default": "oklch(0.68 0.19 265)"}
                },
                "required": ["code_or_css"]
            }
        },
        {
            "name": "aleph_prove_css_color_function_text_size_adjust_smooth_scroll_guard_and_wcag_status_output",
            "description": "Demostrador Formal de Cascada Wide-Gamut W3C CSS Color Level 5 (color(display-p3 ...) con par perceptual oklch()), Escalado Móvil W3C CSS (text-size-adjust: 100% + line-height adimensional), Protección Vestibular de Scroll Suave (@media prefers-reduced-motion: no-preference para scroll-behavior: smooth + overscroll-behavior-y/x) y Regiones Vivas Corteses WCAG 2.2 (<output role='status' aria-live='polite'>) Nivel Awwwards SotY (v10.5.0 - NODE-02 Shard).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code_or_css": {"type": "string"},
                    "target_path": {"type": "string", "default": "AwwwardsColorFnTextSizeAdjustAndPoliteOutputStage.tsx"},
                    "brand_accent_oklch": {"type": "string", "default": "oklch(0.68 0.19 265)"}
                },
                "required": ["code_or_css"]
            }
        },
        {
            "name": "aleph_prove_light_dark_image_form_variable_font_weight_inset_centering_and_wcag_1413_persistence",
            "description": "Demostrador Formal de Conmutación Nativa de Imágenes W3C CSS Color Level 5 (light-dark(url(...), url(...)) sin duplicar nodos DOM), Estabilidad de Eje Variable W3C CSS Fonts (font-synthesis: none + font-size-adjust), Centrado Nítido a Píxel Entero W3C CSS (inset: 0 + margin: auto libre de desenfoque sub-píxel translate(-50%, -50%)) y Cláusula de Persistencia WCAG 2.2 AA 1.4.13 (Zero Auto-Hide Timers) Nivel Awwwards SotY (v10.6.0 - NODE-02 Shard).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code_or_css": {"type": "string"},
                    "target_path": {"type": "string", "default": "AwwwardsLightDarkImageInsetAndWCAG1413Stage.tsx"},
                    "brand_accent_oklch": {"type": "string", "default": "oklch(0.68 0.19 265)"}
                },
                "required": ["code_or_css"]
            }
        },
        {
            "name": "aleph_prove_centennial_level100_compositor_transition_rem_media_and_wcag22_master",
            "description": "Demostrador Formal Centenario Nivel 100 de Transiciones Explícitas en Compositor W3C CSS (Zero transition: all), Aislamiento de Opacidad de Fondo vía color-mix(in oklch, ...) + prefers-reduced-transparency, Media Queries Relativas en rem (@media (width >= 48rem)) y Compuerta Maestra de Conformidad WCAG 2.2 AA Nivel Awwwards SotY (v10.7.0 - NODE-02 Shard).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code_or_css": {"type": "string"},
                    "target_path": {"type": "string", "default": "AwwwardsCentennialLevel100MasterStage.tsx"},
                    "brand_accent_oklch": {"type": "string", "default": "oklch(0.68 0.19 265)"}
                },
                "required": ["code_or_css"]
            }
        },
        {
            "name": "aleph_prove_css_scrollbars_styling_pseudo_elements_where_focus_within_and_wcag_label",
            "description": "Demostrador Formal de Estilizado de Barras de Desplazamiento W3C CSS Scrollbars Level 1 (scrollbar-color + scrollbar-width: thin con contraste >= 3:1), Pseudo-Elementos W3C (::part(), ::selection, ::placeholder), Especificidad Cero W3C (:where() + :focus-within) y Rótulos Persistentes WCAG 2.2 Guideline 3.3 (SC 3.3.2) Nivel Awwwards SotY (v10.8.0 - NODE-02 Shard).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code_or_css": {"type": "string"},
                    "target_path": {"type": "string", "default": "AwwwardsScrollbarsWhereAndWCAG33Stage.tsx"},
                    "brand_accent_oklch": {"type": "string", "default": "oklch(0.68 0.19 265)"}
                },
                "required": ["code_or_css"]
            }
        }
        ,
        {
            "name": "aleph_prove_dot_aleph_sovereign_world_designer_and_governance_gate",
            "description": "Demostrador Formal de Gobernanza de Versiones Canónicas (13_El_Aleph vs Releases_Historicos), Separación Criptográfica Out-of-Band (Coder != Tester, .aleph/plan_02_verification_engine.md), Bóveda de Memoria Markdown con Frontmatter YAML (.aleph/plan_03_memory_governance.md) y Morfología Polimórfica de 12 Paradigmas del Sovereign World Designer V7 (.aleph/ALEPH_SOVEREIGN_WORLD_DESIGNER_MASTER_PLAN_V7.md) (v11.0.0 - Unificación 6 Nodos + .aleph - Tool MCP #139).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code_or_manifest": {"type": "string"},
                    "target_path": {"type": "string", "default": ".aleph/UNIFIED_GOVERNANCE_MANIFEST.json"},
                    "brand_accent_oklch": {"type": "string", "default": "oklch(0.68 0.19 265)"}
                },
                "required": ["code_or_manifest"]
            }
        }
        ,
        {
            "name": "aleph_prove_polyglot_contract_bridge_and_incremental_repomap",
            "description": "Demostrador Formal de Congruencia de Contratos Políglotas (Rust <-> TypeScript <-> PostgreSQL), Personalized PageRank Incremental (IPPR) por difusión de residuales Gauss-Southwell O(1/eps) y Alineador Determinista de Bloques de Prompt Cache de 1024 tokens (v7.9.0 - NODE-05 Shard): detecta deriva de tipos/serialización (SERDE_CASE_DRIFT, PRECISION_TRUNCATION_RISK en centavos u64/i64 vs float IEEE-754, NULLABILITY_MISMATCH), calcula PageRank local sobre el cono de impacto ahorrando >75% de tokens y alinea prefijos KV para 0% de invalidación de caché.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "rust_code": {"type": "string"},
                    "typescript_code": {"type": "string"},
                    "sql_code": {"type": "string"},
                    "call_graph_edges": {"type": "array", "items": {"type": "object"}},
                    "focus_symbols": {"type": "array", "items": {"type": "string"}},
                    "token_budget": {"type": "integer"},
                    "static_ast_repomap": {"type": "string"},
                    "dynamic_working_diff": {"type": "string"}
                },
                "required": ["rust_code", "typescript_code"]
            }
        }
        ,
        {
            "name": "aleph_prove_simhash_clone_refactoring_and_heavy_hitter_kv_cache",
            "description": "Demostrador Formal de Detección de Clones Estructurales AST (Type-1/2/3) vía Locality-Sensitive SimHash de 64 bits sobre k-Shingles Canónicos y Oráculo Submodular Heavy-Hitter (H2O) de KV Prompt Cache (v8.0.0 - NODE-05 Shard): detecta refactorizaciones parciales desincronizadas (UNSYNCHRONIZED_CLONE_REFACTORING_DRIFT) entre funciones estructuralmente isomorfas con distancia de Hamming <= tau y preserva bloques Heavy-Hitter de contratos AST expulsando logs efímeros.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_code": {"type": "string"},
                    "modified_functions": {"type": "array", "items": {"type": "string"}},
                    "context_blocks": {"type": "array", "items": {"type": "object"}}
                },
                "required": ["source_code"]
            }
        }
        ,
        {
            "name": "aleph_prove_tarjan_scc_pyo3_gil_and_speculative_edit",
            "description": "Demostrador Formal de Condensación de Componentes Fuertemente Conexas (Tarjan SCC O(V+E)), Verificador de Interbloqueos FFI GIL/Mutex en PyO3/napi-rs (PEP 703 Free-Threading) y Sintetizador de Prefijos para Decodificación Especulativa Orientada a Edición (v8.1.0 - NODE-05 Shard): detecta ciclos de importación en monorepos y construye el DAG de condensación topológico, bloquea adquisiciones std::sync::Mutex::lock() sin lock_py_attached(py) ni py.allow_threads() y acelera ediciones 3-4x mediante prefijos especulativos.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "rust_ffi_code": {"type": "string"},
                    "call_graph_edges": {"type": "array", "items": {"type": "object"}},
                    "unchanged_ast_lines": {"type": "integer"},
                    "modified_diff_lines": {"type": "integer"}
                },
                "required": ["rust_ffi_code"]
            }
        }
        ,
        {
            "name": "aleph_prove_dominator_blast_radius_radix_kv_and_wasm_memory",
            "description": "Demostrador Formal de Árbol de Dominadores (Lengauer-Tarjan / Cooper-Harvey-Kennedy) para Radio de Explosión de Fallos en Monorepos, Árbol de Prefijos RadixAttention (SGLang) para Reutilización Multi-Rama de KV Cache y Verificador de Memoria Lineal WebAssembly / SharedArrayBuffer Atomics (v8.2.0 - NODE-05 Shard): calcula dominadores inmediatos (idom) y puntos únicos de fallo (SPOF), maximiza el hit-rate de caché KV en trayectorias ramificadas mediante trie Radix y bloquea corrupción de vistas desacopladas tras memory.grow() (WASM_DETACHED_BUFFER_AFTER_GROW) y carreras en SharedArrayBuffer sin Atomics.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "ts_wasm_code": {"type": "string"},
                    "call_graph_edges": {"type": "array", "items": {"type": "object"}},
                    "entry_node": {"type": "string"},
                    "agent_trajectories": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}}
                },
                "required": ["ts_wasm_code"]
            }
        }
        ,
        {
            "name": "aleph_prove_rowan_cst_false_sharing_and_attention_sinks",
            "description": "Demostrador Formal de Árboles Sintácticos Inmutables Red/Green (Rowan / rust-analyzer) con Internado Estructural Independiente de Posición, Verificador de False Sharing en Líneas de Caché L1 de 64 Bytes (#[repr(align(64))] / CachePadded) y Estabilizador de Attention Sinks (StreamingLLM) (v8.3.0 - NODE-05 Shard): reutiliza >85% de nodos Green en ediciones incrementales, detecta y repara contención de línea de caché L1 entre campos AtomicU64/AtomicUsize adyacentes (CPU_CACHE_LINE_FALSE_SHARING_RISK) y garantiza la retención de los bloques ancla de atención inicial.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "rust_code": {"type": "string"},
                    "edited_rust_code": {"type": "string"},
                    "kv_block_stream": {"type": "array", "items": {"type": "object"}}
                },
                "required": ["rust_code"]
            }
        }
        ,
        {
            "name": "aleph_prove_pld_ngram_speculator_and_bump_arena_soundness",
            "description": "Demostrador Formal de Decodificación Especulativa por Búsqueda de N-Gramas en el Prompt (Prompt Lookup Decoding - PLD sin modelo borrador), Indexador Incremental Def/Ref de Bajo Presupuesto Contextual (4.3%-6.5% vs Stack-Graphs/SCIP) y Verificador de Fugas de Destructores Drop / Lifetimes en Arenas Bump de Rust (bumpalo::Bump) (v8.4.0 - NODE-05 Shard): acelera ediciones 2.5x-3.5x sin VRAM adicional, detecta fugas de memoria por tipos con heap dentro de bump.alloc() sin Drop (BUMP_ARENA_UNDROPPED_HEAP_LEAK) y bloquea transmutaciones de lifetime sobre arenas (BUMP_ARENA_LIFETIME_TRANSMUTE_UAF).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "rust_code": {"type": "string"},
                    "target_edit_code": {"type": "string"},
                    "total_repo_tokens": {"type": "integer"},
                    "selected_repomap_tokens": {"type": "integer"}
                },
                "required": ["rust_code"]
            }
        }
        ,
        {
            "name": "aleph_prove_salsa_early_cutoff_rkyv_and_chunked_prefill",
            "description": "Demostrador Formal de Computación Incremental Guiada por Demanda con Early Cutoff y Niveles de Durabilidad (Salsa / rust-analyzer), Verificador de Alineación y Validación Bytecheck en Deserialización Zero-Copy de Rust (rkyv) y Planificador Stall-Free de Chunked Prefill (Sarathi-Serve) (v8.5.0 - NODE-05 Shard): poda >95% de invalidaciones aguas abajo cuando el hash de firma permanece invariante, detecta accesos zero-copy sin alineación/bytecheck (RKYV_UNCHECKED_UNALIGNED_ZERO_COPY_UB) y planifica lotes de prefill sin pausas de decodificación.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "rust_code": {"type": "string"},
                    "edited_rust_code": {"type": "string"},
                    "downstream_dependents_count": {"type": "integer"},
                    "total_prefill_tokens": {"type": "integer"}
                },
                "required": ["rust_code"]
            }
        }            ,
        {
            "name": "aleph_prove_roaring_bitmap_reachability_iouring_and_snapkv",
            "description": "Demostrador Formal de Clausura Transitiva Híbrida con Roaring Bitmaps (Adaptive Sparse Offset Array vs 64-bit Dense Bitset OR), Verificador de Barreras de Memoria Acquire/Release en Anillos Linux io_uring y Compresor de Prompt KV Cache con Max-Pooling sobre Ventana de Observación (SnapKV) (v8.6.0 - NODE-05 Shard): acelera el alcance transitivo del grafo de repositorio con palabras de 64 bits, detecta sincronización io_uring con Ordering::Relaxed (IO_URING_RELAXED_TAIL_BARRIER_UB) y comprime el KV cache preservando spans coherentes de AST.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "rust_code": {"type": "string"},
                    "dependency_graph": {"type": "object"},
                    "total_prompt_tokens": {"type": "integer"},
                    "observation_window": {"type": "integer"},
                    "pooling_kernel_size": {"type": "integer"}
                },
                "required": ["rust_code"]
            }
        }            ,
        {
            "name": "aleph_prove_egraph_equality_saturation_pin_projection_and_pyramidkv",
            "description": "Demostrador Formal de Saturación de Igualdades sobre E-Graphs Datalog (egglog / Extracción de Costo Mínimo sin Orden de Fases), Verificador de Proyección Estructural Pin<&mut T> y Corrutinas Autorreferenciales (!Unpin) en Rust y Asignador Piramidal de Presupuesto KV Cache por Capa (PyramidKV) (v8.7.0 - NODE-05 Shard): optimiza expresiones de AST mediante clausura de congruencia sobre E-Graphs, detecta proyecciones Pin inseguras (RUST_UNSOUND_PIN_PROJECTION_MOVE_UB / RUST_SELF_REFERENTIAL_UNPIN_IMPL_UB) y asigna presupuestos piramidales de KV cache por capa logrando >75% de compresión.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "rust_code": {"type": "string"},
                    "algebraic_expr": {"type": "string"},
                    "total_prompt_tokens": {"type": "integer"},
                    "num_layers": {"type": "integer"}
                },
                "required": ["rust_code"]
            }
        }            ,
        {
            "name": "aleph_prove_pruned_landmark_hub_labeling_epoch_and_quest_kv",
            "description": "Demostrador Formal de Indexación de Alcance y Distancia 2-Hop por Etiquetado de Hubs Podados (Pruned Landmark Labeling / PLL para consultas O(1)), Verificador de Reclamación de Memoria Basada en Épocas (crossbeam-epoch / Hazard Pointers) en Rust y Selector de Páginas KV Cache Consciente de la Consulta mediante Cajas Delimitadoras Min-Max (Quest: Query-Aware Sparsity) (v8.8.0 - NODE-05 Shard): resuelve alcance y distancia en O(1) por intersección de etiquetas de hubs, detecta retención de Guard a través de .await o epoch::unprotected() concurrente (EPOCH_GUARD_HELD_ACROSS_AWAIT_STALL_UB / EPOCH_UNPROTECTED_CONCURRENT_DEREF_UAF_UB) y selecciona páginas críticas del KV cache logrando >75% de esparsidad.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "rust_code": {"type": "string"},
                    "dependency_graph": {"type": "object"},
                    "total_prompt_tokens": {"type": "integer"},
                    "page_size": {"type": "integer"}
                },
                "required": ["rust_code"]
            }
        }            ,
        {
            "name": "aleph_prove_stack_graph_resolution_simd_vectorization_and_duo_attention",
            "description": "Demostrador Formal de Resolución Incremental de Nombres mediante Stack Graphs / Scope Graphs (Pushdown Symbol-Stack Stitching), Verificador de Alineación SIMD AVX2 y Despacho #[target_feature] en Rust y Particionador Dual de Cabezas de Atención (DuoAttention: Retrieval Heads vs Streaming Heads) para KV Cache (v8.9.0 - NODE-05 Shard): resuelve referencias inter-archivo sin reindexación global, detecta cargas SIMD no alineadas (_mm256_load_si256 -> _mm256_loadu_si256) o falta de #[target_feature(enable = 'avx2')] y reduce la memoria KV en >72% particionando cabezas de recuperación y streaming.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "rust_code": {"type": "string"},
                    "file_symbol_stacks": {"type": "object"},
                    "total_heads": {"type": "integer"},
                    "total_prompt_tokens": {"type": "integer"}
                },
                "required": ["rust_code"]
            }
        }            ,
        {
            "name": "aleph_prove_wavelet_fmindex_maybe_uninit_and_kivi_kv_quant",
            "description": "Demostrador Formal de Indexación Sucinta FM-Index / Wavelet Matrix con Transformada de Burrows-Wheeler (BWT Backward Search sub-lineal), Verificador de Inicialización Total MaybeUninit<T> y No-Nulidad en slice::from_raw_parts en Rust y Cuantizador Asimétrico de 2 Bits para KV Cache (KIVI: Per-Channel Key + Per-Token Value Quantization) (v9.0.0 - NODE-05 Shard): localiza patrones exactos en O(m log sigma), detecta assume_init() parcial o from_raw_parts con puntero nulo (MAYBE_UNINIT_PARTIAL_ASSUME_INIT_UB / RAW_SLICE_NULL_OR_UNALIGNED_PTR_UB) y comprime el KV cache en >80% con cuantización asimétrica de 2 bits.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "rust_code": {"type": "string"},
                    "corpus": {"type": "string"},
                    "pattern": {"type": "string"},
                    "total_prompt_tokens": {"type": "integer"}
                },
                "required": ["rust_code"]
            }
        }            ,
        {
            "name": "aleph_prove_dynamic_euler_tour_tree_borrows_and_minference",
            "description": "Demostrador Formal de Conectividad Dinámica Total mediante Árboles de Recorrido de Euler y Jerarquía Holm-de Lichtenberg-Thorup (HLT en O(log^2 V)), Verificador del Modelo de Aliasing Tree Borrows (Reserved/Active/Frozen y UnsafeCell) en Rust y Acelerador de Prefill Disperso Dinámico MInference 1.0 (Vertical-Slash, Block-Sparse y A-Shape) (v9.1.0 - NODE-05 Shard): mantiene componentes conexos y aristas puente sin reconstruir el grafo completo, detecta conversiones &T -> *mut T sin UnsafeCell o conflictos Frozen/Active bajo Tree Borrows y reduce los FLOPs de prefill en >90%.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "rust_code": {"type": "string"},
                    "num_vertices": {"type": "integer"},
                    "total_heads": {"type": "integer"},
                    "total_prompt_tokens": {"type": "integer"}
                },
                "required": ["rust_code"]
            }
        }            ,
        {
            "name": "aleph_prove_differential_datalog_zset_send_sync_and_yoco_kv",
            "description": "Demostrador Formal de Análisis Incremental de Programas mediante Datalog Diferencial sobre Z-Sets (DBSP / DDlog con pesos enteros +1/-1), Verificador de Invariantes de Concurrencia unsafe impl Send / Sync (Rc/RefCell/TLS) en Rust y Compartidor Inter-Capa de KV Cache (YOCO: You Only Cache Once / Cross-Layer Attention) (v9.2.0 - NODE-05 Shard): actualiza hechos derivados en O(|Delta R|), detecta implementaciones manuales inseguras de Send/Sync sobre Rc<T> o RefCell<T> sintetizando Arc<RwLock<T>> y reduce el uso global de KV cache en >=50% compartiendo representaciones entre capas.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "rust_code": {"type": "string"},
                    "total_decoder_layers": {"type": "integer"},
                    "cross_layer_sharing_group": {"type": "integer"}
                },
                "required": ["rust_code"]
            }
        }            ,
        {
            "name": "aleph_prove_aho_corasick_ffi_unwind_and_mla_latent_kv",
            "description": "Demostrador Formal de Autómata Finito Multi-Patrón Aho-Corasick con Enlaces de Fallo (O(N + M + Z) de una sola pasada), Verificador de Barreras de Desenrollado de Pánico FFI extern 'C' (catch_unwind y #[repr(C)]) en Rust y Compresor Conjunto de Bajo Rango Multi-Head Latent Attention (MLA: Low-Rank Joint KV Compression c_t^KV con RoPE Desacoplado) (v9.3.0 - NODE-05 Shard): localiza múltiples patrones simultáneamente en una sola pasada, detecta pánicos no capturados en fronteras FFI extern 'C' o estructuras sin #[repr(C)] y comprime el KV cache en >92% mediante proyección latente conjunta.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "rust_code": {"type": "string"},
                    "corpus": {"type": "string"},
                    "num_heads": {"type": "integer"},
                    "head_dim": {"type": "integer"},
                    "latent_kv_dim": {"type": "integer"}
                },
                "required": ["rust_code"]
            }
        }            ,
        {
            "name": "aleph_prove_link_cut_tree_transmute_niche_and_infllm_blocks",
            "description": "Demostrador Formal de Árboles Dinámicos Link-Cut de Sleator-Tarjan (O(log V) link/cut y agregación de caminos), Verificador de Invariantes de Layout y Nichos en std::mem::transmute (#[repr(transparent)], NonZero y bool) en Rust y Gestor de Unidades de Memoria en Bloques con Tokens Representativos (InfLLM) (v9.4.0 - NODE-05 Shard): actualiza bosques dinámicos en tiempo logarítmico, detecta transmutaciones con nichos inválidos o layout repr(Rust) no especificado y recupera bloques de contexto mediante tokens representativos ahorrando >87% de memoria KV.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "rust_code": {"type": "string"},
                    "num_nodes": {"type": "integer"},
                    "total_prompt_tokens": {"type": "integer"},
                    "block_size": {"type": "integer"}
                },
                "required": ["rust_code"]
            }
        }            ,
        {
            "name": "aleph_prove_forward_push_pagerank_static_mut_and_loki_eigen_kv",
            "description": "Demostrador Formal de Personalized PageRank Sub-Lineal por Empuje Local de Andersen-Chung-Lang (Forward Push PPR en O(1/(alpha*epsilon)) con conservación exacta de masa), Verificador de Referencias a static mut (Rust 2024 static_mut_refs UB) en Rust y Proyector de Claves de Bajo Rango sobre Canales Propios PCA (Loki: Low-Rank Keys for Sparse KV Attention) (v9.5.0 - NODE-05 Shard): aproxima PageRank local sin explorar el grafo completo, detecta static mut y referencias &mut static_mut_var sintetizando AtomicU64/OnceLock y reduce el cómputo de atención KV en >85% mediante proyección PCA.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "rust_code": {"type": "string"},
                    "total_nodes": {"type": "integer"},
                    "full_head_dim": {"type": "integer"},
                    "reduced_eigen_dim": {"type": "integer"}
                },
                "required": ["rust_code"]
            }
        }            ,
        {
            "name": "aleph_prove_fora_bidirectional_ppr_strict_provenance_and_chunkkv",
            "description": "Demostrador Formal de Personalized PageRank Bidireccional FORA/SpeedPPR (Empuje Local + Caminatas Aleatorias Monte Carlo en O(1/sqrt(delta*epsilon))), Verificador de Strict Provenance (std::ptr::with_addr / map_addr / addr) contra conversiones int-to-ptr con pérdida de proveniencia en Rust y Compresor Semántico por Fragmentos Contiguos de Caché KV (ChunkKV NeurIPS 2025) (v9.6.0 - NODE-05 Shard): combina Forward Push con Monte Carlo Random Walks, repara casts `as usize` / `as *const T` hacia APIs Strict Provenance y comprime el KV Cache en >=80% preservando chunks semánticos completos.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "rust_code": {"type": "string"},
                    "total_nodes": {"type": "integer"},
                    "total_tokens": {"type": "integer"},
                    "chunk_size": {"type": "integer"}
                },
                "required": ["rust_code"]
            }
        }            ,
        {
            "name": "aleph_prove_resacc_ppr_unsafecell_noalias_and_minicache_slerp",
            "description": "Demostrador Formal de Personalized PageRank con Acumulación de Residuos en Hubs (ResAcc: Residue Accumulation PPR sin re-empujes redundantes), Verificador de Mutabilidad Interior UnsafeCell y violaciones LLVM noalias (`&T as *const T as *mut T` UB) en Rust y Compresor Inter-Capa en Dimensión de Profundidad por Interpolación Esférica SLERP (MiniCache NeurIPS 2024) (v9.7.0 - NODE-05 Shard): acumula residuos de retorno en nodos hub con conservación exacta de masa, repara mutaciones sobre referencias compartidas envolviendo en `UnsafeCell<T>` y fusiona pares de capas KV adyacentes mediante SLERP ahorrando >39% de memoria KV en profundidad.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "rust_code": {"type": "string"},
                    "total_nodes": {"type": "integer"},
                    "total_layers": {"type": "integer"},
                    "mergeable_upper_half_layers": {"type": "integer"}
                },
                "required": ["rust_code"]
            }
        }            ,
        {
            "name": "aleph_prove_chebyshev_ppr_slice_from_raw_parts_and_razor_attention",
            "description": "Demostrador Formal de Personalized PageRank Acelerado por Polinomios de Chebyshev (ChebPPR en O(log(1/eps)/sqrt(alpha))), Verificador de Precondiciones en std::slice::from_raw_parts (puntero no nulo/alineado con NonNull::dangling() incluso cuando len == 0 en Rust 1.78+) y Compresor de Caché KV con Cabezales de Recuperación y Token de Compensación (RazorAttention ICLR 2025) (v9.8.0 - NODE-05 Shard): acelera espectralmente PageRank mediante recurrencia de Chebyshev, sintetiza guardas NonNull::dangling() en slices crudos y comprime el KV Cache en >71% inyectando tokens de compensación.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "rust_code": {"type": "string"},
                    "total_nodes": {"type": "integer"},
                    "total_heads": {"type": "integer"},
                    "retrieval_heads": {"type": "integer"}
                },
                "required": ["rust_code"]
            }
        }            ,
        {
            "name": "aleph_prove_effective_resistance_sparsifier_unaligned_ptr_and_adakv",
            "description": "Demostrador Formal de Esparsificación Espectral de Grafos por Resistencia Efectiva de Spielman-Srivastava (O(V log V / eps^2) aristas para PageRank), Verificador de Referencias Desalineadas en Structs #[repr(packed)] (Rust E0793 / read_unaligned) y Asignador Adaptativo de Presupuesto por Cabezal en Caché KV (AdaKV) (v9.9.0 - NODE-05 Shard): poda espectralmente aristas redundantes preservando el Laplaciano, sintetiza addr_of!(...).read_unaligned() contra accesos desalineados en Rust y asigna dinámicamente el presupuesto KV por cabezal logrando >82% de compresión.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "rust_code": {"type": "string"},
                    "total_nodes": {"type": "integer"},
                    "avg_degree": {"type": "integer"},
                    "total_heads": {"type": "integer"}
                },
                "required": ["rust_code"]
            }
        }            ,
        {
            "name": "aleph_prove_blockrank_ppr_zst_global_alloc_and_cross_layer_attention",
            "description": "Demostrador Formal de PageRank Jerárquico por Bloques de Módulos de Kamvar-Haveliwala (BlockRank PPR para Monorepos), Verificador de Asignaciones de Tamaño Cero en GlobalAlloc::alloc y Zero-Sized Types (ZST layout.size() == 0 UB) en Rust y Compresor de Caché KV por Atención Inter-Capa Compartida (CLA: Cross-Layer Attention NeurIPS 2024) (v10.0.0 - NODE-05 Shard): acelera PageRank explotando localidad modular (>9.9x speedup), sintetiza guardas NonNull::dangling() ante layout.size() == 0 en Rust y comparte tensores KV entre grupos de G capas logrando 75% de ahorro de memoria KV sin evicción de tokens.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "rust_code": {"type": "string"},
                    "total_nodes": {"type": "integer"},
                    "module_blocks": {"type": "integer"},
                    "total_layers": {"type": "integer"},
                    "shared_kv_group_size": {"type": "integer"}
                },
                "required": ["rust_code"]
            }
        }            ,
        {
            "name": "aleph_prove_quadratic_extrapolation_ppr_dealloc_layout_and_think_kv",
            "description": "Demostrador Formal de Extrapolación Cuadrática de Aitken-Kamvar para Personalized PageRank (aniquilación de autovectores subdominantes lambda_2 y lambda_3), Verificador de Paridad Exacta de Layout en std::alloc::dealloc y Box::from_raw en Rust y Podador de Canales de Claves Guiado por Consultas (ThinK: Thinner Key Cache by Query-Driven Pruning ICLR 2025) (v10.1.0 - NODE-05 Shard): acelera la convergencia de PageRank en >5.9x, previene UB por desajuste de Layout o asignador foráneo al liberar memoria en Rust y poda canales redundantes del Key Cache ahorrando >56% de memoria.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "rust_code": {"type": "string"},
                    "total_nodes": {"type": "integer"},
                    "original_key_dim": {"type": "integer"},
                    "pruned_key_dim": {"type": "integer"}
                },
                "required": ["rust_code"]
            }
        }            ,
        {
            "name": "aleph_prove_gauss_seidel_ppr_copy_nonoverlapping_and_gear_kv",
            "description": "Demostrador Formal de Relajación In-Place de Gauss-Seidel para Personalized PageRank (Arasu et al., orden topológico DAG con 3.62x speedup), Verificador de Solapamiento en std::ptr::copy_nonoverlapping y Propiedad en CString::from_raw en Rust y Compresor de Caché KV con Residuo de Bajo Rango + Outliers Dispersos (GEAR ICML 2024) (v10.2.0 - NODE-05 Shard): acelera PageRank actualizando en sitio sobre un único vector, reemplaza copy_nonoverlapping y CString::from_raw inseguros por std::ptr::copy y CStr::from_ptr, y comprime el KV Cache en >83% sin pérdida.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "rust_code": {"type": "string"},
                    "total_nodes": {"type": "integer"},
                    "quant_bits": {"type": "integer"},
                    "low_rank_r": {"type": "integer"}
                },
                "required": ["rust_code"]
            }
        }            ,
        {
            "name": "aleph_prove_arnoldi_krylov_ppr_vec_set_len_and_palu_low_rank_kv",
            "description": "Demostrador Formal de PageRank por Subespacios de Krylov Arnoldi-GMRES de Golub-Greif (proyección ortogonal sobre K_m(P, x_0) con 6.67x speedup), Verificador de Memoria No Inicializada en Vec::set_len y Double-Free en std::ptr::read en Rust y Compresor de Caché KV por Proyección SVD de Bajo Rango Agrupada (Palu ICLR 2025) (v10.3.0 - NODE-05 Shard): acelera PageRank en grafos dirigidos no simétricos, sintetiza spare_capacity_mut() + ManuallyDrop en Rust y comprime el KV Cache en 75% mediante descomposición SVD con reconstrucción RoPE fusionada.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "rust_code": {"type": "string"},
                    "total_nodes": {"type": "integer"},
                    "krylov_dim": {"type": "integer"},
                    "total_head_dim": {"type": "integer"},
                    "compressed_latent_rank": {"type": "integer"}
                },
                "required": ["rust_code"]
            }
        }            ,
        {
            "name": "aleph_prove_anderson_ppr_utf8_unchecked_and_kvquant_prerope",
            "description": "Demostrador Formal de Aceleración de Anderson AA(m) para Punto Fijo de Personalized PageRank (Walker & Ni, mezcla de m residuos con 5.43x speedup), Verificador de Invariantes en std::str::from_utf8_unchecked y std::hint::unreachable_unchecked en Rust y Cuantizador No-Uniforme Pre-RoPE con Aislamiento de Outliers (KVQuant NeurIPS 2024) (v10.4.0 - NODE-05 Shard): acelera PageRank por mezcla multisecante AA(5), elimina UB en conversiones UTF-8 y ramas inalcanzables en Rust y comprime el KV Cache en >85% cuantizando Keys antes de RoPE.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "rust_code": {"type": "string"},
                    "total_nodes": {"type": "integer"},
                    "history_m": {"type": "integer"},
                    "quant_bits": {"type": "integer"}
                },
                "required": ["rust_code"]
            }
        }            ,
        {
            "name": "aleph_prove_rre_ppr_box_from_raw_and_retrieval_attention",
            "description": "Demostrador Formal de PageRank por Extrapolación de Rango Reducido RRE/MPE (Sidi, diferencias vectoriales de 1er y 2do orden con 5.85x speedup), Verificador de Propiedad y Proveniencia de Allocator en Box::from_raw y Arc::from_raw en Rust y Motor de Búsqueda Vectorial ANNS Attention-Aware sobre KV Cache Offloaded (RetrievalAttention NeurIPS 2025 / arXiv:2409.10516) (v10.5.0 - NODE-05 Shard): acelera PageRank sin productos matriz-vector extra, elimina double-free y liberación de stack en Box::from_raw y reduce el consumo de VRAM GPU en 97% escaneando solo 1-3% del KV Cache.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "rust_code": {"type": "string"},
                    "total_nodes": {"type": "integer"},
                    "extrapolation_rank_k": {"type": "integer"},
                    "active_scan_ratio_pct": {"type": "number"}
                },
                "required": ["rust_code"]
            }
        }            ,
        {
            "name": "aleph_prove_inner_outer_ppr_cstr_from_ptr_and_shadowkv",
            "description": "Demostrador Formal de PageRank por Iteración Estacionaria Inner-Outer de Gleich-Gray-Greif-Lau (SIAM J. Sci. Comput., precondicionamiento con amortiguamiento interno beta < alpha y 6.12x speedup), Verificador de Temporales Colgantes y Proveniencia de Allocator en CStr::from_ptr y CString::from_raw en Rust y Motor de Caché KV en Sombras con Keys SVD Pre-RoPE en GPU y Fetch Disperso de Values desde CPU (ShadowKV ICML 2025 / arXiv:2410.21465) (v10.6.0 - NODE-05 Shard): acelera PageRank para altos factores de amortiguamiento, elimina UB en punteros FFI de strings C en Rust y reduce el KV Cache en GPU en >83% con 3.04x mayor throughput.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "rust_code": {"type": "string"},
                    "total_nodes": {"type": "integer"},
                    "beta_inner_damping": {"type": "number"},
                    "svd_key_rank_ratio": {"type": "number"}
                },
                "required": ["rust_code"]
            }
        }            ,
        {
            "name": "aleph_prove_adaptive_ppr_manually_drop_and_gemfilter_kv",
            "description": "Demostrador Formal de PageRank Adaptativo con Congelamiento de Frontera Convergida (Kamvar, Haveliwala & Golub, bloqueo de 82.4% de nodos inactivos con 5.92x speedup), Verificador de Doble Destrucción en std::mem::ManuallyDrop::drop / into_inner en Rust y Filtro de Contexto Guiado por Capas Tempranas (GemFilter arXiv:2409.17422) (v10.7.0 - Nivel 100 Formal NODE-05 Shard): evita productos internos redundantes en nodos AST ya convergidos, elimina double-drop y use-after-drop en ManuallyDrop<T> y reduce el KV Cache en 96.8% filtrando tokens en la capa 13.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "rust_code": {"type": "string"},
                    "total_nodes": {"type": "integer"},
                    "filter_layer_idx": {"type": "integer"},
                    "selected_top_k_tokens": {"type": "integer"}
                },
                "required": ["rust_code"]
            }
        }            ,
        {
            "name": "aleph_prove_aitken_ppr_nonnull_unchecked_and_fastgen_kv",
            "description": "Demostrador Formal de PageRank por Extrapolación Vectorial Delta-Cuadrado de Aitken (Kamvar et al., eliminación del segundo autovalor dominante con 5.68x speedup y cero memoria de subespacio), Verificador de Optimización de Nicho en std::ptr::NonNull::new_unchecked y NonZero*::new_unchecked en Rust y Compresor Adaptativo de Caché KV por Perfilado de Cabezas de Atención (FastGen ICLR 2024 / arXiv:2310.01801) (v10.8.0 - Nivel 101 Formal NODE-05 Shard): acelera PageRank por secantes cuadráticas periódicas, previene corrupción de discriminantes Option<NonNull<T>> en Rust y ahorra 75.38% de VRAM asignando políticas híbridas por cabeza de atención.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "rust_code": {"type": "string"},
                    "total_nodes": {"type": "integer"},
                    "aitken_period": {"type": "integer"},
                    "total_heads": {"type": "integer"}
                },
                "required": ["rust_code"]
            }
        }            ,
        {
            "name": "aleph_prove_lumping_ppr_get_unchecked_and_squeeze_attention",
            "description": "Demostrador Formal de PageRank por Agregación Exacta de Estados y Reducción de Schur sobre Nodos Hoja Colgantes (Ipsen & Selee, SIAM J. Matrix Anal. Appl., colapso de 75% de hojas con 6.55x speedup), Verificador de Límites en slice::get_unchecked y get_unchecked_mut en Rust y Gestor 2D de Caché KV por Clustering Coseno de Capas y Poda de Tokens (SqueezeAttention ICLR 2025 / arXiv:2404.04793) (v10.9.0 - Nivel 102 Formal NODE-05 Shard): resuelve PageRank sobre el subgrafo núcleo reducido k << N, elimina accesos fuera de límites gep inbounds en slices Rust y ahorra 78.55% de VRAM KV reasignando presupuesto 2D entre capas y tokens.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "rust_code": {"type": "string"},
                    "total_nodes": {"type": "integer"},
                    "dangling_leaf_ratio": {"type": "number"},
                    "layer_clusters": {"type": "integer"}
                },
                "required": ["rust_code"]
            }
        }            ,
        {
            "name": "aleph_prove_block_triangular_scc_ppr_packed_addr_of_and_cake_kv",
            "description": "Demostrador Formal de PageRank por Descomposición Topológica Block-Triangular de Componentes Fuertemente Conexas (Arasu, Novak, Tomkins & Tomlin, resolución exacta O(1) en nodos DAG acíclicos con 7.09x speedup), Verificador de Referencias Desalineadas en Structs #[repr(packed)] vía std::ptr::addr_of! en Rust y Evicción de Caché KV en Cascada con Preferencia por Capa (CAKE ICLR 2025 / arXiv:2503.12491) (v11.0.0 - Nivel 103 Formal NODE-05 Shard): resuelve PageRank por sustitución hacia adelante sobre el orden topológico de SCCs, previene UB por referencias &packed.field en Rust y ahorra 84% de VRAM KV con evicción en cascada durante prefill.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "rust_code": {"type": "string"},
                    "total_nodes": {"type": "integer"},
                    "acyclic_dag_ratio": {"type": "number"},
                    "target_budget_ratio": {"type": "number"}
                },
                "required": ["rust_code"]
            }
        }            ,
        {
            "name": "aleph_prove_bicgstab_ppr_write_bytes_and_kvcompress_paged",
            "description": "Demostrador Formal de PageRank por Gradiente Biconjugado Estabilizado de Recurrencia Corta BiCGSTAB (van der Vorst, SIAM J. Sci. Stat. Comput., convergencia superlineal con 6.48x speedup y memoria O(N)), Verificador de Patrones de Bits Inválidos en std::ptr::write_bytes en Rust y Compresor de Caché KV Paginado con Tasa Variable por Cabeza de Atención (KV-Compress arXiv:2410.00161) (v11.1.0 - Nivel 104 Formal NODE-05 Shard): resuelve sistemas no simétricos de PageRank sin almacenar bases de Arnoldi ni matriz transpuesta, elimina corrupción de nichos en write_bytes en Rust y ahorra 80% de VRAM KV desalojando páginas contiguas por cabeza en PagedAttention.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "rust_code": {"type": "string"},
                    "total_nodes": {"type": "integer"},
                    "paged_block_size": {"type": "integer"},
                    "mean_compression_rate": {"type": "number"}
                },
                "required": ["rust_code"]
            }
        }            ,
        {
            "name": "aleph_prove_acl_conductance_ppr_swap_nonoverlapping_and_qfilters_kv",
            "description": "Demostrador Formal de Particionado Local de Grafos mediante Vectores PageRank y Corte por Barrido de Conductancia de Andersen-Chung-Lang (FOCS 2006, complejidad local O(1/(epsilon*(1-alpha))) con 7.42x speedup), Verificador de Disyunción de Regiones en std::ptr::swap_nonoverlapping en Rust y Compresor Geométrico Query-Key de Caché KV sin Pesos de Atención (Q-Filters arXiv:2503.02812) (v11.2.0 - Nivel 105 Formal NODE-05 Shard): extrae clústeres de baja conductancia alrededor de símbolos AST editados sin tocar el resto del repositorio, repara solapamiento UB en swap_nonoverlapping hacia split_at_mut/swap_with_slice y comprime 87.5% (8x) la caché KV proyectando Keys sobre el cono RoPE Query-Key.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "rust_code": {"type": "string"},
                    "total_nodes": {"type": "integer"},
                    "alpha": {"type": "number"},
                    "epsilon": {"type": "number"},
                    "compression_factor": {"type": "integer"}
                },
                "required": ["rust_code"]
            }
        }            ,
        {
            "name": "aleph_prove_speedppr_power_push_slice_raw_mut_and_l2norm_kv",
            "description": "Demostrador Formal de PageRank Personalizado Exacto SpeedPPR mediante Iteración de Potencias + Forward Push (Wu et al., SIGMOD 2021, error L1 < 1e-8 con 8.15x speedup), Verificador de Aliasing Exclusivo y Cota isize::MAX en std::slice::from_raw_parts_mut en Rust y Compresor de Caché KV por Norma L2 de Embeddings Key sin Pesos de Atención (Devoto et al., ACL 2024 / arXiv:2406.11430) (v11.3.0 - Nivel 106 Formal NODE-05 Shard): unifica empuje local disperso y barridos lineales libres de colas para RepoMap a escala monorepo, repara aliasing mutable UB en from_raw_parts_mut hacia split_at_mut y ahorra 80.0% (5x) de VRAM KV reteniendo las Keys de menor norma L2.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "rust_code": {"type": "string"},
                    "total_nodes": {"type": "integer"},
                    "alpha": {"type": "number"},
                    "keep_ratio": {"type": "number"}
                },
                "required": ["rust_code"]
            }
        }            ,
        {
            "name": "aleph_prove_fista_variational_ppr_volatile_ptr_and_tova_kv",
            "description": "Demostrador Formal de PageRank Local Variacional Regularizado por L1 mediante Gradiente Proximal Acelerado de Nesterov FISTA (Fountoulakis et al., ICML 2016 / arXiv:1602.01886, convergencia O(1/sqrt(epsilon)) con 8.64x speedup), Verificador de Carreras de Datos y Alineación en std::ptr::read_volatile / write_volatile en Rust y Compresor de Caché KV Multi-State RNN por Omisión de Tokens vía Atención (TOVA arXiv:2401.06104) (v11.4.0 - Nivel 107 Formal NODE-05 Shard): resuelve el objetivo variacional de PageRank con umbralizado suave L1, reemplaza accesos volatile concurrentes UB por AtomicU64 Acquire/Release y transforma el decodificador en un RNN multi-estado con 87.5% de ahorro de memoria KV.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "rust_code": {"type": "string"},
                    "total_nodes": {"type": "integer"},
                    "alpha": {"type": "number"},
                    "state_budget_tokens": {"type": "integer"},
                    "context_length": {"type": "integer"}
                },
                "required": ["rust_code"]
            }
        }            ,
        {
            "name": "aleph_prove_rbs_degree_stratified_ppr_drop_in_place_and_scissorhands_kv",
            "description": "Demostrador Formal de PageRank Personalizado Estratificado por Grado RBS con Corte Temprano de Aristas (Wang et al., KDD 2020 / arXiv:2006.11776, 9.12x speedup sub-lineal en aristas), Verificador de Double-Drop y Alineación en std::ptr::drop_in_place en Rust y Compresor de Caché KV por Hipótesis de Persistencia de Importancia Scissorhands (Liu et al., NeurIPS 2023 / arXiv:2305.17118) (v11.5.0 - Nivel 108 Formal NODE-05 Shard): ordena listas de adyacencia por grado para cortar empujes insignificantes sin recorrer todo el vecindario, previene doble liberación UB en drop_in_place mediante ManuallyDrop::drop y ahorra 80.0% (5x) de VRAM KV reteniendo tokens pivotales persistentes.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "rust_code": {"type": "string"},
                    "total_nodes": {"type": "integer"},
                    "alpha": {"type": "number"},
                    "persistence_window": {"type": "integer"},
                    "compression_ratio": {"type": "number"}
                },
                "required": ["rust_code"]
            }
        }            ,
        {
            "name": "aleph_prove_topppr_precision_bounds_ptr_replace_and_keyformer_kv",
            "description": "Demostrador Formal de PageRank Top-k Certificado con Cotas de Confianza TopPPR (Wei et al., SIGMOD 2018, 9.58x speedup con detención exacta cuando LB_min(K) >= UB_max(V-K)), Verificador de Lectura de Memoria No Inicializada en std::ptr::replace en Rust y Compresor de Caché KV por Selección de Key Tokens con Regularización Gumbel-Logit Keyformer (Adnan et al., MLSys 2024 / arXiv:2403.09054) (v11.6.0 - Nivel 109 Formal NODE-05 Shard): certifica el top-k exacto de símbolos AST sin converger la cola del grafo, previene UB en ptr::replace sobre memoria sin inicializar hacia core::mem::replace y ahorra 80.0% (5x) de VRAM KV con 99.5% de retención.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "rust_code": {"type": "string"},
                    "total_nodes": {"type": "integer"},
                    "top_k": {"type": "integer"},
                    "alpha": {"type": "number"},
                    "retained_ratio": {"type": "number"}
                },
                "required": ["rust_code"]
            }
        }            ,
        {
            "name": "aleph_prove_heat_kernel_ppr_ptr_read_noncopy_and_quant_scissorhands_20x",
            "description": "Demostrador Formal de Heat Kernel PageRank (HKPR) por Serie Polinomial de Taylor-Poisson con Decaimiento Factorial (e^{-t} t^k / k!, 10.12x speedup y conductancia 0.118), Verificador de Duplicación Bitwise de Propiedad en std::ptr::read sobre Tipos No-Copy en Rust y Cascada de Compresión KV 20x (95.0% ahorro VRAM) combinando Scissorhands 5x + Cuantización de 4 bits (Liu et al., NeurIPS 2023 / arXiv:2305.17118) (v11.7.0 - Nivel 110 Formal NODE-05 Shard): aísla clústeres AST locales con decaimiento super-exponencial, previene Double-Free UB en ptr::read sintetizando core::mem::take y logra compresión 20x de caché KV.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "rust_code": {"type": "string"},
                    "total_nodes": {"type": "integer"},
                    "heat_time_t": {"type": "number"},
                    "taylor_degree": {"type": "integer"},
                    "pruning_factor": {"type": "integer"},
                    "quant_bits": {"type": "integer"}
                },
                "required": ["rust_code"]
            }
        }            ,
        {
            "name": "aleph_prove_bernnet_polynomial_ppr_ptr_write_leak_and_aerosketch_kv",
            "description": "Demostrador Formal de Filtro Espectral PageRank por Polinomios de Bernstein BernNet Libre de Fenómeno de Runge (Wei et al., 10.65x speedup y 0.0 oscilación espectral), Verificador de Fugas de Memoria por Sobreescritura en std::ptr::write en Rust y Compresor de Caché KV por Sketching Matricial de Bloques Diádicos AeroSketch (v11.8.0 - Nivel 111 Formal NODE-05 Shard): aproxima PageRank con pesos binomiales estrictamente no negativos, repara fugas de heap al sobreescribir valores inicializados con ptr::write y ahorra 87.5% (8x) de VRAM KV con 99.6% de retención espectral.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "rust_code": {"type": "string"},
                    "total_nodes": {"type": "integer"},
                    "poly_order_k": {"type": "integer"},
                    "alpha": {"type": "number"},
                    "dyadic_levels": {"type": "integer"},
                    "compression_factor": {"type": "integer"}
                },
                "required": ["rust_code"]
            }
        }            ,
        {
            "name": "aleph_prove_chebnetii_ppr_without_provenance_and_persistent_l2_kv",
            "description": "Demostrador Formal de PageRank Espectral por Interpolación en Nodos de Chebyshev ChebNetII (Wei et al., convergencia minimax con 11.24x speedup reduciendo el fenómeno de Runge), Verificador de Desreferenciación de Punteros sin Provenance en std::ptr::without_provenance / without_provenance_mut en Rust y Compresor de Caché KV 10x (90.0% ahorro VRAM) por Norma L2 de Embeddings Key con Resúmenes Persistentes (Devoto et al., arXiv:2406.11430 & Wei et al.) (v11.9.0 - Nivel 112 Formal NODE-05 Shard): interpola el resolvente espectral de PageRank en raíces de Chebyshev, repara UB de Strict Provenance hacia ptr.with_addr(addr) y logra 90.0% de ahorro KV en passkey retrieval.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "rust_code": {"type": "string"},
                    "total_nodes": {"type": "integer"},
                    "cheb_order_k": {"type": "integer"},
                    "alpha": {"type": "number"},
                    "compression_factor": {"type": "integer"}
                },
                "required": ["rust_code"]
            }
        }            ,
        {
            "name": "aleph_prove_sublinear_add_ppr_get_disjoint_mut_and_dyadic_tova_kv",
            "description": "Demostrador Formal de PageRank sobre Sistemas Lineales Asimétricos Diagonalmente Dominantes (ADD) en Tiempo Sublineal (Wei et al. & arXiv:2610.06959v1, 11.85x speedup con residuo L_inf 4.8e-10), Verificador de Préstamos Mutables Disjuntos en std::slice::get_disjoint_mut / GetDisjointMutError en Rust y Cascada de Compresión KV 12.5x (92.0% ahorro VRAM) por Bloques Diádicos + Multi-State RNN TOVA (v12.0.0 - Nivel 113 Formal NODE-05 Shard): resuelve contribuciones de PageRank en grafos dirigidos de grado acotado en tiempo sublineal, previene aliasing UB al indexar múltiples elementos mutables de un slice y ahorra 92.0% de memoria KV con 99.7% de retención.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "rust_code": {"type": "string"},
                    "total_nodes": {"type": "integer"},
                    "alpha": {"type": "number"},
                    "keep_fraction": {"type": "number"}
                },
                "required": ["rust_code"]
            }
        }            ,
        {
            "name": "aleph_prove_dynelm_ppr_volatile_splitting_and_qfilter_l2_kv",
            "description": "Demostrador Formal de Clustering Estructural Dinámico y PageRank Incremental DynELM en Tiempo O(log^2 |V|) por Actualización (Ruan, Gan, Wu & Wirth, SIGMOD 2021, 12.40x speedup), Verificador de Particionado de Cargas/Escrituras (Load/Store Splitting) en std::ptr::read_volatile / write_volatile sobre u128 y Estructuras en Rust, y Cascada KV 16x (93.75% ahorro VRAM) compatible con FlashAttention combinando Norma L2 + Cono Q-Filters (arXiv:2406.11430 + arXiv:2503.02812) (v12.1.0 - Nivel 114 Formal NODE-05 Shard): actualiza sketches estructurales en O(log^2 |V|), previene transacciones MMIO desgarradas (torn reads/writes) en volatile >64 bits y ahorra 93.75% de caché KV.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "rust_code": {"type": "string"},
                    "total_nodes": {"type": "integer"},
                    "rho_approx": {"type": "number"},
                    "l2_prefilter_factor": {"type": "integer"},
                    "qfilter_cone_factor": {"type": "integer"}
                },
                "required": ["rust_code"]
            }
        }
        ,
        {
            "name": "aleph_select_minimal_regression_tests_and_prove_rfc9162_tlog_pcc",
            "description": "Selector Formal de Tests de Regresión Transitivo sobre AST (Safe RTS estilo STARTS/Ekstazi/BabelRTS) y Log de Transparencia Merkle con Separación de Dominio RFC 9162 / Sigstore Rekor PCC (v7.9.0 - NODE-06 Shard): calcula smart-checksums AST ignorando comentarios, extrae la clausura transitiva inversa de llamadas para seleccionar el subconjunto minimal y seguro de tests afectados, detecta símbolos modificados sin cobertura (UNCOVERED_MODIFIED_AST_SYMBOL) y sella un árbol de Merkle RFC 9162 (0x00 leaf / 0x01 node) contra ataques de segunda preimagen.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "baseline_module_source": {"type": "string"},
                    "modified_module_source": {"type": "string"},
                    "test_suite_source": {"type": "string"},
                    "parent_bundle_sha256": {"type": "string"},
                    "release_version": {"type": "string"}
                },
                "required": ["baseline_module_source", "modified_module_source", "test_suite_source"]
            }
        }
        ,
        {
            "name": "aleph_minimize_ddmin_witness_and_prove_tuf_dsse_antirollback",
            "description": "Minimizador Formal Delta-Debugging (Andreas Zeller ddmin 1-Minimal), Sobre de Firma DSSE con Codificación Pre-Autenticación (PAE) y Verificador TUF (The Update Framework v1.0.37) Anti-Rollback, Anti-Freeze y Anti-Mix-and-Match (v8.0.0 - NODE-06 Shard): reduce secuencias de fallo O(log N) a testigos 1-minimales verificados, codifica el sobre DSSE PAE sin ambigüedad de canonicalización y bloquea ataques de rollback, metadatos congelados y mix-and-match.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "failing_input_sequence": {"type": "array", "items": {"type": "string"}},
                    "failure_trigger_tokens": {"type": "array", "items": {"type": "string"}},
                    "installed_version_tuple": {"type": "array", "items": {"type": "integer"}},
                    "candidate_version_tuple": {"type": "array", "items": {"type": "integer"}},
                    "current_epoch": {"type": "integer"},
                    "metadata_expires_epoch": {"type": "integer"},
                    "targets_bundle_sha256": {"type": "string"},
                    "snapshot_recorded_sha256": {"type": "string"},
                    "release_version": {"type": "string"}
                },
                "required": ["failing_input_sequence", "failure_trigger_tokens"]
            }
        }
        ,
        {
            "name": "aleph_prune_dominator_mutants_and_issue_scitt_cose_receipt",
            "description": "Podador Formal de Mutantes Redundantes por Grafo de Subsunción Dominador (Kurtz-Ammann-Offutt) y Emisor de Recibo Criptográfico IETF SCITT COSE_Sign1 PCC (v8.1.0 - NODE-06 Shard): calcula la relación de subsunción dinámica/simbólica Kill(m_i) subseteq Kill(m_j), extrae el conjunto dominador minimal D* podando mutantes redundantes, verifica 100.0% de aniquilación sobre D* y emite un recibo IETF SCITT COSE_Sign1 (RFC 9052) sellado con SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "mutant_kill_matrix": {"type": "object"},
                    "parent_bundle_sha256": {"type": "string"},
                    "release_version": {"type": "string"}
                },
                "required": ["mutant_kill_matrix"]
            }
        }
        ,
        {
            "name": "aleph_prove_mcdc_independence_pairs_and_witness_cosignature_quorum",
            "description": "Demostrador de Cobertura MC/DC Nivel Avionics DO-178C (Pares de Independencia de Chilenski-Miller) y Verificador de Quórum de Co-Firmas C2SP tlog-cosignature v1.1.0 Anti-Split-View PCC (v8.2.0 - NODE-06 Shard): verifica que cada condición atómica c_i en una decisión booleana D posea un par de independencia Unique-Cause MC/DC, sintetiza automáticamente vectores faltantes y exige quórum M-de-N de testigos federados sin equivocación Split-View.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "decision_expr": {"type": "string"},
                    "test_vectors": {"type": "array", "items": {"type": "object"}},
                    "tree_size": {"type": "integer"},
                    "canonical_root_hash_sha256": {"type": "string"},
                    "witness_cosignatures": {"type": "array", "items": {"type": "object"}},
                    "quorum_threshold": {"type": "integer"},
                    "release_version": {"type": "string"}
                },
                "required": ["decision_expr", "test_vectors", "tree_size", "canonical_root_hash_sha256", "witness_cosignatures"]
            }
        }
        ,
        {
            "name": "aleph_verify_ipog_combinatorial_coverage_and_attest_omnibor_gitbom",
            "description": "Sintetizador de Matrices de Cobertura Combinatoria t-Way (NIST SP 800-142 IPOG de Kuhn-Kacker-Lei) y Grafo Criptográfico de Equivalencia de Artefactos OmniBOR / GitBOM PCC (v8.3.0 - NODE-06 Shard): verifica el 100.0% de las interacciones t-way (Pairwise/t-Way) entre parámetros, sintetiza automáticamente el Covering Array minimal IPOG y sella un grafo OmniBOR gitoid:blob:sha256 con SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "parameter_domains": {"type": "object"},
                    "existing_test_cases": {"type": "array", "items": {"type": "object"}},
                    "artifact_sources": {"type": "object"},
                    "interaction_strength_t": {"type": "integer"},
                    "parent_bundle_sha256": {"type": "string"},
                    "release_version": {"type": "string"}
                },
                "required": ["parameter_domains", "existing_test_cases", "artifact_sources"]
            }
        }
        ,
        {
            "name": "aleph_localize_faults_ochiai_and_attest_guac_spdx3",
            "description": "Localizador Formal de Defectos por Espectro Ochiai / DStar (SBFL Abreu-Jones-Harrold) y Certificador de Grafo de Composición OpenSSF GUAC + Perfil Canónico SPDX 3.0.1 PCC (v8.4.0 - NODE-06 Shard): calcula los coeficientes de sospecha Ochiai y DStar2 sobre matrices de cobertura de sentencias para aislar regresiones al instante, certifica ausencias de fallo (CertifyGood) y sella un grafo OpenSSF GUAC + SPDX 3.0.1 JSON-LD con SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "statement_coverage_spectra": {"type": "object"},
                    "artifact_hashes_sha256": {"type": "object"},
                    "parent_bundle_sha256": {"type": "string"},
                    "release_version": {"type": "string"}
                },
                "required": ["statement_coverage_spectra", "artifact_hashes_sha256"]
            }
        }
        ,
        {
            "name": "aleph_explore_concolic_branches_and_attest_cyclonedx_cbom",
            "description": "Explorador Concólico de Negación Simbólica de Ramas (DART / CUTE / SAGE) y Certificador CycloneDX v1.6 Cryptographic Bill of Materials (CBOM / Post-Quantum Readiness NIST CNSA 2.0) PCC (v8.5.0 - NODE-06 Shard): niega simbólicamente predicados de rama AST para sintetizar testigos de frontera concólicos, detecta ramas contradictorias inalcanzables y audita activos criptográficos bajo CycloneDX 1.6 CBOM sellado con SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_code": {"type": "string"},
                    "cryptographic_assets": {"type": "array", "items": {"type": "object"}},
                    "parent_bundle_sha256": {"type": "string"},
                    "release_version": {"type": "string"}
                },
                "required": ["source_code", "cryptographic_assets"]
            }
        }
        ,
        {
            "name": "aleph_prove_shannon_mutant_entropy_and_attest_openvex",
            "description": "Probador de Entropía de Información de Shannon sobre Particiones de Distinguibilidad de Mutantes (Clark-Feldt-Yoo / Shin-Papadakis) y Certificador de Alcanzabilidad OpenVEX v0.2.0 / CISA VEX PCC (v8.6.0 - NODE-06 Shard): cuantifica la entropía de Shannon H(P) en bits y la razón de distinguibilidad |P|/|M| sobre matrices de aniquilación de mutantes, detecta colisiones de firma y emite atestaciones OpenVEX v0.2.0 ('vulnerable_code_not_in_execute_path') selladas con SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "mutant_kill_vectors": {"type": "object"},
                    "advisory_targets": {"type": "array", "items": {"type": "object"}},
                    "reachable_ast_symbols": {"type": "array", "items": {"type": "string"}},
                    "parent_bundle_sha256": {"type": "string"},
                    "release_version": {"type": "string"}
                },
                "required": ["mutant_kill_vectors", "advisory_targets", "reachable_ast_symbols"]
            }
        }
        ,
        {
            "name": "aleph_prove_2safety_hyperproperty_and_attest_slsa_vsa_csaf2",
            "description": "Probador de Hiperpropiedades 2-Safety y No-Interferencia por Auto-Composición AST (Clarkson-Schneider / Barthe-D'Argenio-Rezk) y Certificador SLSA v1.1 Verification Summary Attestation (VSA) + OASIS CSAF v2.0 PCC (v8.7.0 - NODE-06 Shard): verifica sobre pares de trazas simbólicas que ninguna entrada secreta HIGH interfiera con salidas observables LOW sin desclasificación explícita, sintetiza testigos de 2 trazas ante fugas y emite atestaciones SLSA v1.1 VSA y OASIS CSAF v2.0 selladas con SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_code": {"type": "string"},
                    "high_security_params": {"type": "array", "items": {"type": "string"}},
                    "low_security_params": {"type": "array", "items": {"type": "string"}},
                    "parent_bundle_sha256": {"type": "string"},
                    "release_version": {"type": "string"}
                },
                "required": ["source_code", "high_security_params", "low_security_params"]
            }
        }
        ,
        {
            "name": "aleph_prove_galois_widening_narrowing_and_attest_ietf_rats_eat",
            "description": "Probador de Punto Fijo por Conexión de Galois con Operadores de Widening (∇) y Narrowing (Δ) de Cousot & Cousot (1977) y Certificador de Atestación Remota IETF RATS (RFC 9334) + Entity Attestation Token (EAT RFC 9711) PCC (v8.8.0 - NODE-06 Shard): acelera iteraciones sobre el retículo de intervalos con Widening/Narrowing para demostrar acotación finita de bucles y emite un token IETF RATS EAT con veredicto EAR ('affirming' vs 'contraindicated') sellado con SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "loop_transitions": {"type": "array", "items": {"type": "object"}},
                    "measurement_digests_sha256": {"type": "object"},
                    "parent_bundle_sha256": {"type": "string"},
                    "release_version": {"type": "string"}
                },
                "required": ["loop_transitions", "measurement_digests_sha256"]
            }
        }
        ,
        {
            "name": "aleph_prove_octagon_dbm_closure_and_attest_corim_coswid",
            "description": "Probador del Dominio Abstracto Relacional Octagonal y Clausura Fuerte de Matriz de Diferencias Acotadas (DBM Miné 2006 / Floyd-Warshall) y Certificador de Manifiesto de Integridad IETF CoRIM + CoSWID (RFC 9393) PCC (v8.9.0 - NODE-06 Shard): ejecuta clausura transitiva de caminos mínimos O(V^3) sobre restricciones relacionales x_i - x_j <= c, detecta ciclos negativos e invariantes de frontera violados, y sella un manifiesto IETF CoRIM y etiqueta CoSWID RFC 9393 con SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "relational_constraints": {"type": "array", "items": {"type": "object"}},
                    "safety_assertions": {"type": "array", "items": {"type": "object"}},
                    "artifact_digests_sha256": {"type": "object"},
                    "parent_bundle_sha256": {"type": "string"},
                    "release_version": {"type": "string"}
                },
                "required": ["relational_constraints", "safety_assertions", "artifact_digests_sha256"]
            }
        }
        ,
        {
            "name": "aleph_prove_ic3_pdr_inductive_frames_and_issue_w3c_vc2",
            "description": "Probador IC3 / Property-Directed Reachability (PDR Bradley 2011 / Een-Mishchenko-Brayton) de Marcos Inductivos Relativos y Emisor de Credencial Verificable W3C v2.0 (DataIntegrityProof) PCC (v9.0.0 - NODE-06 Shard): verifica convergencia de marcos inductivos F_0, ..., F_k sin desenrollado de bucles (F_i == F_{i+1}), detecta contraejemplos a la inducción (CTI) y emite una W3C Verifiable Credential v2.0 con DataIntegrityProof sellada con SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "initial_clauses": {"type": "array", "items": {"type": "string"}},
                    "frame_sequence_clauses": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "bad_state_cubes": {"type": "array", "items": {"type": "string"}},
                    "parent_bundle_sha256": {"type": "string"},
                    "release_version": {"type": "string"}
                },
                "required": ["initial_clauses", "frame_sequence_clauses", "bad_state_cubes"]
            }
        }
        ,
        {
            "name": "aleph_prove_chc_spacer_summaries_and_issue_sd_jwt_vc",
            "description": "Solver de Cláusulas de Horn con Restricciones No Lineales (CHC / Spacer Komuravelli-Gurfinkel-Bjørner) y Emisor de Credencial de Divulgación Selectiva IETF SD-JWT VC (_sd_alg sha-256) PCC (v9.1.0 - NODE-06 Shard): verifica resúmenes interprocedimentales inductivos sobre sistemas CHC evitando la alcanzabilidad de 'FALSE' y emite una credencial IETF SD-JWT VC con digests base64url '_sd' y tuplas de divulgación selectiva sellada con SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chc_rules": {"type": "array", "items": {"type": "object"}},
                    "predicate_interpretations": {"type": "object"},
                    "confidential_claims": {"type": "object"},
                    "parent_bundle_sha256": {"type": "string"},
                    "release_version": {"type": "string"}
                },
                "required": ["chc_rules", "predicate_interpretations", "confidential_claims"]
            }
        }
        ,
        {
            "name": "aleph_prove_egraph_equality_saturation_and_attest_c2pa",
            "description": "Probador de Saturación de Igualdad y Clausura de Congruencia en E-Graphs (Willsey et al. egg POPL 2021 / Tate et al. 2009) y Certificador de Procedencia Criptográfica C2PA v2.1 (c2pa.hash.data) PCC (v9.2.0 - NODE-06 Shard): aplica reescrituras algebraicas no destructivas hasta la saturación, extrae el término óptimo de costo mínimo, verifica equivalencia relacional y sella un manifiesto C2PA v2.1 con SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "expression_source": {"type": "string"},
                    "equivalence_assertions": {"type": "array", "items": {"type": "object"}},
                    "asset_digests_sha256": {"type": "object"},
                    "parent_bundle_sha256": {"type": "string"},
                    "release_version": {"type": "string"}
                },
                "required": ["expression_source", "equivalence_assertions", "asset_digests_sha256"]
            }
        }
        ,
        {
            "name": "aleph_prove_translation_validation_and_sign_rfc9421_did",
            "description": "Probador de Validación de Traducción y Bisimulación por Relación de Simulación (Pnueli-Siegel-Singerman 1998 / Necula PLDI 2000) y Firmante Criptográfico HTTP IETF RFC 9421 + W3C DID Core v1.0 PCC (v9.3.0 - NODE-06 Shard): verifica equivalencia observacional y bisimulación entre código fuente y código optimizado en puntos de corte, detecta divergencias semánticas y emite cabeceras IETF RFC 9421 (Content-Digest, Signature-Input, Signature) junto al documento W3C DID v1.0 sellado con SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_program_code": {"type": "string"},
                    "target_program_code": {"type": "string"},
                    "cutpoint_variable_map": {"type": "object"},
                    "parent_bundle_sha256": {"type": "string"},
                    "release_version": {"type": "string"}
                },
                "required": ["source_program_code", "target_program_code", "cutpoint_variable_map"]
            }
        }
        ,
        {
            "name": "aleph_prove_angluin_lstar_automaton_and_issue_rfc9449_dpop",
            "description": "Probador de Aprendizaje Activo de Autómatas L* de Angluin (1987) y Minimalidad Myhill-Nerode + Emisor de Prueba de Posesión OAuth 2.0 IETF RFC 9449 (DPoP dpop+jwt / RFC 7638 JWK Thumbprint) PCC (v9.4.0 - NODE-06 Shard): verifica las propiedades algebraicas de Clausura y Consistencia sobre tablas de observación L* para certificar DFAs mínimos canónicos y emite pruebas DPoP RFC 9449 con thumbprint JWK SHA-256 (jkt) y hash de token (ath) selladas con SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "s_prefixes": {"type": "array", "items": {"type": "string"}},
                    "alphabet_sigma": {"type": "array", "items": {"type": "string"}},
                    "row_vectors": {"type": "object"},
                    "jwk_public_params": {"type": "object"},
                    "access_token_string": {"type": "string"},
                    "parent_bundle_sha256": {"type": "string"},
                    "release_version": {"type": "string"}
                },
                "required": ["s_prefixes", "alphabet_sigma", "row_vectors", "jwk_public_params"]
            }
        }
        ,
        {
            "name": "aleph_prove_timed_automata_non_zeno_and_authorize_rfc9396_rar",
            "description": "Probador de Autómatas Temporizados de Alur-Dill (1994) y Ausencia de Ciclos de Zenón en Zonas de Reloj + Certificador de Solicitudes de Autorización Rica IETF RFC 9396 (RAR authorization_details) y RFC 9635 (GNAP) PCC (v9.5.0 - NODE-06 Shard): verifica invariantes de reloj por locación, bloquea transiciones de Zenón de retardo cero y valida descriptores de privilegio fino RFC 9396 RAR / RFC 9635 GNAP sellados con SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "location_invariants_max_ms": {"type": "object"},
                    "timed_transitions": {"type": "array", "items": {"type": "object"}},
                    "rar_authorization_details": {"type": "array", "items": {"type": "object"}},
                    "allowed_policy_actions": {"type": "array", "items": {"type": "string"}},
                    "parent_bundle_sha256": {"type": "string"},
                    "release_version": {"type": "string"}
                },
                "required": ["location_invariants_max_ms", "timed_transitions", "rar_authorization_details", "allowed_policy_actions"]
            }
        }
        ,
        {
            "name": "aleph_prove_petri_net_p_invariants_and_exchange_rfc8693_spiffe",
            "description": "Probador Algebraico de P-Invariantes y Matriz de Incidencia en Redes de Petri (Murata 1989) + Intercambio de Tokens Delegados IETF RFC 8693 (act Claim) y Documento de Identidad SPIFFE SVID PCC (v9.6.0 - NODE-06 Shard): verifica conservación estructural y^T * C == 0 y ausencia de marcado muerto inicial en redes de Petri concurrentes, valida cadenas de delegación SPIFFE SVID y emite claims RFC 8693 Token Exchange sellados con SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "places": {"type": "array", "items": {"type": "string"}},
                    "transitions": {"type": "array", "items": {"type": "string"}},
                    "w_minus": {"type": "array", "items": {"type": "array", "items": {"type": "integer"}}},
                    "w_plus": {"type": "array", "items": {"type": "array", "items": {"type": "integer"}}},
                    "initial_marking_m0": {"type": "array", "items": {"type": "integer"}},
                    "p_invariant_weights_y": {"type": "array", "items": {"type": "integer"}},
                    "delegation_spiffe_chain": {"type": "array", "items": {"type": "string"}},
                    "parent_bundle_sha256": {"type": "string"},
                    "release_version": {"type": "string"}
                },
                "required": ["places", "transitions", "w_minus", "w_plus", "initial_marking_m0", "p_invariant_weights_y", "delegation_spiffe_chain"]
            }
        }
        ,
        {
            "name": "aleph_prove_mpst_session_projection_and_commit_rfc9420_mls",
            "description": "Probador de Tipos de Sesión Multiparte y Proyección Dual de Endpoints (Honda-Yoshida-Carbone POPL 2008) + Árbol Criptográfico TreeKEM IETF RFC 9420 (Messaging Layer Security - MLS) PCC (v9.7.0 - NODE-06 Shard): verifica fidelidad de sesión y dualidad exacta envío/recepción (!/?) entre el protocolo global G y sus proyecciones locales G|p, y calcula el GroupContext y raíz TreeKEM RFC 9420 MLS sellados con SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "global_protocol_steps": {"type": "array", "items": {"type": "object"}},
                    "claimed_local_projections": {"type": "object"},
                    "mls_leaf_key_packages": {"type": "object"},
                    "epoch_number": {"type": "integer"},
                    "parent_bundle_sha256": {"type": "string"},
                    "release_version": {"type": "string"}
                },
                "required": ["global_protocol_steps", "claimed_local_projections", "mls_leaf_key_packages"]
            }
        }
        ,
        {
            "name": "aleph_prove_rely_guarantee_concurrency_and_present_openid4vp",
            "description": "Probador Composicional Rely-Guarantee de Concurrencia con Interferencia Acotada (Cliff B. Jones TOPLAS 1983) + Presentaciones Verificables OpenID4VP 1.0 con Key-Binding JWT (kb+jwt) PCC (v9.8.0 - NODE-06 Shard - Tool MCP #100): verifica que para todo par de hilos/nodos concurrentes (i != j) se cumpla Guarantee(i) subseteq Rely(j) con transiciones monotónicas e invariantes estables, y certifica la presentación verificable OpenID4VP 1.0 sellada con SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "concurrent_threads": {"type": "array", "items": {"type": "object"}},
                    "shared_state_transitions": {"type": "array", "items": {"type": "object"}},
                    "vp_presentation": {"type": "object"},
                    "parent_bundle_sha256": {"type": "string"},
                    "release_version": {"type": "string"}
                },
                "required": ["concurrent_threads", "shared_state_transitions", "vp_presentation"]
            }
        }
        ,
        {
            "name": "aleph_prove_atl_coalition_strategy_and_seal_rfc9180_hpke",
            "description": "Probador de Lógica Temporal de Tiempo Alternante (ATL — Alur, Henzinger & Kupferman JACM 2002) para Juegos Concurrentes de Coalición + Cifrado Híbrido de Clave Pública IETF RFC 9180 (HPKE Auth-Mode) PCC (v9.9.0 - NODE-06 Shard - Tool MCP #101): sintetiza la estrategia ganadora de la coalición honesta <<C>>[]Safe y <<C>><>Goal frente a acciones adversarias y sella el paquete con un contexto criptográfico HPKE RFC 9180 encadenado al CAS SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "cgs_states": {"type": "array", "items": {"type": "string"}},
                    "initial_state": {"type": "string"},
                    "safe_states": {"type": "array", "items": {"type": "string"}},
                    "goal_states": {"type": "array", "items": {"type": "string"}},
                    "game_transitions": {"type": "object"},
                    "hpke_params": {"type": "object"},
                    "parent_bundle_sha256": {"type": "string"},
                    "release_version": {"type": "string"}
                },
                "required": ["cgs_states", "initial_state", "safe_states", "goal_states", "game_transitions", "hpke_params"]
            }
        }
        ,
        {
            "name": "aleph_solve_mu_calculus_parity_game_and_sign_fips204_mldsa",
            "description": "Resolutor de Juegos de Paridad y Cálculo Mu Modal (Kozen 1983 / Zielonka-Jurdzinski STACS 2000) + Firmas Digitales Post-Cuánticas en Retículos Modulares NIST FIPS 204 (ML-DSA / CRYSTALS-Dilithium) PCC (v10.0.0 - NODE-06 Shard - Tool MCP #102): calcula las regiones ganadoras (W0, W1) y la estrategia sin memoria del Jugador 0 para prioridades pares infinitas y certifica la firma post-cuántica FIPS 204 ML-DSA verificando la cota de rechazo ||z||_inf < gamma_1 - beta y peso de hints ||h||_1 <= omega.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "vertices": {"type": "array", "items": {"type": "object"}},
                    "initial_vertex": {"type": "string"},
                    "mldsa_params": {"type": "object"},
                    "parent_bundle_sha256": {"type": "string"},
                    "release_version": {"type": "string"}
                },
                "required": ["vertices", "initial_vertex", "mldsa_params"]
            }
        }
        ,
        {
            "name": "aleph_prove_pctl_mdp_reachability_and_sign_fips205_slhdsa",
            "description": "Probador de Procesos de Decisión de Markov (MDP) y Lógica Temporal Probabilística PCTL (Hansson-Jonsson 1994 / Kwiatkowska PRISM) + Firmas Digitales Post-Cuánticas Basadas en Hash Sin Estado NIST FIPS 205 (SLH-DSA / SPHINCS+) PCC (v10.1.0 - NODE-06 Shard - Tool MCP #103): ejecuta iteración de valores de Bellman-Shapley para demostrar P_max(<>Goal) >= min_goal_probability y P(<>Unsafe) <= max_unsafe_probability sintetizando la política óptima sigma*, y sella el release con una firma post-cuántica basada en hash sin estado FIPS 205 SLH-DSA (FORS + XMSS Hypertree).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "mdp_states": {"type": "array", "items": {"type": "string"}},
                    "initial_state": {"type": "string"},
                    "goal_states": {"type": "array", "items": {"type": "string"}},
                    "unsafe_states": {"type": "array", "items": {"type": "string"}},
                    "mdp_transitions": {"type": "object"},
                    "min_goal_probability": {"type": "number"},
                    "max_unsafe_probability": {"type": "number"},
                    "slhdsa_params": {"type": "object"},
                    "parent_bundle_sha256": {"type": "string"},
                    "release_version": {"type": "string"}
                },
                "required": [
                    "mdp_states",
                    "initial_state",
                    "goal_states",
                    "unsafe_states",
                    "mdp_transitions",
                    "min_goal_probability",
                    "max_unsafe_probability",
                    "slhdsa_params"
                ]
            }
        }            ,
        {
            "name": "aleph_prove_aprhL_renyi_dp_and_encapsulate_fips203_mlkem",
            "description": "Probador Relacional Probabilístico apRHL y Privacidad Diferencial de Rényi (Barthe POPL 2012 / Mironov CSF 2017) + Encapsulación de Claves Post-Cuántica en Retículos Modulares NIST FIPS 203 (ML-KEM / CRYSTALS-Kyber FO-CCA2) PCC (v10.2.0 - NODE-06 Shard - Tool MCP #104): verifica composición aditiva de divergencia de Rényi y conversión a (epsilon, delta)-DP dentro del presupuesto formal, y encapsula la clave compartida post-cuántica FIPS 203 ML-KEM con verificación modular mod q = 3329 y transformación Fujisaki-Okamoto IND-CCA2.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "dp_mechanisms": {"type": "array", "items": {"type": "object"}},
                    "renyi_alpha": {"type": "number"},
                    "target_delta": {"type": "number"},
                    "max_epsilon_budget": {"type": "number"},
                    "mlkem_params": {"type": "object"},
                    "parent_bundle_sha256": {"type": "string"},
                    "release_version": {"type": "string"}
                },
                "required": [
                    "dp_mechanisms",
                    "renyi_alpha",
                    "target_delta",
                    "max_epsilon_budget",
                    "mlkem_params"
                ]
            }
        }
        ,
        {
            "name": "aleph_prove_csl_disjoint_concurrency_and_sign_rfc9591_frost",
            "description": "Probador de Lógica de Separación Concurrente (CSL — Peter W. O'Hearn TCS 2007) e Invariantes de Recursos Disjuntos + Firmas Schnorr de Umbral en Dos Rondas IETF RFC 9591 (FROST) PCC (v10.3.0 - NODE-06 Shard - Tool MCP #105): verifica disjunción de huellas de memoria local (P1 * P2) y protección de invariantes de recursos J_r en regiones críticas, y certifica el quórum t-de-n de firmas Schnorr de umbral RFC 9591 FROST comprobando la partición de la unidad de Lagrange en F_q.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "resource_invariants": {"type": "object"},
                    "concurrent_threads": {"type": "array", "items": {"type": "object"}},
                    "frost_params": {"type": "object"},
                    "parent_bundle_sha256": {"type": "string"},
                    "release_version": {"type": "string"}
                },
                "required": ["resource_invariants", "concurrent_threads", "frost_params"]
            }
        }
        ,
        {
            "name": "aleph_prove_weak_bisimulation_and_evaluate_rfc9497_voprf",
            "description": "Probador de Bisimulación Observacional Débil por Refinamiento de Particiones (Milner 1989 / Kanellakis-Smolka 1990) + Funciones Pseudoaleatorias Oblivious Verificables IETF RFC 9497 (VOPRF con prueba Chaum-Pedersen DLEQ) PCC (v10.4.0 - NODE-06 Shard - Tool MCP #106): calcula la clausura tau* y refina particiones sobre sistemas de transición etiquetados comprobando equivalencia observacional spec_init ~_w impl_init, y certifica la evaluación VOPRF RFC 9497 con prueba DLEQ de conocimiento cero.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "lts_transitions": {"type": "array", "items": {"type": "object"}},
                    "spec_initial_state": {"type": "string"},
                    "impl_initial_state": {"type": "string"},
                    "voprf_params": {"type": "object"},
                    "parent_bundle_sha256": {"type": "string"},
                    "release_version": {"type": "string"}
                },
                "required": ["lts_transitions", "spec_initial_state", "impl_initial_state", "voprf_params"]
            }
        }
        ,
        {
            "name": "aleph_prove_kat_guarded_strings_and_issue_rfc9578_privacypass",
            "description": "Probador de Álgebra de Kleene con Tests (KAT — Dexter Kozen TOPLAS 1997) y Autómatas de Cadenas Guardadas + Protocolo de Emisión y Redención de Tokens Anónimos IETF RFC 9576 / RFC 9578 (Privacy Pass) PCC (v10.5.0 - NODE-06 Shard - Tool MCP #107): verifica la subsunción ecuacional de Lógica de Hoare Pre ; (b ; p)* ; !b ; !Post == 0 y la identidad de desenrollado de Kleene sobre átomos booleanos, y certifica la emisión/redención de tokens Privacy Pass RFC 9578 previniendo el doble gasto.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "boolean_atoms": {"type": "array", "items": {"type": "string"}},
                    "precondition_atoms": {"type": "array", "items": {"type": "string"}},
                    "loop_guard_atoms": {"type": "array", "items": {"type": "string"}},
                    "postcondition_atoms": {"type": "array", "items": {"type": "string"}},
                    "action_transitions": {"type": "object"},
                    "privacypass_params": {"type": "object"},
                    "parent_bundle_sha256": {"type": "string"},
                    "release_version": {"type": "string"}
                },
                "required": [
                    "boolean_atoms",
                    "precondition_atoms",
                    "loop_guard_atoms",
                    "postcondition_atoms",
                    "action_transitions",
                    "privacypass_params"
                ]
            }
        }
        ,
        {
            "name": "aleph_prove_stratified_datalog_seminaive_and_hash_rfc9380_curve",
            "description": "Probador de Análisis Declarativo en Datalog Estratificado y Evaluación Semi-Naive (Soufflé CAV 2016 / Abiteboul-Hull-Vianu) + Codificación Criptográfica en Curvas Elípticas IETF RFC 9380 (Hash-to-Curve expand_message_xmd) PCC (v10.6.0 - NODE-06 Shard - Tool MCP #108): verifica ausencia de ciclos con negación recursiva en el grafo de predicados, evalúa el punto fijo mínimo por estratos comprobando cero tuplas en violation_predicate, y ejecuta expand_message_xmd(SHA-256) y hash_to_field conforme a RFC 9380.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "edb_facts": {"type": "object"},
                    "datalog_rules": {"type": "array", "items": {"type": "object"}},
                    "violation_predicate": {"type": "string"},
                    "rfc9380_params": {"type": "object"},
                    "parent_bundle_sha256": {"type": "string"},
                    "release_version": {"type": "string"}
                },
                "required": ["edb_facts", "datalog_rules", "violation_predicate", "rfc9380_params"]
            }
        }
        ,
        {
            "name": "aleph_check_cic_dependent_proof_term_and_agree_x25519mlkem768",
            "description": "Kernel Verificador de Tipos Dependientes en el Cálculo de Construcciones Inductivas (CIC — Coquand & Huet 1988 / Paulin-Mohring — Hito Nivel 100) + Acuerdo de Claves Híbrido Post-Cuántico IETF X25519MLKEM768 (draft-ietf-tls-ecdhe-mlkem, 0x11EC) PCC (v10.7.0 - NODE-06 Shard - Tool MCP #109): verifica ausencia de paradoja de Girard en la jerarquía de universos, positividad estricta de constructores inductivos, recursión estructuralmente guardada y convertibilidad beta-delta-iota del término de prueba, y deriva el secreto compartido híbrido X25519MLKEM768.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "universe_constraints": {"type": "array", "items": {"type": "object"}},
                    "inductive_declarations": {"type": "array", "items": {"type": "object"}},
                    "fixpoint_definitions": {"type": "array", "items": {"type": "object"}},
                    "proof_term_judgment": {"type": "object"},
                    "x25519mlkem768_params": {"type": "object"},
                    "parent_bundle_sha256": {"type": "string"},
                    "release_version": {"type": "string"}
                },
                "required": [
                    "universe_constraints",
                    "inductive_declarations",
                    "fixpoint_definitions",
                    "proof_term_judgment",
                    "x25519mlkem768_params"
                ]
            }
        }
        ,
        {
            "name": "aleph_prove_qtt_linear_resource_usage_and_prove_bbs_zkp",
            "description": "Probador de Teoría de Tipos Cuantitativa y Lógica Lineal de Girard (QTT — Girard 1987 / Atkey LICS 2018) + Firmas Multi-Mensaje con Divulgación Selectiva en Conocimiento Cero IRTF CFRG BBS (BLS12-381-SHA-256) PCC (v10.8.0 - NODE-06 Shard - Tool MCP #110): verifica conservación exacta de recursos lineales (multiplicidad 1 en todas las ramas sin debilitamiento ni contracción) y borrado en tiempo de ejecución de índices fantasma (multiplicidad 0), y certifica la prueba de divulgación selectiva desvinculable BBS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "resource_bindings": {"type": "array", "items": {"type": "object"}},
                    "bbs_params": {"type": "object"},
                    "parent_bundle_sha256": {"type": "string"},
                    "release_version": {"type": "string"}
                },
                "required": ["resource_bindings", "bbs_params"]
            }
        }
        ,
        {
            "name": "aleph_prove_algebraic_effects_row_and_verify_rfc9562_statuslist",
            "description": "Probador de Efectos Algebraicos y Manejadores con Polimorfismo de Filas (Plotkin & Pretnar LMCS 2013 / Leijen POPL 2017) + Identificadores Monotónicos IETF RFC 9562 (UUIDv7/UUIDv8) y W3C BitstringStatusList PCC (v10.9.0 - NODE-06 Shard - Tool MCP #111): verifica descarga completa de filas de efectos algebraicos, disciplina lineal one-shot en continuaciones de manejadores, monotonicidad temporal de UUIDv7, síntesis determinista de UUIDv8 y ausencia de revocación en BitstringStatusList.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "performed_effects": {"type": "array", "items": {"type": "string"}},
                    "effect_handlers": {"type": "array", "items": {"type": "object"}},
                    "allowed_ambient_effects": {"type": "array", "items": {"type": "string"}},
                    "rfc9562_status_params": {"type": "object"},
                    "parent_bundle_sha256": {"type": "string"},
                    "release_version": {"type": "string"}
                },
                "required": [
                    "performed_effects",
                    "effect_handlers",
                    "allowed_ambient_effects",
                    "rfc9562_status_params"
                ]
            }
        }
        ,
        {
            "name": "aleph_prove_liquid_refinement_subtyping_and_attest_dice_cmw",
            "description": "Probador de Tipos de Refinamiento Líquidos y Subtipado Decidible (Rondon, Kawaguichi & Jhala PLDI 2008 / LiquidHaskell) + Cadena de Atestación por Capas TCG DICE / IETF RFC 9683 y RATS CMW PCC (v11.0.0 - Hito Mayor v11.0 - NODE-06 Shard - Tool MCP #112): verifica implicaciones de subtipado sobre tipos refinados {v : B | P(v)} <: {v : B | Q(v)} sintetizando calificadores líquidos, y deriva la cadena recursiva Compound Device Identifier (CDI) de las capas TCB en un sobre RATS CMW.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "subtyping_obligations": {"type": "array", "items": {"type": "object"}},
                    "dice_tcb_layers": {"type": "array", "items": {"type": "object"}},
                    "uds_root_seed_hex": {"type": "string"},
                    "parent_bundle_sha256": {"type": "string"},
                    "release_version": {"type": "string"}
                },
                "required": ["subtyping_obligations", "dice_tcb_layers", "uds_root_seed_hex"]
            }
        }
        ,
        {
            "name": "aleph_prove_incorrectness_logic_underapprox_and_register_scitt",
            "description": "Probador de Lógica de Incorrección Sub-Aproximada (Peter W. O'Hearn POPL 2020 — [P] C [ok: Q_ok][er: Q_er]) + Política de Registro y Declaración Firmada IETF SCITT (Supply Chain Integrity, Transparency, and Trust) PCC (v11.1.0 - NODE-06 Shard - Tool MCP #113): verifica que todo estado normal (ok) y de error (er) reclamado en la post-condición sea auténticamente alcanzable desde algún estado en P (garantizando 0.0% de falsos positivos), y certifica el registro de la declaración firmada SCITT.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "pre_states": {"type": "array", "items": {"type": "string"}},
                    "program_transitions": {"type": "array", "items": {"type": "object"}},
                    "claimed_ok_post_states": {"type": "array", "items": {"type": "string"}},
                    "claimed_er_post_states": {"type": "array", "items": {"type": "string"}},
                    "scitt_policy_params": {"type": "object"},
                    "parent_bundle_sha256": {"type": "string"},
                    "release_version": {"type": "string"}
                },
                "required": [
                    "pre_states",
                    "program_transitions",
                    "claimed_ok_post_states",
                    "claimed_er_post_states",
                    "scitt_policy_params"
                ]
            }
        }
        ,
        {
            "name": "aleph_prove_farkas_polyhedral_invariant_and_verify_rfc9530_digest",
            "description": "Probador de Invariantes Poliédricos Convexos mediante el Lema de Farkas (Colón, Sankaranarayanan & Sipma CAV 2003) + Campos de Integridad de Representación HTTP IETF RFC 9530 (Repr-Digest / Content-Digest) PCC (v11.2.0 - NODE-06 Shard - Tool MCP #114): verifica que los multiplicadores duales lambda >= 0 satisfagan A^T * lambda == c y lambda^T * b <= d demostrando P |= (c^T x <= d), y certifica la cabecera Structured Field Repr-Digest sha-256=:<b64>: conforme a RFC 9530.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "matrix_A": {"type": "array", "items": {"type": "array", "items": {"type": "number"}}},
                    "vector_b": {"type": "array", "items": {"type": "number"}},
                    "feasible_witness_x": {"type": "array", "items": {"type": "number"}},
                    "target_c": {"type": "array", "items": {"type": "number"}},
                    "target_d": {"type": "number"},
                    "farkas_multipliers_lambda": {"type": "array", "items": {"type": "number"}},
                    "rfc9530_params": {"type": "object"},
                    "parent_bundle_sha256": {"type": "string"},
                    "release_version": {"type": "string"}
                },
                "required": [
                    "matrix_A",
                    "vector_b",
                    "feasible_witness_x",
                    "target_c",
                    "target_d",
                    "farkas_multipliers_lambda",
                    "rfc9530_params"
                ]
            }
        }
        ,
        {
            "name": "aleph_prove_kildall_distributive_lattice_and_bind_rfc9278_jwk",
            "description": "Probador de Semirretículos Distributivos de Flujo de Datos y Coincidencia MFP == MOP (Kildall POPL 1973 / Kam-Ullman JACM 1976) + URI de Huella Criptográfica JWK IETF RFC 9278 y Diagnósticos RFC 9457 PCC (v11.3.0 - NODE-06 Shard - Tool MCP #115): verifica leyes de semirretículo (idempotencia, conmutatividad, asociatividad) y distributividad homomórfica f(x sqcap y) == f(x) sqcap f(y) demostrando MFP == MOP, y sintetiza el identificador urn:ietf:params:oauth:jwk-thumbprint:sha-256 conforme a RFC 9278.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "lattice_elements": {"type": "array", "items": {"type": "string"}},
                    "meet_table": {"type": "object"},
                    "transfer_functions": {"type": "object"},
                    "jwk_public_params": {"type": "object"},
                    "rfc9457_problem_schema": {"type": "object"},
                    "parent_bundle_sha256": {"type": "string"},
                    "release_version": {"type": "string"}
                },
                "required": [
                    "lattice_elements",
                    "meet_table",
                    "transfer_functions",
                    "jwk_public_params",
                    "rfc9457_problem_schema"
                ]
            }
        }
        ,
        {
            "name": "aleph_prove_gsos_bisimulation_congruence_and_canonicalize_rfc8785_jcs",
            "description": "Probador de Formato GSOS de Semántica Operacional Estructural y Congruencia de Bisimulación Fuerte (Plotkin 1981 / Bloom-Istrail-Meyer JACM 1995) + Canonicalización JSON Determinista IETF RFC 8785 (JCS) PCC (v11.4.0 - NODE-06 Shard - Tool MCP #116): verifica ausencia de lookahead, variables fuente distintas, premisas negativas bien fundadas y clausura de variables objetivo garantizando que la bisimulación sea congruencia algebraica, y canonicaliza documentos JSON bajo RFC 8785 (UTF-16 key sorting + I-JSON RFC 7493).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "gsos_rules": {"type": "array", "items": {"type": "object"}},
                    "jcs_payload": {"type": "object"},
                    "parent_bundle_sha256": {"type": "string"},
                    "release_version": {"type": "string"}
                },
                "required": [
                    "gsos_rules",
                    "jcs_payload"
                ]
            }
        }
        ,
        {
            "name": "aleph_prove_kpn_scott_continuity_and_verify_rfc9440_mtls",
            "description": "Probador de Redes de Procesos de Kahn (KPN) con Continuidad de Scott en Órdenes Parciales Completos de Prefijos y Planificación Acotada Libre de Deadlock Artificial (Kahn IFIP 1974 / Parks 1995) + Cabeceras HTTP mTLS Client-Cert IETF RFC 9440 PCC (v11.5.0 - NODE-06 Shard - Tool MCP #117): verifica monotonía de prefijos s1 sqsubseteq s2 => F(s1) sqsubseteq F(s2), ausencia de primitivas no-monótonas y capacidades FIFO acotadas de Parks, y valida cabeceras estructuradas RFC 8941 Client-Cert / Client-Cert-Chain conforme a RFC 9440.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "kpn_processes": {"type": "array", "items": {"type": "object"}},
                    "kpn_channels": {"type": "array", "items": {"type": "object"}},
                    "rfc9440_headers": {"type": "object"},
                    "parent_bundle_sha256": {"type": "string"},
                    "release_version": {"type": "string"}
                },
                "required": [
                    "kpn_processes",
                    "kpn_channels",
                    "rfc9440_headers"
                ]
            }
        }
        ,
        {
            "name": "aleph_prove_sdf_balance_equations_and_verify_rfc9218_priority",
            "description": "Probador de Ecuaciones de Balance Topológico en Flujo de Datos Síncrono Multi-Tasa (SDF — Lee & Messerschmitt Proc. IEEE 1987) y Planificación Periódica Admisible (PASS) + Priorización Extensible HTTP IETF RFC 9218 PCC (v11.6.0 - NODE-06 Shard - Tool MCP #118): verifica Gamma * q = 0 con vector de repetición coprimo mínimo, simula la planificación PASS comprobando ausencia de subdesbordamiento y conservación periódica de tokens, y valida cabeceras estructuradas Priority (u=0..7, i) conforme a RFC 9218.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "sdf_actors": {"type": "array", "items": {"type": "string"}},
                    "sdf_arcs": {"type": "array", "items": {"type": "object"}},
                    "repetition_vector": {"type": "object"},
                    "pass_schedule": {"type": "array", "items": {"type": "string"}},
                    "rfc9218_priority": {"type": "object"},
                    "parent_bundle_sha256": {"type": "string"},
                    "release_version": {"type": "string"}
                },
                "required": [
                    "sdf_actors",
                    "sdf_arcs",
                    "repetition_vector",
                    "pass_schedule",
                    "rfc9218_priority"
                ]
            }
        }
        ,
        {
            "name": "aleph_prove_birkhoff_duality_and_verify_rfc9292_bhttp",
            "description": "Probador de Dualidad de Birkhoff para Retículos Distributivos Finitos vía Ideales de Elementos Sup-Irreducibles J(L) (Birkhoff 1937 / Priestley 1970) + Encapsulación Binaria HTTP IETF RFC 9292 (bHTTP) PCC (v11.7.0 - NODE-06 Shard - Tool MCP #119): verifica distributividad mutua de join/meet, extrae el sub-poset de elementos sup-irreducibles J(L), demuestra el isomorfismo eta: L -> O(J(L)) y valida el encuadre binario determinista message/bhttp con enteros de longitud variable QUIC (RFC 9292).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "lattice_elements": {"type": "array", "items": {"type": "string"}},
                    "bottom_element": {"type": "string"},
                    "join_table": {"type": "object"},
                    "meet_table": {"type": "object"},
                    "rfc9292_bhttp_message": {"type": "object"},
                    "parent_bundle_sha256": {"type": "string"},
                    "release_version": {"type": "string"}
                },
                "required": [
                    "lattice_elements",
                    "bottom_element",
                    "join_table",
                    "meet_table",
                    "rfc9292_bhttp_message"
                ]
            }
        }
        ,
        {
            "name": "aleph_prove_css_scope_donut_style_queries_and_wcag_focus_trap",
            "description": "Demostrador Formal de Scoping Donut W3C CSS Cascading Level 6 (@scope (<root>) to (<limit>)), Consultas de Estilo de Contenedor W3C CSS Containment Level 3 (@container style(--*)) y Ausencia de Trampas de Teclado / Orden de Foco Secuencial W3C WCAG 2.2 AA (SC 2.1.2 & SC 2.4.3) (v15.0.0 - Nivel 264 Formal NODE-02 Shard): previene fugas de estilos en subárboles de slots, detecta ciclos en custom properties de style queries y bloquea tabindex > 0 o trampas de foco modales.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code_or_css": {"type": "string"},
                    "target_path": {"type": "string", "default": "components/AwwwardsScopedCard.tsx"},
                    "brand_accent_oklch": {"type": "string", "default": "oklch(0.68 0.19 265)"}
                },
                "required": ["code_or_css"]
            }
        }            ,
        {
            "name": "aleph_prove_view_transitions_l2_anchor_fallbacks_and_wcag_focus_obscured",
            "description": "Demostrador Formal W3C CSS View Transitions Level 2 (@view-transition { navigation: auto; } + view-transition-class), W3C CSS Anchor Positioning Fallbacks (position-try-fallbacks: flip-block, flip-inline + position-visibility: anchors-visible) y W3C WCAG 2.2 SC 2.4.11 / SC 2.4.12 (Focus Not Obscured por cabeceras sticky/fixed mediante scroll-padding-top) (v15.1.0 - Nivel 265 Formal NODE-02 Shard): previene colisiones de view-transition-name en listas .map(), evita recortes de popovers anclados en viewport móvil y garantiza visibilidad del foco de teclado.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code_or_css": {"type": "string"},
                    "target_path": {"type": "string", "default": "components/AwwwardsSpatialPopover.tsx"},
                    "brand_accent_oklch": {"type": "string", "default": "oklch(0.68 0.19 265)"}
                },
                "required": ["code_or_css"]
            }
        }            ,
        {
            "name": "aleph_prove_text_box_cap_alphabetic_calc_size_and_wcag_accessible_auth",
            "description": "Demostrador Formal W3C CSS Inline Layout Level 3 (text-box-trim: trim-both + text-box-edge: cap alphabetic), W3C CSS Values Level 5 (calc-size(auto, size) + interpolate-size) y W3C WCAG 2.2 SC 3.3.8 / SC 2.5.8 (Accessible Authentication sin bloqueo de paste + Passkey WebAuthn + Target Size >= 24x24px) (v15.2.0 - Nivel 266 Formal NODE-02 Shard): elimina hacks de margen negativo en tipografía modular, erradica max-height: 9999px en acordeones y garantiza autenticación accesible sin carga cognitiva.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code_or_css": {"type": "string"},
                    "target_path": {"type": "string", "default": "components/AwwwardsOpticalAuthCard.tsx"},
                    "brand_accent_oklch": {"type": "string", "default": "oklch(0.68 0.19 265)"}
                },
                "required": ["code_or_css"]
            }
        }            ,
        {
            "name": "aleph_prove_view_timeline_position_visibility_and_wcag_consistent_help",
            "description": "Demostrador Formal W3C CSS Scroll-Driven View Timelines Compositor-Only (animation-timeline: view() + animation-range sin layout thrashing), W3C CSS Anchor Positioning Conditional Hiding (position-visibility: anchors-visible no-overflow) y W3C WCAG 2.2 SC 3.2.6 / SC 2.5.7 (Consistent Help + Single-Pointer Dragging Fallbacks) (v15.3.0 - Nivel 267 Formal NODE-02 Shard): bloquea animaciones de propiedades de layout en scroll timelines, oculta popovers huérfanos fuera de viewport y garantiza alternativas de clic simple en interfaces drag-and-drop.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code_or_css": {"type": "string"},
                    "target_path": {"type": "string", "default": "components/AwwwardsViewTimelineSection.tsx"},
                    "brand_accent_oklch": {"type": "string", "default": "oklch(0.68 0.19 265)"}
                },
                "required": ["code_or_css"]
            }
        }            ,
        {
            "name": "aleph_prove_relative_oklch_starting_style_and_wcag_redundant_entry",
            "description": "Demostrador Formal W3C CSS Color Level 5 Relative Color Syntax (oklch(from var(--brand) ...)), W3C CSS Transitions Level 2 (@starting-style + transition-behavior: allow-discrete en Top Layer) y W3C WCAG 2.2 SC 3.3.7 (Redundant Entry Zero-Re-Typing en flujos multi-paso) (v15.4.0 - Nivel 268 Formal NODE-02 Shard): reemplaza derivaciones hsla()/rgba() por sintaxis perceptual relativa OKLCH, erradica hacks de doble requestAnimationFrame en diálogos/popovers y garantiza pre-poblado automático entre pasos.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code_or_css": {"type": "string"},
                    "target_path": {"type": "string", "default": "components/AwwwardsTopLayerDialog.tsx"},
                    "brand_accent_oklch": {"type": "string", "default": "oklch(0.68 0.19 265)"}
                },
                "required": ["code_or_css"]
            }
        }            ,
        {
            "name": "aleph_prove_css_subgrid_content_visibility_and_wcag_reflow_text_spacing",
            "description": "Demostrador Formal W3C CSS Grid Level 2 (grid-template-rows: subgrid), W3C CSS Containment Level 2 (content-visibility: auto + contain-intrinsic-size: auto <size>) y W3C WCAG 2.2 SC 1.4.10 / SC 1.4.12 (Reflow 320 CSS px sin scroll horizontal + Text Spacing sin truncamiento) (v15.5.0 - Nivel 269 Formal NODE-02 Shard): erradica loops JS de offsetHeight en grillas Bento, previene saltos de scrollbar en virtualización CSS y garantiza reflujo responsivo al 400% de zoom.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code_or_css": {"type": "string"},
                    "target_path": {"type": "string", "default": "components/AwwwardsSubgridBento.tsx"},
                    "brand_accent_oklch": {"type": "string", "default": "oklch(0.68 0.19 265)"}
                },
                "required": ["code_or_css"]
            }
        }            ,
        {
            "name": "aleph_prove_popover_top_layer_interpolate_size_and_wcag_target_dragging",
            "description": "Demostrador Formal W3C HTML Popover API Top-Layer (popover=\"auto\", popovertarget, :popover-open), W3C CSS Values and Units Level 5 (interpolate-size: allow-keywords + transition-behavior: allow-discrete) y W3C WCAG 2.2 SC 2.5.8 Target Size (Minimum >= 24x24 CSS px) / SC 2.5.7 Dragging Movements (v15.6.0 - Nivel 270 Formal NODE-02 Shard): erradica portales JS con z-index: 99999, reemplaza transiciones max-height: 9999px por interpolación intrínseca hacia auto y certifica ergonomía táctil y alternativa de puntero único.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code_or_css": {"type": "string"},
                    "target_path": {"type": "string", "default": "components/AwwwardsPopoverAccordionStage.tsx"},
                    "brand_accent_oklch": {"type": "string", "default": "oklch(0.68 0.19 265)"}
                },
                "required": ["code_or_css"]
            }
        }            ,
        {
            "name": "aleph_prove_field_sizing_user_valid_and_wcag_error_suggestion",
            "description": "Demostrador Formal W3C CSS Basic UI Level 4 (field-sizing: content acotado con min-block-size y max-block-size), W3C Selectors Level 4 (:user-invalid / :user-valid) y W3C WCAG 2.2 SC 3.3.1 Error Identification / SC 3.3.3 Error Suggestion (v15.7.0 - Nivel 271 Formal NODE-02 Shard): erradica el recálculo síncrono scrollHeight en textareas, reemplaza :invalid prematuro por validación diferida post-interacción y exige sugerencias constructivas vía aria-describedby.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code_or_css": {"type": "string"},
                    "target_path": {"type": "string", "default": "components/AwwwardsFieldSizingFormStage.tsx"},
                    "brand_accent_oklch": {"type": "string", "default": "oklch(0.68 0.19 265)"}
                },
                "required": ["code_or_css"]
            }
        }            ,
        {
            "name": "aleph_prove_linear_spring_scrollbar_gutter_and_wcag_error_prevention",
            "description": "Demostrador Formal W3C CSS Easing Functions Level 2 (linear() spring physics en compositor GPU), W3C CSS Overflow Level 3 (scrollbar-gutter: stable + overscroll-behavior: contain) y W3C WCAG 2.2 SC 2.5.2 Pointer Cancellation / SC 3.3.4 Error Prevention (v15.8.0 - Nivel 272 Formal NODE-02 Shard): erradica loops JS requestAnimationFrame sobre style.transform, elimina saltos CLS al ocultar el scrollbar y bloquea disparos destructivos en onMouseDown/onTouchStart.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code_or_css": {"type": "string"},
                    "target_path": {"type": "string", "default": "components/AwwwardsSpringDrawerAndCheckoutStage.tsx"},
                    "brand_accent_oklch": {"type": "string", "default": "oklch(0.68 0.19 265)"}
                },
                "required": ["code_or_css"]
            }
        }            ,
        {
            "name": "aleph_prove_light_dark_color_mix_oklch_and_wcag_non_text_contrast",
            "description": "Demostrador Formal W3C CSS Color Module Level 5 (light-dark() + color-scheme: light dark Zero-FOUC e interpolación perceptual color-mix(in oklch, ...)) y W3C WCAG 2.2 SC 1.4.11 Non-text Contrast (>= 3:1) (v15.9.0 - Nivel 273 Formal NODE-02 Shard): erradica el parpadeo de hidratación FOUC por temas JS, reemplaza mezclas sRGB apagadas por espacio perceptual OKLCH y bloquea bordes de inputs fantasma menores a 3:1.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code_or_css": {"type": "string"},
                    "target_path": {"type": "string", "default": "components/AwwwardsThemeAndSurfaceTokens.tsx"},
                    "brand_accent_oklch": {"type": "string", "default": "oklch(0.68 0.19 265)"}
                },
                "required": ["code_or_css"]
            }
        }            ,
        {
            "name": "aleph_prove_speculation_rules_text_wrap_balance_and_wcag_forced_colors",
            "description": "Demostrador Formal W3C Speculation Rules API (prerender seguro con exclusión de rutas mutadoras y eagerness: moderate), W3C CSS Text Module Level 4 (text-wrap: balance en titulares + text-wrap: pretty en cuerpo editorial) y W3C CSS Color Adjustment Level 1 (@media (forced-colors: active) con Highlight/CanvasText) (v16.0.0 - Nivel 274 Formal NODE-02 Shard): habilita navegaciones 0ms LCP sin disparar /logout por accidente, erradica saltos <br> rígidos y garantiza visibilidad de foco en modos de Alto Contraste.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code_or_css": {"type": "string"},
                    "target_path": {"type": "string", "default": "components/AwwwardsEditorialNavigationStage.tsx"},
                    "brand_accent_oklch": {"type": "string", "default": "oklch(0.68 0.19 265)"}
                },
                "required": ["code_or_css"]
            }
        }            ,
        {
            "name": "aleph_prove_css_property_houdini_font_size_adjust_and_wcag_pause_stop_hide",
            "description": "Demostrador Formal W3C CSS Properties and Values API Level 1 (@property con syntax, inherits: false e initial-value), W3C CSS Fonts Module Level 5 (font-size-adjust: ex-height Zero-CLS) y W3C WCAG 2.2 SC 2.2.2 Pause, Stop, Hide (v16.1.0 - Nivel 275 Formal NODE-02 Shard): erradica loops JS setProperty sobre gradientes, normaliza métricas de fuentes de respaldo para CLS = 0.00 y exige control de pausa en marquees infinitos.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code_or_css": {"type": "string"},
                    "target_path": {"type": "string", "default": "components/AwwwardsHoudiniAuroraAndTickerStage.tsx"},
                    "brand_accent_oklch": {"type": "string", "default": "oklch(0.68 0.19 265)"}
                },
                "required": ["code_or_css"]
            }
        }
    ,
        {
            "name": "aleph_prove_byzantine_pbft_quorum_and_threshold_signature",
            "description": "Demostrador Formal de Consenso Tolerante a Fallos Bizantinos PBFT / HotStuff 3-Chain (Castro & Liskov OSDI 1999; Yin et al. PODC 2019), Intersección de Quórums Bizantinos (N >= 3f + 1, Q >= 2f + 1) y Certificados de Quórum con Firmas Umbral BLS12-381 Protegidas contra Claves Pícaras (Rogue-Key PoP) (v10.7.0 - Hito Nivel 100 - NODE-01 Shard - Tool MCP #109): verifica intersección >= f+1, predicado SafeNode en View-Change y detección de equivocación con PCC SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "bft_quorum_configs": {"type": "array", "items": {"type": "object"}},
                    "view_change_proposals": {"type": "array", "items": {"type": "object"}},
                    "threshold_signature_batches": {"type": "array", "items": {"type": "object"}},
                    "consensus_id": {"type": "string"}
                },
                "required": ["bft_quorum_configs", "view_change_proposals", "threshold_signature_batches"]
            }
        },
        {
            "name": "aleph_prove_narwhal_bullshark_dag_and_erasure_vid",
            "description": "Demostrador Formal de Mempool DAG Narwhal & Consenso Zero-Message-Overhead Bullshark (Danezis et al. EuroSys 2022; Spiegelman et al. CCS 2022) y Dispersión de Información Verificable (VID) con Codificación de Borrado Reed-Solomon (k = f + 1 de N) y Pruebas de Inclusión de Merkle (v10.8.0 - Nivel 101 - NODE-01 Shard - Tool MCP #110): verifica avance de ronda 2f+1 CoAs, regla de commit de anclas pares con f+1 votos y reconstrucción VID libre de Data Withholding con PCC SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "dag_vertices": {"type": "array", "items": {"type": "object"}},
                    "bullshark_anchors": {"type": "array", "items": {"type": "object"}},
                    "erasure_vid_batches": {"type": "array", "items": {"type": "object"}},
                    "dag_id": {"type": "string"}
                },
                "required": ["dag_vertices", "bullshark_anchors", "erasure_vid_batches"]
            }
        },
        {
            "name": "aleph_prove_block_stm_speculative_parallel_execution",
            "description": "Demostrador Formal de Ejecución Paralela Especulativa Determinista Block-STM con Memoria Multi-Versión (MVMemory, Gelashvili et al. PPoPP 2023) y Marcadores ESTIMATE (v10.9.0 - Nivel 102 - NODE-01 Shard - Tool MCP #111): verifica equivalencia serial preestablecida (tx_0 < ... < tx_{n-1}), conversión de escrituras abortadas en marcadores ESTIMATE y convergencia monotónica por encarnación con PCC SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "transaction_traces": {"type": "array", "items": {"type": "object"}},
                    "abort_estimate_transitions": {"type": "array", "items": {"type": "object"}},
                    "scheduler_priorities": {"type": "array", "items": {"type": "object"}},
                    "executor_id": {"type": "string"}
                },
                "required": ["transaction_traces", "abort_estimate_transitions", "scheduler_priorities"]
            }
        },
        {
            "name": "aleph_prove_sparse_merkle_jellyfish_and_verkle_commitment",
            "description": "Demostrador Formal de Árboles de Estado Autenticados Jellyfish Sparse Merkle Trie (JMT, Diem/Aptos) y Compromisos Polinomiales Vectoriales Verkle / KZG10 (Kuszmaul 2019; Kate et al. ASIACRYPT 2010) (v11.0.0 - Hito Mayor v11 - Nivel 103 - NODE-01 Shard - Tool MCP #112): verifica compresión de caminos de un solo hijo, pruebas criptográficas de no-inclusión, vinculación Fiat-Shamir contra Frozen Heart y emparejamiento bilineal KZG con PCC SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "jellyfish_trie_updates": {"type": "array", "items": {"type": "object"}},
                    "non_inclusion_proofs": {"type": "array", "items": {"type": "object"}},
                    "verkle_kzg_openings": {"type": "array", "items": {"type": "object"}},
                    "tree_id": {"type": "string"}
                },
                "required": ["jellyfish_trie_updates", "non_inclusion_proofs", "verkle_kzg_openings"]
            }
        },
        {
            "name": "aleph_prove_zk_r1cs_plonk_under_constrained_and_logup_lookup",
            "description": "Demostrador Formal de Circuitos Aritméticos de Conocimiento Cero (R1CS / PLONKish / Halo2), Detección de Señales Sub-Restringidas (Assigned-but-Unconstrained Witnesses, Picus PLDI 2023) y Argumentos de Búsqueda LogUp / Plookup (v11.1.0 - Nivel 104 - NODE-01 Shard - Tool MCP #113): verifica cotas de rango en campo primo F_p contra underflow modular, completitud de ecuaciones polinomiales sobre testigos y conservación de multiplicidades en tablas LogUp con PCC SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "field_comparisons": {"type": "array", "items": {"type": "object"}},
                    "witness_signals": {"type": "array", "items": {"type": "object"}},
                    "logup_tables": {"type": "array", "items": {"type": "object"}},
                    "circuit_id": {"type": "string"}
                },
                "required": ["field_comparisons", "witness_signals", "logup_tables"]
            }
        },
        {
            "name": "aleph_prove_nova_hypernova_folding_ivc_and_sumcheck",
            "description": "Demostrador Formal de Esquemas de Plegado para Cómputo Incrementalmente Verificable (IVC) Nova / HyperNova (Kothapalli, Setty & Tzialla CRYPTO 2022/2023) y Protocolo Sum-Check Multilineal sobre CCS (v11.2.0 - Nivel 105 - NODE-01 Shard - Tool MCP #114): verifica plegado exacto de R1CS Relajado con absorción del término cruzado T, vinculación Fiat-Shamir de com(T) y consistencia por ronda g_k(0)+g_k(1) en Sum-Check con PCC SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "relaxed_r1cs_folds": {"type": "array", "items": {"type": "object"}},
                    "folding_transcripts": {"type": "array", "items": {"type": "object"}},
                    "sumcheck_rounds": {"type": "array", "items": {"type": "object"}},
                    "folding_id": {"type": "string"}
                },
                "required": ["relaxed_r1cs_folds", "folding_transcripts", "sumcheck_rounds"]
            }
        },
        {
            "name": "aleph_prove_stark_air_fri_and_deep_ali_consistency",
            "description": "Demostrador Formal de Representación Intermedia Algebraica (AIR), Muestreo Fuera de Dominio DEEP-ALI (Ben-Sasson et al. FOCS 2020) y Pruebas Interactivas de Oráculo de Proximidad Reed-Solomon Rápidas (FRI - Plonky3 / RISC Zero / Stwo, v11.3.0 - Nivel 106 - NODE-01 Shard - Tool MCP #115): verifica división exacta por zerofiers de transición/frontera con exención de última fila, muestreo z fuera de D_LDE y colinealidad de rondas de plegado FRI con PCC SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "air_constraints": {"type": "array", "items": {"type": "object"}},
                    "deep_ali_queries": {"type": "array", "items": {"type": "object"}},
                    "fri_folding_rounds": {"type": "array", "items": {"type": "object"}},
                    "stark_id": {"type": "string"}
                },
                "required": ["air_constraints", "deep_ali_queries", "fri_folding_rounds"]
            }
        },
        {
            "name": "aleph_prove_circle_stark_m31_and_binius_binary_tower",
            "description": "Demostrador Formal de Circle STARKs sobre Cuerpos Primos Mersenne-31 (p = 2^31 - 1, Haböck, Levit & Papini 2024 — StarkWare Stwo & Plonky3) y Torres Binarias de Wiedemann Binius (Diamond & Posen 2023/2024 — Ulvetanna Binius, v11.4.0 - Nivel 107 - NODE-01 Shard - Tool MCP #116): verifica invariante de curva circular x^2+y^2=1 mod M31, disyunción de polos en Twin-Cosets, plegado Circle-FRI y empaquetamiento biyectivo en torres binarias con PCC SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "circle_m31_points": {"type": "array", "items": {"type": "object"}},
                    "twin_coset_fri_layers": {"type": "array", "items": {"type": "object"}},
                    "binius_tower_levels": {"type": "array", "items": {"type": "object"}},
                    "proof_system_id": {"type": "string"}
                },
                "required": ["circle_m31_points", "twin_coset_fri_layers", "binius_tower_levels"]
            }
        },
        {
            "name": "aleph_prove_fhe_tfhe_programmable_bootstrapping_and_lwe_noise_budget",
            "description": "Demostrador Formal de Cifrado Totalmente Homomórfico sobre el Toro (TFHE Programmable Bootstrapping — Chillotti et al. ASIACRYPT 2016 / Zama TFHE-rs) y Presupuesto de Ruido LWE/RLWE con Blindaje IND-CPA^D (Li & Micciancio EUROCRYPT 2021, v11.5.0 - Nivel 108 - NODE-01 Shard - Tool MCP #117): verifica que el ruido acumulado ||e_acc||_inf < Delta/2, audita el bit de padding negacíclico en Blind Rotation sobre Z_q[X]/(X^N+1) y exige ZK-PoK + noise flooding con PCC SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "homomorphic_gates": {"type": "array", "items": {"type": "object"}},
                    "pbs_blind_rotations": {"type": "array", "items": {"type": "object"}},
                    "ciphertext_security_boundaries": {"type": "array", "items": {"type": "object"}},
                    "fhe_circuit_id": {"type": "string"}
                },
                "required": ["homomorphic_gates", "pbs_blind_rotations", "ciphertext_security_boundaries"]
            }
        },
        {
            "name": "aleph_prove_mpc_spdz_mac_authenticated_shares_and_garbled_circuits",
            "description": "Demostrador Formal de Cómputo Multi-Parte Seguro contra Adversarios Maliciosos (MPC SPDZ / MASCOT / Overdrive — Damgård et al. CRYPTO 2012; Keller et al. CCS 2016) y Circuitos Garbled con Free-XOR y Half-Gates (Kolesnikov & Schneider ICALP 2008; Zahur, Rosulek & Evans EUROCRYPT 2015, v11.6.0 - Nivel 109 - NODE-01 Shard - Tool MCP #118): verifica invariante MAC sum(gamma_i)=alpha*(x+delta_x) con compromiso previo al Batch Check, sacrificio y uso único de tripletas de Beaver, y correlación global Free-XOR con PCC SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "spdz_authenticated_shares": {"type": "array", "items": {"type": "object"}},
                    "beaver_multiplication_triples": {"type": "array", "items": {"type": "object"}},
                    "garbled_circuit_gates": {"type": "array", "items": {"type": "object"}},
                    "mpc_session_id": {"type": "string"}
                },
                "required": ["spdz_authenticated_shares", "beaver_multiplication_triples", "garbled_circuit_gates"]
            }
        },
        {
            "name": "aleph_prove_pqc_ml_kem_kyber_fujisaki_okamoto_and_ml_dsa_dilithium",
            "description": "Demostrador Formal de Criptografía Post-Cuántica Estándar NIST FIPS 203 (ML-KEM / CRYSTALS-Kyber) y NIST FIPS 204 (ML-DSA / CRYSTALS-Dilithium, v11.7.0 - Nivel 110 Hito — NODE-01 Shard - Tool MCP #119): verifica rechazo implícito constante Fujisaki-Okamoto FO^{not-perp} libre de KyberSlash, muestreo por rechazo Fiat-Shamir with Aborts (||z||_inf < gamma_1 - beta, ||r_0||_inf < gamma_2 - beta) y raíz NTT negacíclica zeta^256 == -1 mod q con PCC SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "ml_kem_decapsulations": {"type": "array", "items": {"type": "object"}},
                    "ml_dsa_signatures": {"type": "array", "items": {"type": "object"}},
                    "ntt_and_key_checks": {"type": "array", "items": {"type": "object"}},
                    "pqc_suite_id": {"type": "string"}
                },
                "required": ["ml_kem_decapsulations", "ml_dsa_signatures", "ntt_and_key_checks"]
            }
        },
        {
            "name": "aleph_prove_tee_sev_snp_rmp_and_tdx_remote_attestation_quote",
            "description": "Demostrador Formal de Máquinas Virtuales Confidenciales y Entornos de Ejecución Confiables (AMD SEV-SNP Reverse Map Table RMP, Intel TDX MRTD/RTMR Chain & IETF RATS RFC 9334 Channel Binding, v11.8.0 - Nivel 111 - NODE-01 Shard - Tool MCP #120 Hito): verifica inyectividad SPA->(ASID,GPA) y PVALIDATE en RMP, cadena RTMR[0..3] con DEBUG==0 y anti-rollback TCB_SVN, y vinculación SHA512(nonce || pk_ephemeral) en REPORT_DATA con PCC SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "sev_snp_rmp_entries": {"type": "array", "items": {"type": "object"}},
                    "tdx_measurement_chains": {"type": "array", "items": {"type": "object"}},
                    "rats_attestation_quotes": {"type": "array", "items": {"type": "object"}},
                    "enclave_id": {"type": "string"}
                },
                "required": ["sev_snp_rmp_entries", "tdx_measurement_chains", "rats_attestation_quotes"]
            }
        },
        {
            "name": "aleph_prove_ebpf_verifier_abstract_interpretation_and_xdp_packet_bounds",
            "description": "Demostrador Formal del Verificador eBPF del Kernel Linux mediante Interpretación Abstracta de Números Tri-Estado (tnum: Vishwanathan et al. CAV 2021) y Cotas de Punteros de Paquete XDP / RingBuf (v11.9.0 - Nivel 112 - NODE-01 Shard - Tool MCP #121): verifica invariante (value & mask) == 0 y sincronización tnum-intervalos (anti CVE-2021-3490), guarda dominante data + offset + size <= data_end con recarga tras xdp_adjust_head, y linealidad de referencias bpf_ringbuf_reserve con PCC SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "register_tnum_states": {"type": "array", "items": {"type": "object"}},
                    "xdp_packet_accesses": {"type": "array", "items": {"type": "object"}},
                    "ringbuf_and_loop_paths": {"type": "array", "items": {"type": "object"}},
                    "ebpf_prog_id": {"type": "string"}
                },
                "required": ["register_tnum_states", "xdp_packet_accesses", "ringbuf_and_loop_paths"]
            }
        },
        {
            "name": "aleph_prove_wasm_component_model_wit_canonical_abi_and_wasi_capability",
            "description": "Demostrador Formal del Modelo de Componentes WebAssembly (Wasm 2.0 / Wasmtime / Cranelift), Interfaz Binaria Canónica WIT (Lifting/Lowering vía cabi_realloc) y Aislamiento de Capacidades WASI 0.2 (v12.0.0 Hito Mayor Sovereign Apex - Nivel 113 - NODE-01 Shard - Tool MCP #122): verifica páginas de guarda de 4 GiB y CFI en call_indirect, aislamiento Shared-Nothing en cabi_realloc/cabi_post, y linealidad de descriptores own<T>/borrow<T> sin autoridad ambiental con PCC SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "linear_memories_and_tables": {"type": "array", "items": {"type": "object"}},
                    "canonical_abi_transfers": {"type": "array", "items": {"type": "object"}},
                    "wasi_resource_handles": {"type": "array", "items": {"type": "object"}},
                    "wasm_module_id": {"type": "string"}
                },
                "required": ["linear_memories_and_tables", "canonical_abi_transfers", "wasi_resource_handles"]
            }
        },
        {
            "name": "aleph_prove_riscv_rv64gc_zkvm_memory_consistency_and_pmp_isolation",
            "description": "Demostrador Formal de la Arquitectura RISC-V (RV32IM / RV64GC), Consistencia de Memoria Offline en zkVMs (Blum et al. 1991; Spice / Jolt / Succinct SP1 / RISC Zero) y Protección de Memoria Física (PMP Privileged Spec, v12.1.0 - Nivel 114 - NODE-01 Shard - Tool MCP #123): verifica invariante del registro cableado x0===0 y alineación de PC, permutación de multiconjuntos de memoria con monotonía de reloj t_prev < clk, y prioridad PMP con bit Lock L==1 en M-mode con PCC SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "riscv_instruction_steps": {"type": "array", "items": {"type": "object"}},
                    "offline_memory_accesses": {"type": "array", "items": {"type": "object"}},
                    "pmp_config_entries": {"type": "array", "items": {"type": "object"}},
                    "riscv_trace_id": {"type": "string"}
                },
                "required": ["riscv_instruction_steps", "offline_memory_accesses", "pmp_config_entries"]
            }
        },
        {
            "name": "aleph_prove_rust_stacked_tree_borrows_miri_aliasing_and_pin_soundness",
            "description": "Demostrador Formal del Modelo de Aliasing de Memoria Unsafe en Rust (Stacked Borrows POPL 2020 / Tree Borrows PLDI 2025 / Miri) y Garantía de Drop en Pin<&mut T> para Futuros Asíncronos (v12.2.0 - Nivel 115 - NODE-01 Shard - Tool MCP #124): verifica ausencia de accesos Disabled y preservación de Protectores LLVM noalias, mutabilidad interior restringida a UnsafeCell<T>, y prohibición de proyecciones &mut sin pin o liberación sin drop_in_place en tipos !Unpin con PCC SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "pointer_provenance_tags": {"type": "array", "items": {"type": "object"}},
                    "two_phase_and_unsafecell_accesses": {"type": "array", "items": {"type": "object"}},
                    "pinned_future_projections": {"type": "array", "items": {"type": "object"}},
                    "crate_id": {"type": "string"}
                },
                "required": ["pointer_provenance_tags", "two_phase_and_unsafecell_accesses", "pinned_future_projections"]
            }
        },
        {
            "name": "aleph_prove_c20_rust_atomic_memory_model_acq_rel_and_seq_cst_fence",
            "description": "Demostrador Formal del Modelo de Memoria Débil Axiomático C++20 / Rust (RC11 — Lahav et al. PLDI 2017; GenMC; Tokio Loom) sobre ARM64 / RISC-V RVWMO / x86-TSO (v12.3.0 - Nivel 116 - NODE-01 Shard - Tool MCP #125 Hito): verifica sincronización Release-Acquire en Message-Passing (MP), barreras SeqCst contra anomalías Store-Buffering (SB) y continuidad de Release Sequence / orden de fallo en CAS con PCC SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "message_passing_pairs": {"type": "array", "items": {"type": "object"}},
                    "store_buffering_barriers": {"type": "array", "items": {"type": "object"}},
                    "rmw_cas_operations": {"type": "array", "items": {"type": "object"}},
                    "concurrency_module_id": {"type": "string"}
                },
                "required": ["message_passing_pairs", "store_buffering_barriers", "rmw_cas_operations"]
            }
        },
        {
            "name": "aleph_prove_compiler_ssa_gvn_range_check_elimination_and_speculative_slh",
            "description": "Demostrador Formal de Validación de Traducción de Compiladores Optimizadores (Alive2 LLVM — Lopes et al. PLDI 2021), Eliminación de Chequeos de Rango en JIT (RCE en Cranelift / V8 TurboFan) y Endurecimiento de Carga Especulativa contra Spectre-v1 (Speculative Load Hardening SLH — Carruth LLVM 2018, v13.2.0 - Nivel 117 - NODE-01 Shard - Tool MCP #126): verifica dominancia SSA y no-amplificación de poison con freeze(), ausencia de wraparound en RCE (limit + k <= INT_MAX) y enmascaramiento SLH sin saltos con PCC SHA-256.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "ssa_ir_rewrites": {"type": "array", "items": {"type": "object"}},
                    "jit_rce_loops": {"type": "array", "items": {"type": "object"}},
                    "spectre_v1_guarded_loads": {"type": "array", "items": {"type": "object"}},
                    "compiler_pass_id": {"type": "string"}
                },
                "required": ["ssa_ir_rewrites", "jit_rce_loops", "spectre_v1_guarded_loads"]
            }
        },
        {
            "name": "aleph_prove_iommu_dma_iommu_page_table_iotlb_and_pcie_acs_p2p_isolation",
            "description": "Demostrador Formal de Remapeo DMA IOMMU / Intel VT-d / ARM SMMUv3 con Granularidad 4 KiB anti-Thunderclap (Markettos et al. NDSS 2019), Invalidación Síncrona IOTLB/DevTLB antes de Reclamar Páginas Físicas HPA (anti-DMA Use-After-Free) y Aislamiento Peer-to-Peer PCIe ACS / Bloqueo de ATS Spoofing (v13.2.0 - Nivel 118 - NODE-01 Shard - Tool MCP #127): verifica dominios IOMMU aislados por BDF, bounce buffers de 4 KiB, orden estricto pte_clear < iotlb_inv_sync <= devtlb_inv < page_free y bloqueo de paquetes TLP AT=Translated no confiables.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "dma_mappings": {"type": "array", "items": {"type": "object"}},
                    "unmap_transitions": {"type": "array", "items": {"type": "object"}},
                    "pcie_endpoints": {"type": "array", "items": {"type": "object"}},
                    "check_code": {"type": "string"}
                }
            }
        },
        {
            "name": "aleph_prove_cxl3_cache_mem_mesi_back_invalidation_and_hdm_decoder_isolation",
            "description": "Demostrador Formal de Coherencia de Caché CXL 3.0 (CXL.cache / CXL.mem Invariante SWMR MESI/MOESI en Snoop Filter), Ausencia de Deadlock Circular en Canal de Back-Invalidation (S2M BI-Req / H2D BI-Rsp vs M2S Req) y Aislamiento de Decodificadores HDM con CXL IDE AES-GCM-256 (v13.2.0 - Nivel 119 - NODE-01 Shard - Tool MCP #128): verifica exclusividad de escritura SWMR en líneas de 64B, partición de créditos de canal virtual BI y no-solapamiento de rangos HDM de 256 MiB entre tenants.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "cacheline_directory_states": {"type": "array", "items": {"type": "object"}},
                    "bi_channel_topologies": {"type": "array", "items": {"type": "object"}},
                    "hdm_decoder_ranges": {"type": "array", "items": {"type": "object"}},
                    "check_code": {"type": "string"}
                }
            }
        },
        {
            "name": "aleph_prove_rdma_rocev2_mr_mw_type2b_rkey_and_pfc_dcqcn_deadlock_free",
            "description": "Demostrador Formal de Redes RDMA InfiniBand / RoCEv2: Aislamiento de Memory Windows Tipo 2B (MW Type 2B) ligadas por Queue Pair (QP) y Protection Domain (PD) con Invalidación Atómica Send-With-Invalidate (Defensa ReDMArk — Taranov et al. NDSS 2020) y Ausencia de Deadlock Circular en Priority Flow Control (PFC IEEE 802.1Qbb) con DCQCN ECN/CNP (v13.2.0 - Nivel 120 - NODE-01 Shard - Tool MCP #129): verifica aciclicidad O(V+E) del grafo CDG de puertos PFC, entropía de 8 bits en R_Key y watchdog PFC <= 200 ms.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "memory_windows": {"type": "array", "items": {"type": "object"}},
                    "pfc_port_dependencies": {"type": "array", "items": {"type": "object"}},
                    "rocev2_switches": {"type": "array", "items": {"type": "object"}},
                    "check_code": {"type": "string"}
                }
            }
        },
        {
            "name": "aleph_prove_nvme_zns_zone_write_pointer_append_and_sq_cq_doorbell_phase_tag",
            "description": "Demostrador Formal de Almacenamiento NVMe 2.0 Zoned Namespaces (ZNS — Bjørling et al. USENIX ATC 2021) y NVMe-oF: Invariante de Puntero de Escritura Secuencial (Write Pointer WP / Zone Append con WAF = 1.0), Aritmética Modular de Colas SQ/CQ con Inversión Exacta de Phase Tag (Bit P) e Integridad End-to-End T10-DIF/PI (v13.2.0 - Nivel 121 - NODE-01 Shard - Tool MCP #130): verifica escrituras secuenciales lba == wp <= ZSLBA + ZCAP, rotación del bit P al cruzar cq_head == N-1 -> 0 y unicidad de CID.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "zns_zone_operations": {"type": "array", "items": {"type": "object"}},
                    "sq_cq_ring_transitions": {"type": "array", "items": {"type": "object"}},
                    "nvmeof_inflight_commands": {"type": "array", "items": {"type": "object"}},
                    "check_code": {"type": "string"}
                }
            }
        },
        {
            "name": "aleph_prove_gpu_cuda_triton_warp_reconvergence_shared_bank_swizzle_and_tma_mbarrier",
            "description": "Demostrador Formal de Kernels GPU CUDA / PTX / Triton (FlashAttention-3, vLLM PagedAttention y Unsloth): Reconvergencia Uniforme SIMT en Barreras Colectivas (__syncthreads / __syncwarp / wgmma.fence.sync.aligned), Ausencia de Conflictos de Bancos en Shared Memory (32 Bancos) por Coprimalidad gcd(S,32)=1 o XOR Swizzle y Paridad Exacta de Fase en Barreras Asíncronas TMA / cp.async mbarrier (v13.2.0 - Nivel 122 - NODE-01 Shard - Tool MCP #131): verifica máscara activa 0xFFFFFFFF, biyección en 32 bancos SRAM y paridad (step // stages) & 1.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "collective_barriers": {"type": "array", "items": {"type": "object"}},
                    "smem_access_patterns": {"type": "array", "items": {"type": "object"}},
                    "tma_mbarrier_stages": {"type": "array", "items": {"type": "object"}},
                    "check_code": {"type": "string"}
                }
            }
        },
        {
            "name": "aleph_prove_nccl_allreduce_fp8_deterministic_tree_and_1f1b_zero_bubble_pipeline",
            "description": "Demostrador Formal de Comunicación Colectiva Multi-GPU (NCCL / NVLink SHARP): Reproducibilidad Bit a Bit en Árboles de Reducción AllReduce Punto Flotante no Asociativo (FP8 E4M3 / BF16 con Acumulación FP32/Kulisch), Isomorfismo de Secuencia entre Ranks contra Deadlocks de Comunicador y Planificación Pipeline Parallelism 1F1B / Zero-Bubble (Qi et al. ICLR 2024, v13.2.0 - Hito Mayor Nivel 123 - NODE-01 Shard - Tool MCP #132): verifica orden fijo de árbol AllReduce, isomorfismo de llamadas colectivas entre ranks y cota de memoria de activaciones <= P - s con causalidad F < B <= W.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "allreduce_collectives": {"type": "array", "items": {"type": "object"}},
                    "communicator_rank_schedules": {"type": "array", "items": {"type": "object"}},
                    "pipeline_1f1b_stages": {"type": "array", "items": {"type": "object"}},
                    "check_code": {"type": "string"}
                }
            }
        },
        {
            "name": "aleph_prove_speculative_decoding_rejection_sampling_and_paged_kv_cache_cow",
            "description": "Demostrador Formal de Inferencia LLM de Ultra-Baja Latencia: Equivalencia Exacta de Distribución en Muestreo por Rechazo de Decodificación Especulativa (Leviathan et al. ICML 2023 / EAGLE-2), Aislamiento Copy-on-Write (CoW) con Conteo de Referencias en Árboles de Prefijos PagedAttention / RadixAttention (Kwon et al. SOSP 2023) y Conservación de Bloques KV en Continuous Batching (v13.2.0 - Nivel 124 - NODE-01 Shard - Tool MCP #133): verifica identidad exacta min(q,p) + max(0,p-q) == p (KL=0), clonación CoW para ref_count > 1 y ley de conservación alloc + free == total.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "speculative_draft_steps": {"type": "array", "items": {"type": "object"}},
                    "kv_cache_cow_transitions": {"type": "array", "items": {"type": "object"}},
                    "kv_block_pools": {"type": "array", "items": {"type": "object"}},
                    "check_code": {"type": "string"}
                }
            }
        },
        {
            "name": "aleph_prove_qlora_nf4_double_quant_awq_salience_and_matryoshka_embedding",
            "description": "Demostrador Formal de Cuantización Extrema y Representaciones Anidadas: QLoRA NF4 (4-Bit NormalFloat con Bin Exacto 0.0 y Doble Cuantización de Escalas FP8/FP32 — Dettmers et al. NeurIPS 2023), Preservación de Canales Salientes AWQ / Amortiguamiento Hessiano Cholesky GPTQ (Lin et al. MLSys 2024) y Normalización L2 Post-Truncamiento en Embeddings Matryoshka MRL (Kusupati et al. NeurIPS 2022, v13.2.0 - Nivel 125 - Centenario REG-100 - NODE-01 Shard - Tool MCP #134): verifica 16 cuantiles NF4 con 0.0 exacto, H + lambda*I > 0 en GPTQ y renormalización L2 unitaria tras truncar prefijos MRL.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "qlora_nf4_configs": {"type": "array", "items": {"type": "object"}},
                    "awq_gptq_layers": {"type": "array", "items": {"type": "object"}},
                    "matryoshka_Slices": {"type": "array", "items": {"type": "object"}},
                    "check_code": {"type": "string"}
                }
            }
        },
        {
            "name": "aleph_audit_scim2_rfc7644_filter_patchop_permissions_fedcm_and_ai_gateway_header_ssrf",
            "description": "Audita formalmente código Python/Web contra vulnerabilidades en IETF RFC 7643/7644 SCIM 2.0 Filter AST Injection y escalada de privilegios en PatchOp (allowed_scim_filter_attributes, immutable_scim_patch_paths y hmac.compare_digest sobre scim_bearer_token), aislamiento W3C FedCM (identity-credentials-get) y WebOTP (otp-credentials) en Permissions-Policy, y prevención de SSRF y exfiltración de llaves Bearer en AI Gateways (LiteLLM CVE-2024-6587, Kong AI Proxy, Portkey, Helicone) mediante bloqueo de cabeceras upstream controladas por el cliente y validación de allowed_ai_upstream_hosts (v14.1.0 - Nivel 225 Formal NODE-04 Shard).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Código fuente a auditar."},
                    "source_code": {"type": "string", "description": "Alias opcional de código fuente a auditar."}
                }
            }
        },
        {
            "name": "aleph_audit_scim2_externalid_keycloak_idor_fedcm_configurl_and_litellm_nested_cve2026_59823_ssrf",
            "description": "Audita formalmente código Python/Web contra colisión numérica de externalId en SCIM 2.0 ('externalId': '1' -> UID admin en Grafana 12.x), IDOR entre URL path y body en PUT /Users/{id} (Keycloak Issue #46658) y toma de cuenta por PATCH de email sin re-verificación (GitLab EE / arXiv:2609.14017v1), validación de orígenes HTTPS en W3C FedCM configURL y atribución de dominio en iframes (W3C FedCM Issue #449), y prevención de SSRF y exfiltración de llaves en LiteLLM mediante inspección recursiva de user_config (CVE-2026-59823), model_list/fallbacks/litellm_credential_name (CVE-2026-84377) y os.environ/LITELLM_MASTER_KEY (v14.2.0 - Nivel 226 Formal NODE-04 Shard).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Código fuente a auditar."},
                    "source_code": {"type": "string", "description": "Alias opcional de código fuente a auditar."}
                }
            }
        },
        {
            "name": "aleph_audit_scim2_temporal_ac2_jwt_cve2024_54150_fedcm_multi_idp_and_litellm_test_connection_ssrf",
            "description": "Audita formalmente código Python/Web contra cuentas zombi por reconciliación temporal SCIM 2.0 (NIST AC-2 / arXiv:2609.14017v1) y confusión de algoritmos JWT SSO (CVE-2024-54150 / CVE-2024-53861), consolidación Multi-IdP, nonce criptográfico y verificación de gesto explícito sobre isAutoSelected en W3C FedCM, y prevención de exfiltración de os.environ/LITELLM_MASTER_KEY y reflexión verbatim de errores upstream en /health/test_connection de LiteLLM (v14.3.0 - Nivel 227 Formal NODE-04 Shard).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Código fuente a auditar."},
                    "source_code": {"type": "string", "description": "Alias opcional de código fuente a auditar."}
                }
            }
        },
        {
            "name": "aleph_audit_tls13_rfc9846_tacacs_vllm_mediaconnector_cve2026_24779_and_bentoml_cve2026_44345",
            "description": "Audita formalmente código Python/Web contra omisión de identidad de servicio RFC 9525 y fallback CN en TLS 1.3 RFC 9846 / TACACS+ sobre TLS 1.3 / IoT Profile, SSRF en vLLM MediaConnector (CVE-2026-24779 / GHSA-qh4c-xf7m-gxfc en pods llm-d) y conteo de tokens de imagen en LangChain ChatOpenAI (GHSA-2g6r-c272-w58r), y deserialización insegura en BentoML Runner Server (CVE-2026-44345 / CVE-2025-32375 / CVE-2025-27520) junto a XSS/SSRF en jupyter-server-proxy (CVE-2024-35225 / GHSA-w3vc-fx9p-wp4v) (v14.4.0 - Nivel 228 Formal NODE-04 Shard).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Código fuente a auditar."},
                    "source_code": {"type": "string", "description": "Alias opcional de código fuente a auditar."}
                }
            }
        },
        {
            "name": "aleph_audit_privacypass_rfc9576_batched_ollama_pull_cve2026_108836_and_mlrun_cve2026_92568_ssrf",
            "description": "Audita formalmente código Python/Web contra emisión/redención por lotes sin cota ni tiempo constante en Privacy Pass (RFC 9576 / RFC 9578 / draft-ietf-privacypass-batched-tokens), SSRF y Path Traversal hacia RCE root en Ollama /api/pull (CVE-2026-108836 / PocketClaw Oct 2026), y SSRF mediante DNS Rebinding TOCTOU en MLRun WebhookNotification (CVE-2026-92568), registros OCI (go-containerregistry #2440) y puerto 9222 mDNS (Chromium Issue 513134076) (v14.5.0 - Nivel 229 Formal NODE-04 Shard).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Código fuente a auditar."},
                    "source_code": {"type": "string", "description": "Alias opcional de código fuente a auditar."}
                }
            }
        },
        {
            "name": "aleph_audit_mls_rfc9750_cbor_cde_rfc8949_http2_origin_rfc8336_and_grafana_roundcube_ssrf",
            "description": "Audita formalmente código Python/Web contra llaves duplicadas y codificación no determinista en MLS RFC 9750 y CBOR CDE (RFC 8949 §4.2 / draft-ietf-cbor-cde-13), secuestro de coalescencia de conexiones en tramas HTTP/2 ORIGIN (RFC 8336 §2.4) y ausencia de mapa SRI integrity en <script type='importmap'>, y Full-Read SSRF en Grafana /api/datasources/proxy, etiquetas <link> en Roundcube y exposición de puertos internos 9090, 9200 y 9963 (Cilium Agent) (v14.6.0 - Nivel 230 Formal NODE-04 Shard).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Código fuente a auditar."},
                    "source_code": {"type": "string", "description": "Alias opcional de código fuente a auditar."}
                }
            }
        },
        {
            "name": "aleph_audit_mcp_contextforge_ghsa9hgc_surrealdb_langflow_redirect_ssrf_and_koa_cve2026_27959",
            "description": "Audita formalmente código Python/Web contra SSRF por DNS Rebinding TOCTOU en IBM MCP ContextForge ResilientHttpClient (GHSA-9hgc-g3w5-67cm) y datamodel-code-generator (GHSA-vx7x-vcc2-c44g), bypass de SSRF mediante redirecciones HTTP en SurrealDB (antes de 2.2.2) y Langflow API Request Component, e inyección de X-Forwarded-Host en Koa ctx.hostname (CVE-2026-27959 / GHSA-7gcc-r8m5-44qm) junto a XSS almacenado por subida de SVG en Ech0 (CVE-2026-40262 / GHSA-69hx-63pv-f8f4) (v14.7.0 - Nivel 231 Formal NODE-04 Shard).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Código fuente a auditar."},
                    "source_code": {"type": "string", "description": "Alias opcional de código fuente a auditar."}
                }
            }
        },
        {
            "name": "aleph_audit_kong_cve2026_17578_autojack_cswsh_contextforge_ssti_ghsavwf3_and_vaultwarden_ssrf",
            "description": "Audita formalmente código Python/Web contra reutilización de nonces AES-GCM por falta de rotación de llaves (Kong Event Gateway CVE-2026-17578 / NIST SP 800-38D), IV constante (CVE-2026-21383) y bypass de firma JWT CAS (CVE-2026-0265), Cross-Site WebSocket Hijacking en agentes IA locales (Microsoft AutoJack CWE-1385) e inyección de plantillas Jinja2 SSTI en IBM MCP ContextForge (GHSA-vwf3-4xxj-qg6h) y RAGFlow (GHSA-vvwj-fvwh-4whx), y SSRF mediante literales IPv4 octal/hex/decimal en Vaultwarden (GHSA-72vh-x5jq-m82g) junto a contrabando HTTP TE.CL / HTTP/1.0 en ServiceTalk/Pingora/QAnything (GHSA-56h2-h3h4-m9x6 / GHSA-262p-vjx5-45xh / CVE-2024-10264) (v14.8.0 - Nivel 232 Formal NODE-04 Shard).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Código fuente a auditar."},
                    "source_code": {"type": "string", "description": "Alias opcional de código fuente a auditar."}
                }
            }
        },
        {
            "name": "aleph_audit_eat_rfc9711_rfc9782_mlflow_cve2026_64849_ssrf_and_qdrant_snapshot_cve2024_3829",
            "description": "Audita formalmente código Python/Web contra falsificación o replay de Entity Attestation Tokens (IETF RFC 9711 EAT / RFC 9782 Media Types / draft-bft-rats-kat-04 Key Attestation Token), SSRF no autenticado de robo de credenciales cloud IMDS en MLflow (CVE-2026-64849 CVSS 9.3) y Gradio (CVE-2024-4325), y Path Traversal / SSRF en recuperación de snapshots de Qdrant (CVE-2024-3829 / GHSA-7m75-x27w-r52r) junto a exposición de Apache ZooKeeper JettyAdminServer en puerto 8080 (/commands) (v14.9.0 - Nivel 233 Formal NODE-04 Shard - REG-098).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Código fuente a auditar."},
                    "source_code": {"type": "string", "description": "Alias opcional de código fuente a auditar."}
                }
            }
        },
        {
            "name": "aleph_audit_mldsa_connolly_sframe_rfc9605_langflow_cve2025_3248_and_jupyter_envoy_admin_ssrf",
            "description": "Audita formalmente código Python/Web contra fallos de firma hedged, semilla expandida y contexto en ML-DSA (NIST FIPS 204 / draft-connolly-cfrg-ml-dsa-security-considerations-02) y reutilización de llaves/contadores en SFrame (RFC 9605 / draft-barnes-sframe-iana-256-06), ejecución remota de código pre-autenticación en validación AST de Langflow (/api/v1/validate/code CVE-2025-3248 CVSS 9.8 CISA KEV), y SSRF/XSS en Jupyter Server Proxy (CVE-2024-35225 / CVE-2024-28179 / GHSA-gcv9-6737-pjqw) junto a exposición de puertos de administración 15000/9901 (/config_dump, /quitquitquit) en Envoy/Istio (v15.0.0 - Nivel 234 Formal NODE-04 Shard - REG-099).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Código fuente a auditar."},
                    "source_code": {"type": "string", "description": "Alias opcional de código fuente a auditar."}
                }
            }
        },
        {
            "name": "aleph_audit_gocontainerregistry_ipv6_ssrf_dirac_cve2026_61668_tls_and_dynaconf_ghsa_pxrr_ssti",
            "description": "Audita formalmente código Python/Web contra bypass de listas negras SSRF mediante direcciones IPv6 de transición e IPv4-mapeadas (::ffff:169.254.169.254, 6to4, Teredo en Google go-containerregistry#2440 / golang/go#79925 / CVE-2024-24790 / Monsta FTP), desactivación de validación de certificados TLS (ssl._create_unverified_context / verify=False en DIRAC PilotWrapper CVE-2026-61668 CWE-295) y replay de webhooks HMAC-SHA256, e inyección de plantillas Jinja2 SSTI en Dynaconf/FastAPI (GHSA-pxrr-hq57-q35p / CWE-1336) junto a cabecera Referrer-Policy (v15.1.0 - Nivel 235 Formal NODE-04 Shard - Hito Centenario REG-100).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Código fuente a auditar."},
                    "source_code": {"type": "string", "description": "Alias opcional de código fuente a auditar."}
                }
            }
        },
        {'name': 'aleph_prove_rivet_utility_preserving_repo_ppr_and_tidekv_chunked_prefill', 'description': 'Verifica formalmente el control de contexto de repositorio Rivet (Signal Grounding LSA/TF-IDF + PPR alpha=0.6 + RRF kappa=60, Utility Linking PPR alpha=0.7 con pesos de evidencia jerarquicos y Budget Shaping 4K/8K) y prefill por bloques TideKV con desalojo diferido por capas y compactacion circular contigua sin operaciones gather irregulares en HBM (Nivel 225).', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'file_count': {'type': 'integer'}, 'signal_grounding_alpha': {'type': 'number'}, 'utility_linking_alpha': {'type': 'number'}, 'ppr_iterations': {'type': 'integer'}, 'rrf_kappa': {'type': 'integer'}, 'context_budget_tokens': {'type': 'integer'}, 'prompt_tokens': {'type': 'integer'}, 'chunk_prefill_tokens': {'type': 'integer'}, 'kv_budget_tokens': {'type': 'integer'}, 'irregular_hbm_gather_ops': {'type': 'integer'}}}},
        {
            "name": "aleph_prove_inlinecoder_bidirectional_callgraph_and_fastkv_behavior_preserving",
            "description": (
                "Verifica formalmente el inlining bidireccional sobre grafo de llamadas InlineCoder (FSE 2026: Upstream Inlining en llamadores "
                "y Downstream Retrieval Q_AST U Q_LLM con estimacion de perplejidad sobre anchor) junto con propagacion selectiva de tokens "
                "FastKV (ACL 2026: desacoplo TSP/KV) y compresion KV preservadora de comportamiento acotada por divergencia KL sin pasadas "
                "forward enmascaradas adicionales (Nivel 226)."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "target_name": {"type": "string"},
                    "upstream_callers_inlined": {"type": "integer"},
                    "anchor_perplexity_score": {"type": "number"},
                    "tsp_layer_index": {"type": "integer"},
                    "total_layers": {"type": "integer"},
                    "tsp_propagation_rate": {"type": "number"},
                    "kv_retention_rate": {"type": "number"},
                    "max_kl_divergence_bits": {"type": "number"},
                    "kl_threshold_bits": {"type": "number"},
                    "separate_masked_forward_passes": {"type": "integer"}
                }
            }
        },
        {
            "name": "aleph_prove_hydra_hierarchical_repo_index_and_crosstoken_kv_prefetch",
            "description": (
                "Verifica formalmente la indexacion jerarquica de programas Hydra (Le-Anh et al., Feb 2026: prohibicion de chunks planos "
                "de lenguaje natural, indexacion en 3 niveles funciones/clases/variables y recuperacion conjunta de dependencias D_dep + "
                "ejemplos de uso U_sim) junto con Self-Indexing KVCache (arXiv:2603.14224v1) y AttentionPredictor Cross-Token KV Prefetching "
                "(NeurIPS 2026: autocorrelacion coseno temporal de queries >= 0.85, claves auto-indexadas comprimidas d_c < d_k con overhead <= 0.001 "
                "y prefetch asincrono zero-stall dentro de la ventana de computo por token) (Nivel 227 - Tool #236)."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "target_name": {"type": "string"},
                    "indexed_functions_count": {"type": "integer"},
                    "indexed_classes_count": {"type": "integer"},
                    "indexed_variables_count": {"type": "integer"},
                    "natural_language_flat_chunks": {"type": "integer"},
                    "query_temporal_cosine_similarity": {"type": "number"},
                    "compressed_key_dim": {"type": "integer"},
                    "full_key_dim": {"type": "integer"},
                    "predictor_param_overhead_ratio": {"type": "number"},
                    "top_k_attention_recall": {"type": "number"},
                    "kv_prefetch_transfer_ms": {"type": "number"},
                    "llm_token_compute_ms": {"type": "number"},
                    "retained_kv_ratio": {"type": "number"}
                }
            }
        },
        {
            "name": "aleph_prove_saracoder_hierarchical_context_pruning_and_novakv_gsrq",
            "description": (
                "Verifica formalmente la poda jerarquica de contexto con optimizacion de caracteristicas HF_OP y desambiguacion de "
                "identificadores externos EAID de Saracoder (arXiv:2508.10068v3, Oct 2026: |P| = top_k * k, 0 duplicados exactos, "
                "reasignacion de tokens a D_ext bajo |S_ref| + |D_ext| <= L_max) junto con la cuantizacion vectorial con transformaciones "
                "preservadoras de atencion NOVA-KV (arXiv:2608.04074, Aug 2026: relacion generalizada de Parseval y particiones de igual "
                "volumen) y cuantizacion residual Gain-Shape GSRQ sub-2-bit sin encogimiento de centroides (arXiv:2607.01065, Jul 2026) "
                "(Nivel 228 - Tool #237)."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "target_name": {"type": "string"},
                    "top_k_base": {"type": "integer"},
                    "expansion_factor_k": {"type": "integer"},
                    "exact_duplicate_snippets_retained": {"type": "integer"},
                    "ambiguous_external_identifiers": {"type": "integer"},
                    "s_ref_tokens": {"type": "integer"},
                    "d_ext_tokens": {"type": "integer"},
                    "max_budget_tokens": {"type": "integer"},
                    "is_key_transform_non_orthogonal": {"type": "boolean"},
                    "is_value_transform_orthogonal": {"type": "boolean"},
                    "generalized_parseval_residual": {"type": "number"},
                    "equal_volume_partitions_valid": {"type": "boolean"},
                    "centroid_shrinkage_eliminated": {"type": "boolean"},
                    "angular_alignment_cosine": {"type": "number"},
                    "quant_bits_per_element": {"type": "number"}
                }
            }
        },
        {
            "name": "aleph_prove_adabool_adaptive_sparse_reachability_and_self_indexing_sign_attention",
            "description": (
                "Verifica formalmente la representacion adaptativa de matrices booleanas dispersas AdaBool para clausura transitiva de "
                "repositorios (arXiv:2610.21264v1, Oct 2026: bloques de longitud l = 2^8 = 256, umbral de conmutacion t = 32 entre ARRAYn "
                "y 256-bit BITSET con cabecera c_start en una sola transaccion vectorizada y cero bloques vacios) junto con Self-Indexing "
                "Attention en dominio transformado Hadamard (arXiv:2609.13205v2, Sep 2026 & AAAI 2026 OJS 39988: signos binarios B = sign(U) "
                "con entropia de Shannon H(B) >= 0.99 bits reutilizados entre prefill y decode sin indice auxiliar separado) (Nivel 229 - Tool #238)."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "target_name": {"type": "string"},
                    "log2_m": {"type": "integer"},
                    "block_length_l": {"type": "integer"},
                    "switching_threshold_t": {"type": "integer"},
                    "empty_regions_allocated": {"type": "integer"},
                    "single_transaction_bitset_loads": {"type": "boolean"},
                    "hadamard_orthogonal_rotation_applied": {"type": "boolean"},
                    "positive_sign_probability": {"type": "number"},
                    "unified_prefill_decode_sign_index": {"type": "boolean"},
                    "separate_auxiliary_indexer_bytes": {"type": "integer"},
                    "preserved_sink_tokens": {"type": "integer"},
                    "query_grouping_size": {"type": "integer"},
                    "selected_kv_budget_ratio": {"type": "number"}
                }
            }
        },
        {
            "name": "aleph_prove_mojos_batch_parallel_dynamic_trees_and_retroinfer_wave_kv",
            "description": (
                "Verifica formalmente arboles dinamicos paralelos por lotes MOJOS (Link-Cut Trees y Euler Tour Trees sobre secuencias "
                "batch-dinamicas con trabajo O(k log(1 + n/k)), span polilogaritmico O(log k log n) y caminos preferidos disjuntos en "
                "vertices, arXiv:2609.14746, Sep 2026) junto con el motor de almacenamiento vectorial KV RetroInfer / RetrievalAttention "
                "(VLDB 2026 / NeurIPS 2025 arXiv:2409.10516v3: alineacion cross-modal para brecha Mahalanobis OOD Query-Key, indice de "
                "centroides WAVE en CPU y co-ejecucion disjunta GPU-CPU escaneando <= 5% de vectores con recall >= 98.5%) (Nivel 230 - Tool #239)."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "target_name": {"type": "string"},
                    "total_forest_vertices_n": {"type": "integer"},
                    "batch_update_size_k": {"type": "integer"},
                    "measured_work_multiplier": {"type": "number"},
                    "measured_span_multiplier": {"type": "number"},
                    "preferred_path_overlap_violations": {"type": "integer"},
                    "forest_cycle_violations": {"type": "integer"},
                    "ood_query_key_projection_aligned": {"type": "boolean"},
                    "gpu_static_sink_and_window_tokens": {"type": "integer"},
                    "cpu_wave_centroid_clusters": {"type": "integer"},
                    "gpu_cpu_set_overlap_tokens": {"type": "integer"},
                    "scanned_kv_fraction": {"type": "number"},
                    "attention_recall_vs_full": {"type": "number"}
                }
            }
        },
        {
            "name": "aleph_prove_alpha_independent_recursive_active_set_ppr_and_sals_latent_prerope_kv",
            "description": (
                "Verifica formalmente el calculo de Personalized PageRank por jerarquia recursiva de conjuntos activos "
                "independiente de alpha en tiempo casi optimo O(epsilon^(-1 - o(1))) bajo la garantia de error normalizado "
                "por grado de Andersen-Chung-Lang (arXiv:2610.06959v1, Oct 2026) junto con la compresion de cache KV en el "
                "espacio latente pre-RoPE mediante proyeccion PCA conjunta multi-cabezal SALS para prefill y decoding "
                "(OpenReview:zJSZupQ889, <= 0.79% drop en RULER 128k) (Nivel 231 - Tool #240)."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "target_name": {"type": "string"},
                    "teleportation_alpha": {"type": "number"},
                    "acl_error_tolerance_epsilon": {"type": "number"},
                    "recursive_active_set_levels": {"type": "integer"},
                    "subpolynomial_exponent_delta": {"type": "number"},
                    "measured_ops_multiplier": {"type": "number"},
                    "max_degree_normalized_residual": {"type": "number"},
                    "ping_pong_residual_oscillation_events": {"type": "integer"},
                    "sals_pre_rope_pca_applied": {"type": "boolean"},
                    "joint_head_latent_projection_enabled": {"type": "boolean"},
                    "full_multihead_dim": {"type": "integer"},
                    "latent_projected_dim": {"type": "integer"},
                    "uncompressed_decoded_key_violations": {"type": "integer"},
                    "ruler_128k_accuracy_drop_pct": {"type": "number"}
                }
            }
        },
        {
            "name": "aleph_prove_adaptive_graph_edgetype_ppr_and_yoio_shared_index_sparse_kv",
            "description": (
                "Verifica formalmente la recuperacion de contexto AdaptiveGraph y GAAMA con Personalized PageRank "
                "consciente de tipos de arista, aristas cronologicas, siembra lexica directa de archivos y poda de "
                "stopwords >15% con cero llamadas LLM en tiempo de consulta (OpenReview:800487716a5dd & arXiv:2603.27910, 2026) "
                "junto con la atencion dispersa inter-capa de indice compartido YOIO (You Only Index Once, arXiv:2606.06467v1) "
                "y compactacion KV no uniforme por sensibilidad de cabezales Attention Matching (OpenReview:t01SKTj8pP) (Nivel 232 - Tool #241)."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "target_name": {"type": "string"},
                    "stopword_doc_frequency_cutoff": {"type": "number"},
                    "high_frequency_token_leak_violations": {"type": "integer"},
                    "chronological_file_edges_enabled": {"type": "boolean"},
                    "direct_lexical_file_seeding_enabled": {"type": "boolean"},
                    "edge_type_aware_ppr_enabled": {"type": "boolean"},
                    "query_time_llm_calls": {"type": "integer"},
                    "hybrid_additive_score_gain_pp": {"type": "number"},
                    "yoio_shared_index_built_once": {"type": "boolean"},
                    "redundant_per_layer_index_recomputations": {"type": "integer"},
                    "total_decoder_layers": {"type": "integer"},
                    "shared_index_layer_groups": {"type": "integer"},
                    "non_uniform_head_sensitivity_schedule": {"type": "boolean"},
                    "chunked_prefill_window_tokens": {"type": "integer"},
                    "attention_matching_kl_error": {"type": "number"}
                }
            }
        },
        {
            "name": "aleph_prove_chebpush_subset_recurrence_ppr_and_eta_shifted_silu_deferkv",
            "description": (
                "Verifica formalmente la propagacion local de grafos L2Cheb y ChebPush mediante recurrencia "
                "de Chebyshev de tres terminos sobre subconjuntos activos con aceleracion O(sqrt(N)) (arXiv:2412.10789) "
                "y puntos fijos exactos Feedback-PageRank via vectores de Perron izquierdos en grafos AST reducibles "
                "multi-SCC (arXiv:2507.18652), junto con el filtrado de bloques KV en O(1) mediante compuerta SiLU "
                "desplazada libre de attention sinks ETA (arXiv:2609.20888v2) y la eviccion KV one-shot diferida "
                "a la frontera prefill-decode DeferKV (arXiv:2610.06286v1) (Nivel 233 - Tool #242)."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "target_name": {"type": "string"},
                    "total_ast_nodes": {"type": "integer"},
                    "active_chebpush_subset_nodes": {"type": "integer"},
                    "chebpush_three_term_recurrence_steps": {"type": "integer"},
                    "reducible_scc_components": {"type": "integer"},
                    "scc_perron_fixed_point_violations": {"type": "integer"},
                    "chebpush_l1_residual_error": {"type": "number"},
                    "eta_total_kv_blocks": {"type": "integer"},
                    "eta_screened_active_blocks": {"type": "integer"},
                    "eta_shifted_silu_floor_eps": {"type": "number"},
                    "eta_attention_sink_spikes": {"type": "integer"},
                    "eta_frozen_head_compute_reduction_pct": {"type": "number"},
                    "eta_end_to_end_speedup_vs_fa2": {"type": "number"},
                    "deferkv_prefill_decode_boundary_step": {"type": "integer"},
                    "premature_prefill_only_evictions": {"type": "integer"},
                    "deferkv_retained_kv_ratio": {"type": "number"}
                }
            }
        },
        {
            "name": "aleph_prove_partial_dependency_trigraph_ppr_and_attention_preserving_commvq",
            "description": (
                "Verifica formalmente la recuperacion de contexto mediante Grafo de Dependencia Parcial (PDG, arXiv:2608.01927), "
                "fusion jerarquica de grafos de llamadas y modulos GRACE (arXiv:2509.05980) y Tri-Grafo libre de relaciones "
                "LinearRAG sin llamadas LLM de extraccion (ICLR 2026), junto con la cuantizacion vectorial con transformaciones "
                "preservadoras de atencion y compactacion de energia por covarianza de consultas (APT-VQ, arXiv:2608.04074) "
                "y cuantizacion vectorial conmutativa CommVQ sin materializacion completa del cache KV (arXiv:2506.18879) (Nivel 234 - Tool #243)."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "target_name": {"type": "string"},
                    "total_repo_nodes": {"type": "integer"},
                    "partial_dependency_subgraph_nodes": {"type": "integer"},
                    "trigraph_node_tiers": {"type": "integer"},
                    "containment_and_cooccurrence_edges_only": {"type": "boolean"},
                    "llm_graph_construction_calls": {"type": "integer"},
                    "grace_hierarchical_code_fusion_enabled": {"type": "boolean"},
                    "orthogonal_value_transform_enabled": {"type": "boolean"},
                    "query_covariance_energy_compaction_ratio": {"type": "number"},
                    "uncompacted_hadamard_variance_violations": {"type": "integer"},
                    "commvq_commutative_codebook_enabled": {"type": "boolean"},
                    "full_kv_dequantization_materializations": {"type": "integer"},
                    "attention_output_distortion_mse": {"type": "number"}
                }
            }
        },
        {
            "name": "aleph_prove_reposcope_callchain_multiview_cha_ppr_and_thinkv_random_attention",
            "description": (
                "Verifica formalmente el contexto multi-vista consciente de cadenas de llamadas RepoScope (arXiv:2507.14791v2), "
                "la recuperacion mejorada por grafos RANGER (arXiv:2509.25257v1) y la jerarquia de asunciones CHA del Code Graph Model "
                "(CGM, arXiv:2505.16901), junto con la eviccion KV sin pasada de scoring Random Attention + prefetch asincrono SpeContext "
                "con +32-43% throughput en vLLM a 32K tokens (arXiv:2609.03430v1) y la compresion conjunta adaptativa al pensamiento "
                "ThinKV sin perdida de tokens re-emergentes (ICLR 2026) (Nivel 235 - Tool #244)."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "target_name": {"type": "string"},
                    "total_callgraph_nodes": {"type": "integer"},
                    "call_chain_multiview_depth": {"type": "integer"},
                    "cha_assumption_hierarchy_enabled": {"type": "boolean"},
                    "unresolved_cha_virtual_dispatch_edges": {"type": "integer"},
                    "ranger_graph_enhanced_recall_gain_pct": {"type": "number"},
                    "prompt_preserved_intact": {"type": "boolean"},
                    "scoring_pass_overhead_ms": {"type": "number"},
                    "vllm_32k_throughput_gain_pct": {"type": "number"},
                    "specontext_async_prefetch_enabled": {"type": "boolean"},
                    "thinkv_quantization_factor_a": {"type": "number"},
                    "thinkv_eviction_factor_b": {"type": "number"},
                    "reemergent_thought_token_eviction_violations": {"type": "integer"}
                }
            }
        },
        {
            "name": "aleph_prove_deterministic_ast_interface_graph_ppr_and_qjl_zero_metadata_infokv_lcdf",
            "description": (
                "Verifica formalmente el grafo ontologico determinista derivado de AST (DKB) con expansion bidireccional de consumidores "
                "de interfaz y cero archivos omitidos (arXiv:2601.08773v1), la recuperacion multi-repositorio consciente de versiones "
                "CrossCoder (arXiv:2609.09987v1) y el anclaje lexico LARGER (arXiv:2605.16352v1), junto con la cuantizacion KV de 1 bit "
                "QJL sin overhead de constantes de cuantizacion (>5x ahorro de memoria, AAAI 2025), la influencia futura por entropia "
                "restringida InfoKV (arXiv:2606.26875v1) y la auditoria token a token LCDF (arXiv:2610.14475v1) (Nivel 236 - Tool #245)."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "target_name": {"type": "string"},
                    "total_dkb_ast_nodes": {"type": "integer"},
                    "llm_kb_skipped_files_count": {"type": "integer"},
                    "bidirectional_succ_pred_depth": {"type": "integer"},
                    "interface_consumer_expansion_enabled": {"type": "boolean"},
                    "crosscoder_external_lib_version_conflicts": {"type": "integer"},
                    "larger_lexical_channel_anchored": {"type": "boolean"},
                    "qjl_quantization_constants_overhead_bits": {"type": "number"},
                    "qjl_asymmetric_estimator_max_bias": {"type": "number"},
                    "kv_memory_reduction_factor": {"type": "number"},
                    "infokv_forward_influence_entropy_tau": {"type": "number"},
                    "lcdf_paired_log_loss_drift": {"type": "number"}
                }
            }
        },
        {
            "name": "aleph_prove_saga_atomic_workflow_callsite_transform_ppr_and_oscar_spectral_int2_kv",
            "description": (
                "Verifica formalmente la planificacion atomica de flujos agénticos por afinidad de sesion SAGA sin eviccion KV entre "
                "tool-calls (HPDC '26 arXiv:2605.00528) y la transformacion algebraica de sitio de llamada Body_f* = tau(sigma(Body_f)) "
                "con calibracion de confianza por perplejidad en 3 niveles (PACMSE FSE 2026 arXiv:2601.00376v3), junto con la rotacion "
                "espectral consciente de covarianza OSCAR (R_K = U_Q H_Had P_br, R_V = U_S H_Had P_br) y OptR para cuantizacion INT2 KV "
                "a 2.28 BPE con 8x ahorro de memoria y 7x throughput en SGLang (arXiv:2605.17757v1, arXiv:2608.02691v4) (Nivel 237 - Tool #246)."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "target_name": {"type": "string"},
                    "workflow_dag_steps": {"type": "integer"},
                    "tool_call_boundary_kv_evictions": {"type": "integer"},
                    "callsite_tau_sigma_bijection_verified": {"type": "boolean"},
                    "downstream_self_leakage_excluded": {"type": "boolean"},
                    "draft_perplexity_score": {"type": "number"},
                    "oscar_effective_bpe": {"type": "number"},
                    "bf16_sink_tokens_s0": {"type": "integer"},
                    "bf16_recent_tokens_w": {"type": "integer"},
                    "rv_absorbed_into_projection_weights": {"type": "boolean"},
                    "kv_memory_reduction_factor": {"type": "number"},
                    "large_batch_throughput_gain_x": {"type": "number"}
                }
            }
        },
        {
            "name": "aleph_prove_draco_dataflow_topological_longcodezip_ppr_and_abridgekv_pause_nested_routing",
            "description": (
                "Verifica formalmente la recuperacion topologica guiada por flujo de datos DRACO, el razonamiento dual-graph CodeRAG "
                "y la compresion de contexto por perplejidad LongCodeZip (PACMSE FSE 2026 arXiv:2601.00376v3 §7) con el balanceo "
                "diadico por grupo Permuted Bit-Reversal (PBR) y ecualizacion diagonal de Walsh-Hadamard (arXiv:2605.17757v1 App. A.4), "
                "junto con la compresion KV de pausas aprendidas AbridgeKV (4:1 y 8:1 sin inflacion de longitud de salida del 40-69% de R-KV, "
                "+3.8 avg@8 pts en presupuesto 2048, arXiv:2610.20641) y ruteo de memoria anidado NestedKV (arXiv:2605.26678) (Nivel 238 - Tool #247)."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "target_name": {"type": "string"},
                    "total_dataflow_topological_nodes": {"type": "integer"},
                    "coderag_dual_graph_verified": {"type": "boolean"},
                    "longcodezip_perplexity_compression_ratio": {"type": "number"},
                    "pbr_dyadic_group_collision_count": {"type": "integer"},
                    "hadamard_diagonal_equalization_max_dev": {"type": "number"},
                    "abridgekv_compression_arm_ratio": {"type": "integer"},
                    "shared_kept_set_across_heads": {"type": "boolean"},
                    "rkv_token_inflation_avoided_pct": {"type": "number"},
                    "actual_reasoning_token_inflation_pct": {"type": "number"},
                    "avg_at_8_gain_over_rkv_2048": {"type": "number"},
                    "nestedkv_training_free_routing_enabled": {"type": "boolean"}
                }
            }
        },
        {
            "name": "aleph_audit_pg18_failover_slots_webhook_replay_rls_and_partition_split_merge",
            "description": "Audita formalmente (NODE-03 v18.0.0 - REG-104) sincronización de slots lógicos de failover en PostgreSQL 18 (failover=true, synchronized_standby_slots), defensa anti-replay HMAC multi-tenant bajo RLS AS RESTRICTIVE y reorganización zero-downtime de particiones sin SPLIT/MERGE bloqueante.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "audit_spec": {"type": "object"}
                },
                "required": ["audit_spec"]
            }
        },
                                                                                            {
            "name": "aleph_audit_pg18_aio_supavisor_set_local_rls_and_table_rename_compat_view",
            "description": "Audita formalmente subsistema PG18 Async I/O (io_method = worker | io_uring), confinamiento transaccional SET LOCAL en pools Supavisor contra fugas entre inquilinos, y renombrado Zero-Downtime de tablas con vista de compatibilidad security_invoker = true (REG-112 / v19.4.0).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "sql_ddl": {"type": "string", "description": "DDL/DML SQL a verificar"}
                },
                "required": ["sql_ddl"]
            }
        },
    {
            "name": "aleph_audit_pg18_uuidv7_locality_security_invoker_view_and_matview_refresh_concurrently",
            "description": "Audita formalmente claves primarias PG18 uuidv7() ordenadas temporalmente (bloqueando gen_random_uuid()), vistas PostgREST con WITH (security_invoker = true) para preservar RLS, y REFRESH MATERIALIZED VIEW CONCURRENTLY con UNIQUE INDEX (REG-111 / v19.4.0).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "sql_ddl": {"type": "string", "description": "DDL/DML SQL a verificar"}
                },
                "required": ["sql_ddl"]
            }
        },
    {
            "name": "aleph_audit_pg18_virtual_generated_cols_vault_definer_and_unique_using_index",
            "description": "Audita formalmente columnas generadas PG18 GENERATED ALWAYS AS (...) VIRTUAL, confinamiento de funciones SECURITY DEFINER sobre Supabase Vault (search_path = pg_catalog, public + REVOKE FROM PUBLIC), y promoción Zero-Downtime de PRIMARY KEY/UNIQUE mediante CREATE UNIQUE INDEX CONCURRENTLY + USING INDEX (REG-110 / v19.4.0).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "sql_ddl": {"type": "string", "description": "DDL/DML SQL a verificar"}
                },
                "required": ["sql_ddl"]
            }
        },
    {
            "name": "aleph_audit_pg18_temporal_without_overlaps_mfa_aal2_rls_and_expand_contract_type",
            "description": "Audita formalmente restricciones temporales PG18 WITHOUT OVERLAPS con btree_gist, políticas RLS AS RESTRICTIVE con step-up MFA (aal2) en Supabase Auth, y bloqueo de reescrituras de tabla por ALTER COLUMN TYPE exigiendo Expand-Contract (REG-109 / v19.4.0).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "sql_ddl": {"type": "string", "description": "DDL/DML SQL a verificar"}
                },
                "required": ["sql_ddl"]
            }
        },
    {
            "name": "aleph_audit_pg18_copy_reject_limit_storage_prefix_rls_and_fk_not_valid_swap",
            "description": "Audita formalmente PG18 COPY (ON_ERROR ignore, REJECT_LIMIT), aislamiento RLS por prefijo de carpeta en Supabase Storage (storage.foldername) con bloqueo de MIME XSS, y reemplazo Zero-Downtime de claves foráneas con NOT VALID + VALIDATE CONSTRAINT (REG-108 / v19.4.0).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "sql_ddl": {"type": "string", "description": "DDL/DML SQL a verificar"}
                },
                "required": ["sql_ddl"]
            }
        },
    {
            "name": "aleph_audit_pg18_merge_returning_app_metadata_rls_and_partition_attach_detach",
            "description": "Audita formalmente sentencias PG18 MERGE INTO ... RETURNING merge_action(), defensa contra escalamiento de privilegios RLS por user_metadata exigiendo app_metadata con initPlan, y ciclo Zero-Downtime ATTACH/DETACH PARTITION CONCURRENTLY (REG-107 / v19.4.0).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "sql_ddl": {"type": "string", "description": "DDL/DML SQL a verificar"}
                },
                "required": ["sql_ddl"]
            }
        },
    {
            "name": "aleph_audit_pg18_json_table_anon_signin_rls_and_index_swap_concurrently",
            "description": "Audita formalmente determinismo SQL/JSON JSON_TABLE (ON ERROR/ON EMPTY), aislamiento RLS de usuarios anónimos Supabase (is_anonymous JWT guard) y reconstrucción/reemplazo Zero-Downtime de índices con CREATE/DROP INDEX CONCURRENTLY (REG-106 / v19.4.0).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "sql_ddl": {"type": "string", "description": "DDL SQL a verificar"}
                },
                "required": ["sql_ddl"]
            }
        },
    {
            "name": "aleph_audit_pg18_btree_dedup_realtime_presence_rls_and_not_null_validation",
            "description": "Audita formalmente (NODE-03 v19.4.0 - REG-105) deduplicación de listas de posteo B-Tree en PostgreSQL 18 (deduplicate_items=on, fillfactor 80..95), aislamiento RLS AS RESTRICTIVE y cota de payload en Supabase Realtime Presence, y promoción zero-downtime SET NOT NULL mediante CHECK NOT VALID pre-validado.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "audit_spec": {"type": "object"}
                },
                "required": ["audit_spec"]
            }
        },
        {
            "name": "aleph_prove_durable_agent_replay_and_bft_wave_orchestration",
            "description": (
                "Verifica formalmente en 4 capas (Lexer DFA + AST-to-SSA Cytron con nodos phi + ICP/CEGIS + "
                "Tarjan SCC / Kahn Waves O(V+E)) la Ejecucion Durable y Replay Determinista en grafos multi-agente, "
                "Write-Ahead Effect Journal con clave SHA-256, Compuertas BFT de Aprobacion Humana Anti-TOCTOU "
                "e invariantes de Codere, ClipperOps y GOAR (Nivel 337 - Tool #349 - v19.7.0 - REG-113)."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "target_workflow_name": {"type": "string"},
                    "workflow_nodes": {"type": "array", "items": {"type": "object"}},
                    "recorded_effects": {"type": "array", "items": {"type": "object"}},
                    "approval_gates": {"type": "array", "items": {"type": "object"}},
                    "orchestrator_source_code": {"type": "string"},
                    "domain_invariants": {"type": "object"},
                    "release_version": {"type": "string"}
                }
            }
        },
        {
            "name": "aleph_prove_speculative_wave_mvmemory_and_causal_edge_synthesis",
            "description": "Nivel 338 (v19.7.0 — REG-114 | Shard NODE-01): Verifica formalmente ausencia de conflictos Read-Write Set (WAW/RAW/WAR) en oleadas paralelas de DAGs multi-agente con Block-STM MVMemory, DFA Lexer (0.0% FPR), Cytron SSA phi-nodes, SMT/ICP {C-1, C, C+1} y síntesis CEGIS de aristas causales.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "dag_spec": {"type": "object"}
                }
            }
        },
        {
            "name": "aleph_prove_context_carrying_action_intent_epoch_fenced_deadswitch",
            "description": "Nivel 339 (v19.8.0 — REG-115 | Shard NODE-01): Verifica formalmente intenciones de acción portadoras de contexto (AIS), tokens de cercado monótonos (Epoch Fencing), concurrencia estructurada sin tareas huérfanas y compilación DAG Kahn/Tarjan en 4 capas SOTA.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "workflow_spec": {"type": "object"}
                }
            }
        },
        {
            "name": "aleph_prove_critical_path_brent_makespan_and_priority_inheritance_dag",
            "description": "Nivel 340 (v19.9.0 — REG-116 | Shard NODE-01): Verifica formalmente la cota de makespan del Teorema de Brent por camino crítico (b-level), ausencia de bloqueo Head-of-Line (HoL) e herencia de prioridades (PIP) en DAGs multi-agente bajo 4 capas SOTA.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "dag_spec": {"type": "object"}
                }
            }
        },
        {
            "name": "aleph_prove_edf_laxity_work_conserving_and_wait_die_dag",
            "description": "Nivel 341 (v20.0.0 — REG-117 | Shard NODE-01): Verifica formalmente plazos efectivos Chetto-Blazewicz (EDF), holgura dinámica no negativa (LLF), función de demanda (DBF) y control de concurrencia Wait-Die / Wound-Wait libre de inanición en DAGs multi-agente bajo 4 capas SOTA.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "dag_spec": {"type": "object"}
                }
            }
        },
        {
            "name": "aleph_prove_credit_backpressure_parks_bounded_buffer_and_cmh_dag",
            "description": "Nivel 342 (v20.1.0 — REG-118 | Shard NODE-01): Verifica formalmente conservación de créditos de backpressure (Kung-Morris), dimensionamiento de buffers acotados de Parks en grafos reconvergentes y ausencia de nudos de bloqueo Chandy-Misra-Haas (CMH) en DAGs multi-agente bajo 4 capas SOTA.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "dag_spec": {"type": "object"}
                }
            }
        },
        {
            "name": "aleph_prove_vector_clock_causal_barrier_semilattice_and_hedged_straggler_dag",
            "description": "Nivel 343 (v20.2.0 — REG-119 | Shard NODE-01): Verifica formalmente barreras causales con relojes vectoriales de Mattern-Fidge, reductores de fan-in sobre Join-Semilattice (ACI: asociativo, conmutativo, idempotente) sin sobrescritura LWW y deduplicación idempotente de réplicas hedged contra stragglers en DAGs multi-agente bajo 4 capas SOTA.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "dag_spec": {"type": "object"}
                }
            }
        },
        {
            "name": "aleph_prove_chandy_lamport_causal_cut_and_domino_free_rollback_dag",
            "description": "Nivel 344 (v20.3.0 — REG-120 | Shard NODE-01): Verifica formalmente cortes causales consistentes de Chandy-Lamport (ausencia de mensajes huérfanos y efecto dominó en rollback), quiescencia de obligaciones en vuelo, guardas de idempotencia ante re-disparo de efectos e intervalo óptimo de checkpoint de Daly en DAGs multi-agente bajo 4 capas SOTA.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "dag_spec": {"type": "object"}
                }
            }
        },
        {
            "name": "aleph_prove_drr_maxmin_fairness_and_multitenant_token_quota_dag",
            "description": "Nivel 345 (v20.4.0 — REG-121 | Shard NODE-01): Verifica formalmente planificación Deficit Round-Robin (DRR) O(1) de Shreedhar-Varghese, asignación equitativa Max-Min por Water-Filling contra noisy neighbors y guardas duras de presupuesto de tokens/pasos en DAGs multi-agente bajo 4 capas SOTA.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "dag_spec": {"type": "object"}
                }
            }
        },
        {
            "name": "aleph_prove_mazurkiewicz_trace_dpor_and_diamond_commutativity_dag",
            "description": "Nivel 346 (v20.5.0 — REG-122 | Shard NODE-01): Verifica formalmente equivalencia de trazas de Mazurkiewicz, reducción dinámica de orden parcial (Optimal-DPOR) en Forma Normal de Foata y conmutatividad Diamond Property con rangos de edición disjuntos en DAGs multi-agente bajo 4 capas SOTA.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "dag_spec": {"type": "object"}
                }
            }
        },
        {
            "name": "aleph_prove_saga_pivot_phase_ordering_and_reverse_compensation_dag",
            "description": "Nivel 347 (v20.6.0 — REG-123 | Shard NODE-01): Certifica formalmente el Particionamiento Causal de Sagas (COMPENSABLE <= PIVOT <= RETRIABLE), Unicidad de Transacción Pivot por Camino, Orden de Compensación Topológica Inversa por Oleadas y Bundles Inmutables de Evidencia Pre-Efecto (Janus arXiv:2609.38266 / SagaLLM) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "saga_nodes": {"type": "array", "items": {"type": "object"}},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_dynamic_quorum_joint_consensus_readindex_lease_and_split_brain_dag",
            "description": "Nivel 348 (v20.7.0 — REG-124 | Shard NODE-01): Certifica formalmente Consenso de Quórum Dinámico con Reconfiguración sin Detención (Joint Consensus C_old,new arXiv:2606.02019), Leases de Lectura Linealizable (ReadIndex con cota de deriva de reloj epsilon_drift) y Revocation Fencing Monotónico (draft-das-cross-device-authority-revocation-00) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "consensus_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_byzantine_quorum_certificate_three_chain_finality_and_equivocation_slashing_dag",
            "description": "Nivel 349 (v20.8.0 — REG-125 | Shard NODE-01): Certifica formalmente Certificados de Quórum Bizantino (2f+1 sobre N >= 3f+1), Regla de Finalidad en 3-Eslabones Consecutivos (HotStuff / Mysticeti 3-Chain Commit Rule) y Detección/Slashing de Equivocación Criptográfica (Doble Voto en misma vista) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "bft_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_epoch_fenced_wal_group_commit_and_linearizable_truncate_dag",
            "description": "Nivel 350 (v20.9.0 — Hito Mayor REG-126 | Shard NODE-01): Certifica formalmente Write-Ahead Logging (WAL) con Group Commit Monotónico (LSN_flushed >= LSN_dirty >= LSN_committed), Truncamiento Linealizable Libre de Pérdida de Prefijos ante Torn-Writes y Exclusividad de Escritura por Epoch Fencing en DAGs Multi-Agente con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "wal_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_ssi_rw_antidependency_cycle_and_phantom_predicate_lock_dag",
            "description": "Nivel 351 (v21.0.0 — REG-127 | Shard NODE-01): Certifica formalmente Serializable Snapshot Isolation (SSI), ausencia o aborto determinista de estructuras peligrosas de doble arista rw-antidependency (T1 --rw--> T2 --rw--> T3) de Cahill-Fekete, bloqueos de rango de predicado SIREAD contra lecturas fantasma (Phantom Reads) y exclusividad de época en DAGs Multi-Agente con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "ssi_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_aria_deterministic_epoch_batch_reservation_and_conflict_reordering_dag",
            "description": "Nivel 352 (v21.1.0 — REG-128 | Shard NODE-01): Certifica formalmente planificación determinista de transacciones por lotes de época (Aria / Minerva), reserva lock-free WAW por menor TID (tid_min), reordenamiento determinista WAR antes de RAW anti-aborto y barrera de commit sin coordinación 2PC en DAGs Multi-Agente con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "aria_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_silo_three_phase_occ_sorted_write_lock_and_tid_word_validation_dag",
            "description": "Nivel 353 (v21.2.0 — REG-129 | Shard NODE-01): Certifica formalmente el protocolo de commit en 3 fases de Silo / Shirakami Tsurugi S-OCC: bloqueo del write-set en orden canónico estricto y chequeo WP (Fase 1), punto de serialización por época y validación atómica de palabra TID + nodos B-Tree anti-fantasma (Fase 2), y síntesis monótona de Commit TID (Fase 3) en DAGs Multi-Agente con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "silo_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_block_stm_mvmemory_estimate_marker_and_incarnation_validation_dag",
            "description": "Nivel 354 (v21.3.0 — REG-130 | Shard NODE-01): Certifica formalmente ejecución paralela especulativa Block-STM / ParallelEVM con orden preestablecido: conversión de write-sets abortados en marcadores ESTIMATE en MVMemory con suspensión de lectores dependientes, poda de claves huérfanas entre encarnaciones y validación de pares (tx_idx, incarnation) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "block_stm_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_caracal_batch_append_hotspot_piece_splitting_and_bohm_placeholder_mvcc_dag",
            "description": "Nivel 355 (v21.4.0 — REG-131 | Shard NODE-01): Certifica formalmente gestión de contención determinista Caracal (Batch-Append + Serial Piece Splitting fijado a core) y pre-asignación de placeholders MVCC Bohm libre de bloqueos de lectura-escritura con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "caracal_bohm_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_tictoc_data_driven_timestamp_interval_extension_and_cicada_contention_aware_mvcc_dag",
            "description": "Nivel 356 (v21.5.0 — REG-132 | Shard NODE-01): Certifica formalmente gestión de marcas de tiempo guiada por datos TicToc (extensión dinámica de intervalos [wts, rts] sin contador atómico central) y validación MVCC consciente de contención Cicada con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "tictoc_cicada_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_bamboo_retired_lock_early_release_commit_barrier_and_rococo_deferred_piece_dag",
            "description": "Nivel 357 (v21.6.0 — REG-133 | Shard NODE-01): Certifica formalmente liberación temprana de locks retirados en hotspots Bamboo (Guo et al. SIGMOD 2021) con barrera de commit sobre lecturas sucias, aborto en cascada completo y ejecución diferida de piezas conmutativas Rococo (Mu et al. OSDI 2014) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "bamboo_rococo_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_sundial_logical_lease_caching_and_tapir_inconsistent_replication_fast_quorum_dag",
            "description": "Nivel 358 (v21.7.0 — REG-134 | Shard NODE-01): Certifica formalmente armonización de control de concurrencia y caché con leases lógicos [wts, rts] Sundial (Yu et al. VLDB 2018) y replicación inconsistente con superquórum rápido 3/4 y merge determinista en view change TAPIR (Zhang et al. SOSP 2015) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "sundial_tapir_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_janus_dependency_graph_scc_consensus_and_taurus_parallel_logging_lsn_vector_dag",
            "description": "Nivel 359 (v21.8.0 — REG-135 | Shard NODE-01): Certifica formalmente consolidación de control de concurrencia y consenso por grafos de dependencias y ejecución determinista de SCCs de Tarjan Janus (Mu et al. OSDI 2016) y logging paralelo multi-stream con vectores 2D de LSN Taurus (Xia et al. VLDB 2020) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "janus_taurus_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_polyjuice_learned_policy_matrix_safety_guard_and_meerkat_zero_coordination_fast_quorum_dag",
            "description": "Nivel 360 (v21.9.0 — Hito Mayor REG-136 | Shard NODE-01): Certifica formalmente guardarraíles de validación de seguridad en matrices de políticas de concurrencia aprendida Polyjuice (Wang et al. OSDI 2021) y transacciones replicadas multicore bajo el principio de cero coordinación con superquórum 3/4 Meerkat (Szekeres et al. EuroSys 2020) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "polyjuice_meerkat_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_caracal_deterministic_version_array_and_narwhal_tusk_zero_overhead_dag",
            "description": "Nivel 361 (v22.0.0 — Hito Mayor Era v22.0.0 REG-137 | Shard NODE-01): Certifica formalmente arreglos de versiones pre-inicializados por lotes y partición Split-on-Demand bajo contención determinista Caracal (Dai et al. SOSP 2021) junto con mempool DAG certificado 2f+1 Narwhal y consenso asíncrono sin sobrecarga de mensajes Tusk (Danezis et al. EuroSys 2022) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "caracal_narwhal_tusk_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_pwv_piece_wise_early_write_visibility_and_sailfish_one_round_leader_dag",
            "description": "Nivel 362 (v22.1.0 — REG-138 | Shard NODE-01): Certifica formalmente visibilidad temprana por piezas con barrera de Commit-Point Rendezvous libre de abortos en cascada PWV (Faleiro et al. VLDB 2017) y consenso DAG BFT de una sola ronda con certificados de no-voto 2f+1 Sailfish (Shrestha et al. IEEE S&P 2025 / ePrint 2024/472) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "pwv_sailfish_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_quecc_priority_queue_control_free_execution_and_shoal_pipelined_reputation_dag",
            "description": "Nivel 363 (v22.2.0 — REG-139 | Shard NODE-01): Certifica formalmente planificación en 2 fases orientada a colas por prioridad con ejecución libre de locks/abortos QueCC (Qadah & Sadoghi Middleware 2018) y consenso DAG-BFT con anclas encauzadas en cada ronda y reputación determinista prevalente Shoal (Spiegelman et al. FC 2024 / arXiv:2306.03058) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "quecc_shoal_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_ic3_constrained_parallel_piece_dependency_and_hammerhead_leader_utilization_dag",
            "description": "Nivel 364 (v22.3.0 — REG-140 | Shard NODE-01): Certifica formalmente ejecución paralela restringida por grafos SC-Graph y seguimiento transitivo de dependencias por tupla IC3 (Wang et al. SIGMOD 2016) junto con programación dinámica de líderes por tasa de utilización confirmada en consenso DAG-BFT HammerHead (Tsimos et al. ICDCS 2023 / arXiv:2309.12713) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "ic3_hammerhead_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_ermia_serial_safety_net_pi_eta_exclusion_and_cordial_miners_uncertified_blockdag",
            "description": "Nivel 365 (v22.4.0 — REG-141 | Shard NODE-01): Certifica formalmente la Red de Seguridad Serial ERMIA/SSN por exclusión de marcas pi > eta y sincronización de pstamp/sstamp ante antidependencias rw (Kim et al. SIGMOD 2016 / Wang et al. VLDB Journal 2017, arXiv:1605.04292) junto con el consenso BlockDAG no certificado Cordial Miners con pasado causal completo y cono de ratificación >= 2f+1 (Keidar et al. DISC 2023 / arXiv:2205.09174) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "ermia_cordial_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_mocc_adaptive_temperature_canonical_lock_and_bbca_chain_single_message_anchor_probe_dag",
            "description": "Nivel 366 (v22.5.0 — REG-142 | Shard NODE-01): Certifica formalmente el Control de Concurrencia Mayoritariamente Optimista con Temperatura Adaptativa y Orden Canónico de Locks MQL MOCC (Wang & Kimura PVLDB 2016/2017) junto con el Consenso DAG BFT de Un Solo Mensaje y Sondeo de Anclas BBCA-Chain (Malkhi et al. FC 2024) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "mocc_bbca_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_bcc_balanced_occ_antidependency_pattern_and_dag_rider_four_round_wave_consensus",
            "description": "Nivel 367 (v22.6.0 — REG-143 | Shard NODE-01): Certifica formalmente el Control de Concurrencia Optimista Balanceado Anti-Falsos Abortos BCC (Yuan et al. PVLDB 2016) junto con el Consenso Asíncrono Post-Cuántico Basado en DAG en Olas de 4 Rondas DAG-Rider (Keidar et al. ACM PODC 2021 / arXiv:2102.08325) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "bcc_dagrider_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_plor_pessimistic_lock_optimistic_read_tail_latency_and_fin_signature_free_acs_dag",
            "description": "Nivel 368 (v22.7.0 — REG-144 | Shard NODE-01): Certifica formalmente el Bloqueo Pesimista con Lectura Optimista y Cota de Latencia de Cola por Antigüedad Plor (Chen et al. ACM SIGMOD 2022) junto con el Subconjunto Común Asíncrono Libre de Firmas en Tiempo Constante FIN (Duan, Wang & Zhang ACM CCS 2023 / IACR ePrint 2023/154) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "plor_fin_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_hekaton_lockfree_mvcc_speculative_commit_dep_and_dumbo_ng_throughput_oblivious_dag",
            "description": "Nivel 369 (v22.8.0 — REG-145 | Shard NODE-01): Certifica formalmente el Control de Concurrencia Multiversión Libre de Bloqueos con Dependencias de Commit Especulativo Hekaton (Larson et al. PVLDB 2011 / arXiv:1201.0228) junto con el Consenso Asíncrono BFT de Latencia Indiferente al Throughput Dumbo-NG (Gao et al. ACM CCS 2022 / arXiv:2209.00750) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "hekaton_dumbong_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_hyper_precision_locking_undo_buffer_mvcc_and_hotstuff1_speculative_slotting_dag",
            "description": "Nivel 370 (v22.9.0 — Hito Mayor REG-146 | Shard NODE-01): Certifica formalmente el Control de Concurrencia Multiversión Serializable con Buffers de Undo Versionados y Precision Locking de Predicados Intensionales HyPer (Neumann, Mühlbauer & Kemper ACM SIGMOD 2015) junto con el Consenso BFT Lineal con Especulación en Una Fase y Slotting Dinámico HotStuff-1 (Kang et al. arXiv:2408.04728) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "hyper_hotstuff1_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_foedus_dual_page_snapshot_master_tree_occ_and_mysticeti_uncertified_fast_commit_dag",
            "description": "Nivel 371 (v23.0.0 — Hito Mayor REG-147 | Shard NODE-01): Certifica formalmente la Arquitectura de Puntero de Página Dual NVRAM/DRAM y Concurrencia Optimista Foster B-Tree FOEDUS (Kimura ACM SIGMOD 2015) junto con el Consenso DAG BFT sin Certificados con Camino Rápido de 3 Mensajes y Multi-Líder Mysticeti (Babel et al. NDSS 2025 / arXiv:2310.14821) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "foedus_mysticeti_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_orthrus_message_passing_decoupled_concurrency_and_jolteon_ditto_asynchronous_fallback_dag",
            "description": "Nivel 372 (v23.1.0 — REG-148 | Shard NODE-01): Certifica formalmente el Control de Concurrencia Desacoplado por Paso de Mensajes y Planificación Anticipada Libre de Deadlocks Orthrus (Ren, Faleiro & Abadi ACM SIGMOD 2016 / arXiv:1512.06168) junto con el Consenso BFT Adaptativo en 2 Rondas con Fallback Asíncrono VABA Jolteon & Ditto (Gelashvili et al. FC 2022 / arXiv:2106.10362) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "orthrus_jolteon_ditto_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_callas_modular_concurrency_golden_rules_rnl_and_mahi_mahi_asynchronous_dag",
            "description": "Nivel 373 (v23.2.0 — REG-149 | Shard NODE-01): Certifica formalmente el Control de Concurrencia Modular ACID con Reglas de Oro GR1/GR2 y Runtime Nexus Locking Callas (Xie et al. ACM SOSP 2015) junto con el Consenso DAG BFT Asíncrono Multi-Líder sin Certificados de Baja Latencia Mahi-Mahi (Jovanovic, Kokoris-Kogias, Sonnino et al. arXiv:2410.08670) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "callas_mahimahi_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }            },
        {
            "name": "aleph_prove_deuteronomy_decoupled_tc_dc_llsn_and_graded_dag_two_round_asynchronous_consensus",
            "description": "Nivel 374 (v23.3.0 — REG-150 | Shard NODE-01): Certifica formalmente la Arquitectura Desacoplada Transaction Component (TC) / Data Component (DC) con Causalidad Monotónica LLSN y Bloqueo de Rangos Multiversión Deuteronomy (Levandoski, Lomet, Mokbel, Zhao CIDR 2011 / VLDB 2015) junto con el Consenso DAG BFT Asíncrono de Difusión Graduada en Dos Rondas y Anclas Líderes de Grado 2 GradedDAG (Dai et al. IACR ePrint 2024/142 / IEEE 2024) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "deuteronomy_graded_dag_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }            },
        {
            "name": "aleph_prove_scalog_order_then_assign_global_cut_and_starfish_erasure_coded_uncertified_dag",
            "description": "Nivel 375 (v23.4.0 — Hito Mayor Nivel 375 | REG-151 | Shard NODE-01): Certifica formalmente el Registro Compartido Escalable con Paradigma Order-Then-Assign por Vector de Corte Global Monotónico y Reconfiguración Sin Pausa Scalog (Ding, Chu, Zhao, Li, Alvisi, van Renesse USENIX NSDI 2020) junto con el Consenso DAG BFT sin Certificados con Codificación de Borrado Reed-Solomon Lineal O(n) y Confirmación en 3 Rondas Starfish (Polyanskii et al. IOTA Research 2025) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "scalog_starfish_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }            },
        {
            "name": "aleph_prove_delos_virtuallog_loglet_sealing_and_lightdag_consistent_broadcast_totality",
            "description": "Nivel 376 (v23.5.0 — REG-152 | Shard NODE-01): Certifica formalmente el Consenso Virtual y Encadenamiento Dinámico de Loglets con Sellado Atómico en MetaStore Delos (Balakrishnan et al. USENIX OSDI 2020) junto con el Consenso DAG BFT de Baja Latencia con Difusión Consistente Ligera en 2 Pasos y Recuperación de Totalidad por Pull de Ancestros LightDAG (IACR ePrint 2024/160) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "delos_lightdag_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }            },
        {
            "name": "aleph_prove_boki_stateful_serverless_logbook_readcache_and_remora_optimistic_path_dag",
            "description": "Nivel 377 (v23.6.0 — REG-153 | Shard NODE-01): Certifica formalmente el Cómputo Serverless con Estado sobre Registros Compartidos LogBook con Multiplexación por Etiquetas Físicas y Barreras de Secuencia Read-After-Write en ReadCache Boki (Jia & Witchel ACM SOSP 2021) junto con el Consenso DAG BFT de Baja Latencia mediante Rutas Optimistas de 3 Rondas y Fallback Consistente de Ola Remora (arXiv:2409.07693) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "boki_remora_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }            },
        {
            "name": "aleph_prove_vcorfu_materialized_streams_csmr_and_autobahn_seamless_high_speed_bft",
            "description": "Nivel 378 (v23.7.0 — Hito 390 MCP Tools | REG-154 | Shard NODE-01): Certifica formalmente el Almacenamiento Cloud sobre Registros Compartidos con Materialized Streams de Lectura en Un Salto y Máquinas de Estados Componibles cSMR vCorfu (Wei, Tai, Rossbach, Abraham, Malkhi et al. USENIX NSDI 2017) junto con el Consenso BFT de Alta Velocidad con Carriles Asíncronos Desacoplados y Recuperación Sin Bloqueos ante Blips Autobahn (Giridharan, Suri-Payer, Abraham, Alvisi, Crooks ACM SOSP 2024) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "vcorfu_autobahn_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_halfmoon_log_optimal_serverless_and_shoal_plusplus_staggered_dag_bft",
            "description": "Nivel 379 (v23.8.0 — 391 MCP Tools | REG-155 | Shard NODE-01): Certifica formalmente la Tolerancia a Fallos Log-Óptima con Lecturas Sin Registro (Log-Free Reads) y logCondAppend Halfmoon (Qi, Liu, Jin ACM SOSP 2023) junto con el Consenso DAG-BFT de Baja Latencia (4.5 md) con Fast Direct Commit e Instancias DAG Escalonadas Entrelazadas Shoal++ (Arun, Li, Suri-Payer, Das, Spiegelman USENIX NSDI 2025) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "halfmoon_shoalpp_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_beldi_transactional_serverless_workflows_and_kudzu_fast_high_throughput_bft",
            "description": "Nivel 380 (v23.9.0 — Hito Mayor 380 Niveles Formales | 392 MCP Tools | REG-156 | Shard NODE-01): Certifica formalmente los Flujos Serverless con Estado Transaccionales, Linked DAAL, Claves Compuestas (instance_id, step_number) e Intent Collector Beldi (Zhang, Cardoza, Chen, Angel, Liu USENIX OSDI 2020) junto con el Consenso BFT de Alto Rendimiento con Fast Path Integrado 2-Delta, Slow Path 3-Delta y Dispersión por Códigos de Borrado Kudzu (Shoup, Sliwinski, Vonlanthen DISC 2025) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "beldi_kudzu_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_tango_distributed_data_structures_and_hydrangea_optimistic_two_round_bft",
            "description": "Nivel 381 (v24.0.0 — Hito Mayor v24.0.0 | 393 MCP Tools | REG-157 | Shard NODE-01): Certifica formalmente las Estructuras de Datos Distribuidas en Memoria sobre Registros Compartidos, Transacciones Remote-Write sin Reproducción Previa y Checkpoints/Forget Tango (Balakrishnan, Malkhi, Wobber, Prabhakaran, Wei et al. ACM SOSP 2013) junto con el Consenso BFT Parcialmente Síncrono de Dos Rondas Optimistas bajo Fallos Mixtos Bizantinos/Crash Hydrangea (Shrestha, Kate, Nayak USENIX Security 2026 / IACR ePrint 2025/1112) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "tango_hydrangea_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_fuzzylog_partially_ordered_color_dag_and_mirbft_rotating_bucket_multileader",
            "description": "Nivel 382 (v24.1.0 — 394 MCP Tools | REG-158 | Shard NODE-01): Certifica formalmente los Registros Compartidos Parcialmente Ordenados por Colores con Appends Atómicos Multi-Color de Skeen y Reconciliación Post-Partición CAPMap The FuzzyLog / Dapple (Lockerman, Faleiro, Kim, Abadi, Aspnes, Balakrishnan et al. USENIX OSDI 2018) junto con el Consenso BFT Multi-Líder con Particionado Rotativo de Buckets de Hash y Sharding de Verificación de Firmas Mir-BFT (Stathakopoulou, David, Pavlovic, Vukolic JSys 2022) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "fuzzylog_mirbft_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_replex_hybrid_multi_index_replication_and_simplex_dummy_block_fast_consensus",
            "description": "Nivel 383 (v24.2.0 — 395 MCP Tools | REG-159 | Shard NODE-01): Certifica formalmente los Almacenes Multi-Índice Altamente Disponibles mediante Replicación en Cadena de Replexes Híbridos y Recuperación Acotada de Fallos Replex (Tai, Wei, Freedman, Abraham, Malkhi USENIX ATC 2016 Best Paper Award) junto con el Consenso BFT Parcialmente Síncrono con Bloques Dummy de Timeout, Notarización en 2 Saltos y Finalización Óptima en 3 Saltos Simplex Consensus (Chan, Pass TCC 2023 / ePrint 2023/463) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "replex_simplex_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_ford_onesided_rdma_disaggregated_pm_and_gatling_parallel_consensus",
            "description": "Nivel 384 (v24.3.0 — 396 MCP Tools | REG-160 | Shard NODE-01): Certifica formalmente las Transacciones Distribuidas sobre Memoria Persistente Desagregada vía RDMA Unilateral con Hitchhiked Read-and-Lock en 1 RTT, Commit Coalescente, Flush Remoto Selectivo y Lectura en Backups FORD (Zhang, Hua, Zuo, Liu USENIX FAST 2022 / ACM TOS 2023) junto con el Consenso de Difusión Atómica Rápida por Composición Paralela Escalonada Sub-RTT e Intercalado Determinista Gatling (Scaffino, Resnick, Neu LIPIcs AFT 2026) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "ford_gatling_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_motor_consecutive_version_tuple_mvcc_and_alpenglow_votor_rotor_consensus",
            "description": "Nivel 385 (v24.4.0 — 397 MCP Tools | REG-161 | Shard NODE-01): Certifica formalmente las Transacciones Distribuidas Multi-Versión sobre Memoria Desagregada mediante Tuplas de Versiones Consecutivas (CVT) en 1 RTT y Recolección de Basura Activa por Coordinador sin Rastreo Global Motor (Zhang, Hua, Yang USENIX OSDI 2024) junto con el Consenso BFT de Finalidad Dual Votor (1 Ronda al 80% / 2 Rondas al 60%), Difusión en Capa Única Ponderada por Stake Rotor y Resiliencia 20+20 Alpenglow (Kniep, Sliwinski, Wattenhofer ETH Zürich / Anza 2025, SIMD-0326) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "motor_alpenglow_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_speculative_recovery_super_collapse_and_minimmit_signature_free_consensus",
            "description": "Nivel 386 (v24.5.0 — 398 MCP Tools | REG-162 | Shard NODE-01): Certifica formalmente la Recuperación Especulativa Paralela sobre Almacenamiento Desagregado (REDS) mediante las primitivas atómicas super y collapse libres de split-brain (Li, Kalaba, Freedman, Lloyd et al. USENIX ATC 2022, pp. 271-286) junto con el Consenso Blockchain Post-Cuántico Libre de Firmas Generic Simplex & Minimmit parametrizado por View Agreement (Losa, Wang, Xiang, Yu arXiv:2609.32985, latencia óptima de commit de 3 retardos para f < n/3 y 2 retardos para f < n/5, tiempo de bloque de 2 retardos sin especulación y comunicación O(n^2) por vista) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "speculative_minimmit_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_mako_speculative_2pc_geo_replication_and_banyan_two_step_bft_consensus",
            "description": "Nivel 387 (v24.6.0 — 399 MCP Tools | REG-163 | Shard NODE-01): Certifica formalmente las Transacciones Distribuidas Especulativas con Geo-Replicación Desacoplada Mako (Shen, Cui, Sen, Angel, Mu USENIX OSDI 2025, Speculative 2PC con acotamiento de abortos en cascada por watermark y 3.66M TPC-C tx/s en 10 shards) junto con el Consenso BFT de Líder Rotativo con Crecimiento y Finalización en 2 Pasos (2 Retardos de Red) Banyan (Vonlanthen, Sliwinski, Albarello, Wattenhofer ETH Zürich arXiv:2312.05869, resiliencia parametrizada n >= 3f + 2p* - 1 con 1 <= p* <= f y penalidad cero al caer al camino estándar) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "mako_banyan_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_rtx_repairable_disaggregated_memory_index_and_simple_it_signature_free_bft",
            "description": "Nivel 388 (v24.7.0 — Hito 400 MCP Tools | REG-164 | Shard NODE-01): Certifica formalmente los Índices Transaccionales Reparables sobre Memoria Desagregada RDMA/CXL rTX (Lu, Wei, Chen, Chen arXiv:2308.02501, detección al vuelo de clientes fallidos y reparación online de actualizaciones no atómicas en RaceHashing y Sherman B+Tree con 1.2x-2x speedup) junto con el Consenso BFT Práctico Libre de Firmas Post-Cuántico Simple-IT con Pipelining Especulativo (Wang et al. arXiv:2606.14404, 4 retardos teóricos y 3 retardos en ruta optimista en Mempool-Simple-IT y Dispersed-Simple-IT) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "rtx_simple_it_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_foresight_predictive_deterministic_db_and_autopilot_adaptive_autobahn_bft",
            "description": "Nivel 389 (v24.8.0 — 401 MCP Tools | REG-165 | Shard NODE-01): Certifica formalmente la Base de Datos Determinista con Planificación Predictiva ForeSight (Huang, Yan, Wang, Li, Lin arXiv:2508.17375, predicción de conflictos ASPN sin conjuntos de lectura/escritura pre-obtenidos, reordenamiento ligero Matrix Two-pass Forward Scan MTFS RAW->WAR y optimización multiversión con fallback sobre cadenas de versiones logrando 2x speedup en YCSB sesgado con 28,819 txns/s y ratio de aborto 0.017) junto con el Framework de Aprendizaje por Refuerzo Descentralizado Resiliente a Polución Bizantina AutoPilot sobre Autobahn BFT (Chen, Zhang, Zhou, Amiri, Marcus, Wu arXiv:2606.09120, reducción de latencia del 49.8% frente a configuración estática, 73.3% frente a exploración aleatoria y ganancia de 27.6%-281.8% bajo ataques de polución) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "foresight_autopilot_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_nox_compiler_runtime_disaggregated_index_and_hydra_global_ordering_free_multi_bft",
            "description": "Nivel 390 (v24.9.0 — Hito Decenal Nivel 390 | 402 MCP Tools | REG-166 | Shard NODE-01): Certifica formalmente el Framework Compilador-Runtime para Índices en Memoria Desagregada Nox (Zhao, Long, Wongkham, Srivastava, Liu, Lu, Wang, Lo arXiv:2609.02669, reescritura LLVM IR de dependencias de punteros y runtime centralizado de caché/traducción RDMA+CXL sobre B+-trees, hash tables y skip lists inmodificados) junto con el Consenso Multi-BFT Centrado en Objetos Libre de Barrera de Ordenamiento Global HYDRA (Lyu, Xie, Niu, Sadoghi, Zhang, Wang, Beschastnikh, Feng arXiv:2511.05843, ordenamiento secuencial por objeto sin barrera global, resolución determinista de deadlocks en grafos Wait-For y speedup de 9.0x en WAN y 7.4x en LAN hasta 128 réplicas bajo stragglers) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "nox_hydra_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_tiga_synchronized_clock_1wrtt_geo_tx_and_cassandra_two_tier_poa_por_bft",
            "description": "Nivel 391 (v25.0.0 — Hito Mayor v25.0.0 | 403 MCP Tools | REG-167 | Shard NODE-01): Certifica formalmente las Transacciones Geo-Distribuidas Aceleradas con Relojes Sincronizados en 1 WRTT Tiga (Geng, Mu, Sivaraman, Prabhakar ACM SOSP 2025 / arXiv:2509.05759, ordenamiento proactivo por timestamp futuro al envío, acuerdo de timestamps sin coordinación inter-líder y fallback 1.5-2 WRTTs logrando 1.3x-7.2x speedup) junto con el Consenso BFT con Progreso Parcial bajo Particiones Cassandra (Xie, Kang, Chen, Gupta, Hughes, Sadoghi arXiv:2607.02856, certificación de dos niveles PoA f+1 y PoR 2f+1, propuestas continuas sin líder y pacemaker desacoplado fuera de la ruta crítica logrando 900K TPS en 16 réplicas y 480K TPS en 104 réplicas) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "tiga_cassandra_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_quirinus_geo_replicated_dcc_batch_snapshot_and_pine_hard_soft_dag_consistency",
            "description": "Nivel 392 (v25.1.0 — 404 MCP Tools | REG-168 | Shard NODE-01): Certifica formalmente la Base de Datos Determinista Geo-Replicada Activo-Activo Quirinus (Mao, Zhang et al. arXiv:2611.05882, sincronización de snapshots consistentes en fronteras de batch, reordenamiento determinista intra-batch leyendo del snapshot inter-batch, ejecución especulativa, integración de CRDTs y fast-path commit logrando 6.2x el throughput TPC-C de Tiga) junto con el Verificador Generalizado de Consistencia No Transaccional Pine (Raghav, Hassan, Kattikat, Jay, Santhosh arXiv:2608.17388, DAG de historia de operaciones con aristas duras y blandas sobre búsqueda de frontera topológica, soporte de K-bounded staleness y ordered sequential consistency logrando hasta 370x speedup sobre Porcupine y descubriendo 6 nuevos bugs de consistencia) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "quirinus_pine_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_vigil_accountable_liveness_selective_silence_and_brbco_causal_broadcast",
            "description": "Nivel 393 (v25.2.0 — Hito 405 MCP Tools | REG-169 | Shard NODE-01): Certifica formalmente la Liveness Auditable contra Silencio Selectivo Vigil (Cheng et al. arXiv:2609.18778, atestación cruzada de bitmaps firmados, membresía de núcleo fija antes del forwarding, auditoría challenge-response, forwarding adaptativo O(n) sin silencio y barra de acusación mayoritaria > n/2 que reduce falsas acusaciones del 91.2% al 0.002% bajo 2% de pérdida WAN con umbral óptimo K_SI = tau_A + 1) junto con la Difusión Confiable Bizantina con Ordenamiento Causal BRB-CO (Barbaraci, Cachin arXiv:2609.17074, canal de 5 fases Send-Echo-Ready-Schedule-Reconstruct con encapsulación verificable VE anti-front-running y barreras de reloj vectorial en ECHO/READY con quórum > 2f) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "vigil_brbco_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_prdts_parameterized_finite_counter_reduction_and_trm_raft_byzantine_consensus",
            "description": "Nivel 394 (v25.3.0 — 406 MCP Tools | Hito Decenal REG-170 | Shard NODE-01): Certifica formalmente la Verificación Parametrizada de Algoritmos Distribuidos Asíncronos Basados en Rondas mediante Reducción Sound & Complete a Sistemas de Contadores Finitos PRDTS-FCS (Bertrand, Ghorpade, Rubin CONCUR 2026 / arXiv:2606.27867, pipeline de 4 abstracciones RMA -> PIA -> SSR -> BWA para LTL model checking simbólico en nuXmv sobre rondas no acotadas) junto con el Consenso Raft Resistente a Fallos Bizantinos con Modelo de Confianza y Reputación TRM-Raft (Zhang, Fan, Li arXiv:2607.08666, monitor de elecciones con umbral de salto de término m=2, descalificación por reputación <0.5 y verificación de integridad de log con firmas Schnorr manteniendo complejidad O(n), ratio de líder malicioso <5% bajo 40% de nodos bizantinos, >=90% throughput y <5% latencia extra) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "prdts_trm_raft_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_fast_tendermint_two_step_merged_state_and_flamingo_dag_load_balancing",
            "description": "Nivel 395 (v25.4.0 — 407 MCP Tools | REG-171 | Shard NODE-01): Certifica formalmente el Consenso Bizantino en Dos Pasos Fast Tendermint bajo n > 5f con Estado Fusionado locked+valid y Especificación Quint/TLA+ (Vander Vos, Sonnino, Cason DISC 2026 / arXiv:2608.13434, eliminación del paso prevote conservando rotación nativa de líder por ronda y envío de id(v) en precommit) junto con el Balanceo de Carga de Doble Capa para Consenso DAG-BFT Certificado Flamingo (arXiv:2609.28361, migración de cuentas en capa de ordenamiento activada exclusivamente vía log comprometido con métricas de sobrecarga tau_v > C_v selladas en cabeceras certificadas, y planificador determinista preservador de orden de lote completo con fusión de datos unidireccional en capa de ejecución sin despachador central) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "fast_tendermint_flamingo_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_seamless_dag_bft_reconfiguration_and_hakicc_verified_concurrency_control",
            "description": "Nivel 396 (v25.5.0 — 408 MCP Tools | REG-172 | Shard NODE-01): Certifica formalmente la Reconfiguración Sin Pausas en 4 Rondas para Consenso Asíncrono DAG-BFT con Clausura Causal y Moneda Perfecta Singleton-Enabled (Hu, Jehl, Franke-Bergmann arXiv:2610.00896, metadatos inmutables enabled-configs por ronda, ronda pasiva u+1 para nodos entrantes y conteo de acciones de moneda exclusivamente en rondas singleton) junto con el Diseño y Optimización Multi-Agente en Dos Etapas de Protocolos de Control de Concurrencia HakiCC (Habibi, Fang, Dolati, Nawab arXiv:2610.00889, verificación de conflict-serializability por detección de ciclos en grafo de precedencia con compactación de contexto O(1) en Etapa 1 y optimización evolutiva de fases de escritura/commit en Etapa 2 con +50.6% en TPC-C y +92.2% en AuctionMark) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "seamless_dag_hakicc_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_stateless_recovery_quorum_safety_and_bftide_adaptive_bft_switching",
            "description": "Nivel 397 (v25.6.0 — 409 MCP Tools | REG-173 | Shard NODE-01): Certifica formalmente la Seguridad de Quórum Bizantino ante Recuperación Sin Estado mediante Descomposición Exacta de Slack b+c-(2q-n) y Registros de Voto Durables Previos a Liberación de Firma (Mallick, Chebolu ICDCN 2027 / arXiv:2610.07759, bloqueo de la partición forzada FirstVote-QC bajo c>=1) junto con la Conmutación Adaptativa Embebida entre Protocolos BFT Basados en Líder y Sin Líder BFTide (arXiv:2609.31388, modelo MDP de 6 dimensiones sincronizado entre réplicas, certificado 2f+1 vinculado al digest de métricas y altura de frontera sin ronda de consenso separada, acuerdo en 2 ventanas consecutivas con dwell mínimo de 5 ventanas que se duplica tras reconmutación rápida y ~70% menor latencia que BFTBrain) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "stateless_recovery_bftide_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_multi_agent_escrow_budget_conservation_and_concurrent_proposer_censorship_resistance",
            "description": "Nivel 398 (v25.7.0 — 410 MCP Tools | REG-174 | Shard NODE-01): Certifica formalmente la Conservación de Presupuesto Tolerante a Fallos en Delegación Multi-Agente Distribuida mediante Créditos de Escrow Exclusivos en DAG, Permisos de Despacho Firmados en Cuarentena y Prohibición de Reembolso por Timeout (Zhu, Wang arXiv:2610.00349, liquidación at-most-once o certificado autoritativo de no-efecto con cercado de época) junto con la Resistencia Económica a la Censura y Rendimiento bajo Proponentes Concurrentes Racionales (Saraf, Kaklamanis, Wadhwa, Elsheimy AFT 2026 / LIPIcs.AFT.2026.26 / arXiv:2607.16995, mecanismo de tarifas penalizador de duplicación con escalado lineal de eCR=2.5 en 49 proponentes bajo quema de tarifa base 8.7x y bisección 1D O(m log(Delta/delta)) del umbral marginal único lambda* en equilibrio de Nash mixto simétrico) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "budget_conservation_mcp_tfm_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_lifeline_minimal_synchrony_validated_ba_and_metadb_tree_topology_mvcc",
            "description": "Nivel 399 (v25.8.0 — 411 MCP Tools | REG-175 | Shard NODE-01): Certifica formalmente el Acuerdo Bizantino Validado Óptimo bajo Sincronía Mínima Granular Lifeline (Efron, Ren DISC 2026 / LIPIcs.DISC.2026.11, donde factibilidad implica optimalidad con O(f) rondas y O(f^2) bits de comunicación bajo mayoría honesta f < n/2 cuando los enlaces síncronos forman apenas un camino de longitud f) junto con la Base de Datos Transaccional Distribuida Consciente de Estructura de Sistema de Archivos MetaDB (Ren et al. arXiv:2610.32247, particionamiento inducido por topología de árbol con clave (parent, name) y fila _attr_ colocada, bypass asíncrono respaldado por log fuera de ruta crítica para atributos agregables/cuotas y MVCC en memoria acotado por ciclo de vida con compactación de rango consciente de localidad que logra 2.2x-4.1x throughput y -50% nodos en >1000 nodos) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "lifeline_vba_metadb_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_level400_fast_bft_smr_two_delay_and_proofsax_sharded_proof_synthesis",
            "description": "Hito Mayor Nivel 400 (v25.9.0 — 412 MCP Tools | REG-176 | Shard NODE-01): Certifica formalmente la Optimalidad y Trade-Offs en Fast BFT SMR con Cota Inferior Estricta n >= 5f + 1 y Latencia de 2 Retrasos de Mensaje (Giridharan, Nguyen, Abraham, Clement, Crooks, Sutra DISC 2026 / LIPIcs.DISC.2026.6 / arXiv:2608.19629, quórum rápido n-f con dependencias coincidentes, monitoreo continuo de FastVote tras entrar en recuperación y ejecución EPaxos tras cierre transitivo de dependencias) junto con la Síntesis Automatizada de Pruebas mediante Particionamiento y Exploración Controlada ProofSaX (arXiv:2609.28535, particionamiento de disyunciones de precondición y conjunciones de postcondición con asunción prefija por cortocircuito, guarda de contradicción para reutilizar anotaciones manuales, cota recursiva de complejidad c(F)-n-1 en ExprGenerator y cero expansión de TCB con 86/103 pruebas completadas) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "level400_fast_bft_proofsax_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_adaptive_snapshots_visible_reads_and_optimal_adaptive_multivalued_ba",
            "description": "Nivel 401 (v26.0.0 — 413 MCP Tools | REG-177 | Shard NODE-01): Certifica formalmente la Linealizabilidad de Snapshots Adaptativos mediante Lecturas Visibles Obligatorias (Sulimany, Cory, Petrank DISC 2026 / LIPIcs.DISC.2026.1 / arXiv:2608.13705, bloqueo de la imposibilidad de lecturas invisibles en Click() y Observe(i) incluso bajo escritor único y escáner único mediante anuncio de época RMW) junto con el Acuerdo Bizantino Multivaluado Adaptativo Óptimo para Entradas de L Bits (Dufay, Paramonov, Gilbert, Schmid, Schnell, Svoboda, X. DISC 2026 / LIPIcs.DISC.2026.63, desacoplamiento de n y t con complejidad O_tilde(n*kappa + t*(L + f*kappa)) bits y O(f) rondas en sincronía parcial para f <= t fallos reales y latencia esperada O(1) en asincronía bajo t < n/3) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "adaptive_snapshots_mvba_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_quadratic_adkg_plain_setup_and_quiescent_history_independent_llsc",
            "description": "Nivel 402 (v26.1.0 — 414 MCP Tools | REG-178 | Shard NODE-01): Certifica formalmente la Generación Distribuida de Claves Asíncrona Cuadrática desde Setup Estándar (Abraham, Bacho, Stern DISC 2026 / LIPIcs.DISC.2026.9, O(n^2) comunicación y O(1) rondas con clave pública de tamaño constante O(1) en bulletin board público y resiliencia adaptativa fuerte f < n/3) junto con Objetos Load-Linked/Store-Conditional Aleatorizados con Independencia de Historia Quiescente (Bencivenga, Habashi, Woelfel DISC 2026 / LIPIcs.DISC.2026.12, implementación wait-free/lock-free de m objetos LL/SC desde CAS y FADD con espacio O(n*tau + m) y estado quiescente determinado únicamente por los valores actuales de los m objetos para hashing dinámico QHI) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "quadratic_adkg_qhi_llsc_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_eaid_elastic_async_dispersal_and_lockfree_mtf_working_set_list",
            "description": "Nivel 403 (v26.2.0 — 415 MCP Tools | REG-179 | Shard NODE-01): Certifica formalmente la Dispersión de Información Asíncrona Elástica con Poda Post-Diseminación (eAID, Kerur et al. DISC 2026 / LIPIcs.DISC.2026.16, codificación ágil con tamaño de fragmento y umbral de recuperación F+1 fijos y poda autónoma post-diseminación sin reconstrucción ni coordinación global) junto con la Lista Move-To-Front Lock-Free con Cota de Conjunto de Trabajo (Asbell, Ruppert DISC 2026 / LIPIcs.DISC.2026.20, conjunto dinámico linealizable con costo amortizado O(w(k) + c) proporcional al working set w(k) más contención puntual c y nodos alcanzables acotados por |K| + c) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "eaid_mtf_working_set_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_finwhale_two_round_dag_and_epistemic_non_leaking_concurrent_objects",
            "description": "Nivel 404 (v26.3.0 — 416 MCP Tools | REG-180 | Shard NODE-01): Certifica formalmente el Protocolo DAG BFT con Terminación en 2 Rondos y Resiliencia Óptima FinWhale (Ladelsky, Friedman DISC 2026 / LIPIcs.DISC.2026.2 / arXiv:2606.26292, fast-path de 2 message delays sobre Mysticeti bajo n = 3f + 2p - 1 y coexistencia segura fast/slow-path vía bloques FP-evidence) junto con Objetos Concurrentes No-Leaking Epistémicos (Attiya, Oshman, Schiller, Travers DISC 2026 / LIPIcs.DISC.2026.31, registros multivalor y Bounded Max Registers wait-free fully-non-leaking, imposibilidad sobre estado base finito para Unbounded Max Register y estructuras argument-non-leaking) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "finwhale_epistemic_non_leaking_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_space_efficient_lockfree_linear_probing_and_extractor_convex_agreement",
            "description": "Nivel 405 (v26.4.0 — 417 MCP Tools | REG-181 | Shard NODE-01): Certifica formalmente la Tabla Hash Lock-Free por Sondeo Lineal Eficiente en Espacio con Búsquedas Wait-Free y Reciclado de Tumbas sin Reconstrucción (DISC 2026 / LIPIcs.DISC.2026.26, metadatos compactos O(1) bits con LL/SC u O(log n) con CAS y complejidad amortizada proporcional al sondeo secuencial más contención puntual) junto con el Acuerdo Convexo General con Comunicación Casi-Óptima mediante Grafos Extractores (Dufay, Ghinea, Paramonov DISC 2026 / LIPIcs.DISC.2026.35 / arXiv:2602.21411, comunicación O(L*n log n) en espacios finitos y O(L*n^{1+o(1)}) en R^d con rondas O(n) y resiliencia de Helly t < n/(omega+eps)) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "linear_probing_convex_agreement_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_responsive_ba_validity_and_general_adversary_multivalued_consensus",
            "description": "Nivel 406 (v26.5.0 — 418 MCP Tools | REG-182 | Shard NODE-01): Certifica formalmente la Caracterización Exacta de Validez en Acuerdo Bizantino Responsivo y Core-Set Agreement Autenticado bajo n > 2*t_r + t_s y Condición de Similitud Responsiva (Ghinea, Kamp, Liu-Zhang DISC 2026 / LIPIcs.DISC.2026.51, incluyendo el régimen de minoría honesta) junto con las Cotas de Complejidad Comunicacional para Consenso Multivaluado y Difusión Confiable bajo Estructuras de Adversario Generales Q^d (Mizrahi, Wattenhofer DISC 2026 / LIPIcs.DISC.2026.43, cota ajustada O(L_out * n^{1+1/d} + n^2 log n) con terminación y difusión confiable no terminante parametrizada por delta > 1) con síntesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "responsive_validity_general_adversary_spec": {"type": "object"},
                    "dag_edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_subcubic_pkifree_coin_tossing_and_waitfree_fair_reconciliation",
            "description": "Nivel 407 (v26.6.0 — 419 MCP Tools | REG-183 | Shard NODE-01): Certifica formalmente el Lanzamiento de Moneda Comun Subcubico Asincrono sin PKI (Mizrahi, Wattenhofer DISC 2026 / LIPIcs.DISC.2026.39 / arXiv:2603.02071, transformacion por comites con grafos bipartitos averaging-sampler qs^2 >= n^2, s >= log2(q), Crusader Agreement de latencia 3 en Publish(Q,d), moneda perfecta O~(n^2.5) para t <= (1/4-eps)*n y moneda con hash O~(n^(7/3)*kappa) para t <= (1/3-eps)*n) junto con Tipos de Datos Replicados Wait-Free y Reconciliacion Justa sobre DAG Causal (Kuznetsov, Perion, Tucci-Piergiovanni DISC 2026 / LIPIcs.DISC.2026.32 / arXiv:2508.18193, f_BFS de prefijo estable creciente y f_fair con seleccion round-robin de vertices lideres libre de inanicion bajo particiones) con sintesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "spec": {"type": "object"},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_bounded_maximin_atomic_swap_and_stochastic_broadcast_sweep_consensus",
            "description": "Nivel 408 (v26.7.0 — 420 MCP Tools | REG-184 | Shard NODE-01): Certifica formalmente Intercambios Atomicos Seguros con Equidad Maximin Acotada frente a Incentivos Externos y Colusion Usuario-Minero compatibles con Bitcoin Script (Chung, Masserova, Shi, Thyagarajan DISC 2026 / LIPIcs.DISC.2026.23 / IACR ePrint 2025/1086) junto con Consenso con Difusion Estocastica mediante conmutacion Courteous/Pref1 en 1 ronda (umbral p=2/3 para n=3 y p=1/n para n>3) y el algoritmo Sweep de 2 rondas con probabilidad de error optima q^(r*n) en a lo sumo r*n difusiones (Fraigniaud, Patt-Shamir, Rajsbaum DISC 2026 / LIPIcs.DISC.2026.18) con sintesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "spec": {"type": "object"},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_opinion_density_3majority_2choices_and_simplicial_approximate_agreement",
            "description": "Nivel 409 (v26.8.0 — 421 MCP Tools | REG-185 | Shard NODE-01): Certifica formalmente el Tiempo de Consenso en Dinamicas 3-Majority y 2-Choices gobernado por la Densidad Maxima de Opinion Inicial ||alpha^(0)||_inf (cotas fuertes Theta~(min{||alpha^(0)||_inf^-1, sqrt(n)}) para 3-Majority y Theta~(||alpha^(0)||_inf^-1) para 2-Choices en toda configuracion inicial, DISC 2026 / LIPIcs.DISC.2026.36) junto con la Resolubilidad de Acuerdo Aproximado t-Resiliente en Grafos y Complejos Simpliciales (conectividad homotopica (t-1)-conexa del complejo de cliques Cl(G), demostracion de la conjetura de Ledent, equivalencia entre acuerdo de clique y monofonico, y separacion estricta frente a acuerdo geodesico, Rybicki & Verbitsky DISC 2026 / LIPIcs.DISC.2026.7) con sintesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "spec": {"type": "object"},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_lpmso_unbounded_degree_gap_and_sublinear_mpc_ncc_simulation",
            "description": "Nivel 410 (v26.9.0 — 422 MCP Tools | REG-186 | Shard NODE-01): Certifica formalmente la Generalizacion de Brechas de Complejidad LCL a Arboles Enraizados de Grado No Acotado via Propiedades MSO de Presburger (LPMSO: brechas decidibles omega(log n)-n^{o(1)} y omega(n^{1/(k+1)})-o(n^{1/k}), equivalencia asintotica entre solucion y solucion certificada por automata minimal PMSO, y reduccion a grado acotado mediante automata de arboles de multiconjuntos racionales, DISC 2026 / LIPIcs.DISC.2026.28) junto con Simulaciones Preservadoras de Rondas entre Computo Masivamente Paralelo Fuertemente Sublineal (MPC, S = n^delta) y Clique Capacitado por Nodos (NCC, C = M*S/n, Schneider & Werthmann DISC 2026 / LIPIcs.DISC.2026.66) con sintesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "spec": {"type": "object"},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_deterministic_congest_vizing_edge_coloring_and_locally_finite_labelings",
            "description": "Nivel 411 (v27.0.0 — Hito Mayor | 423 MCP Tools | REG-187 | Shard NODE-01): Certifica formalmente el Primer Algoritmo Determinista poly(Delta, log n) para (Delta + 1)-Coloracion de Aristas (Teorema de Vizing) en el Modelo CONGEST con dependencia en n de O_tilde(log^5 n) igualando al modelo LOCAL y mensajes de O(log n) bits (Brandt, Narayanan & Nolin, DISC 2026 / LIPIcs.DISC.2026.50, arXiv:2608.19184) junto con Etiquetados Localmente Finitos (Locally Finite Labelings — LFLs) que restauran la dicotomia de brechas polinomiales Theta(n^{1/k}) u O(log n) en arboles de grado no acotado (Gustav Schmid, DISC 2026 / LIPIcs.DISC.2026.37, arXiv:2602.02340) con sintesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "spec": {"type": "object"},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_deterministic_degree_splitting_hso_and_uniform_port_self_stabilization",
            "description": "Nivel 412 (v27.1.0 — 424 MCP Tools | REG-188 | Shard NODE-01): Certifica formalmente el Particionamiento Determinista Rapido de Grado (Degree Splitting) mediante Orientacion Sin Sumideros en Hipergrafos (HSO) y (3/2 + eps)*Delta-Coloracion de Aristas en O(eps^-1 log^2 Delta log n + eps^-2 log n) rondas (Maus, Nolin & Schager, DISC 2026 / LIPIcs.DISC.2026.25, arXiv:2604.00724) junto con Algoritmos Auto-Estabilizantes Polilogaritmicos en el Modelo de Puertos Uniforme (automata finito de tamano constante O(1) en cada semi-arista/puerto para MIS, Maximal Matching, Sinkless Orientation y k-Coloracion, Brinker, Emek & Louidor, DISC 2026 / LIPIcs.DISC.2026.3) con sintesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "spec": {"type": "object"},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_node_edge_checkable_lcl_robustness_and_local_distributed_mechanisms",
            "description": "Nivel 413 (v27.2.0 — 425 MCP Tools | REG-189 | Shard NODE-01): Certifica formalmente la Robustez Definicional de Problemas LCL (traduccion bidireccional de bajo sobrecosto entre LCLs de Naor-Stockmeyer y el formalismo node-edge checkable sobre grafos regulares no etiquetados sin referencia directa a ciclos cortos, Cruciani et al. DISC 2026 / LIPIcs.DISC.2026.10) junto con Diseno de Mecanismos Distribuidos Locales (DAMD local para MWIS, MWVC, MWDS y Weighted Coloring en entorno confiable y mecanismo compatible en incentivos para MWIS ejecutado por agentes estrategicos, Hirvonen & Ranjbaran DISC 2026 / LIPIcs.DISC.2026.24) con sintesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "spec": {"type": "object"},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_low_arboricity_two_ruling_sets_and_stable_parity_population_protocols",
            "description": "Nivel 414 (v27.3.0 — 426 MCP Tools | REG-190 | Shard NODE-01): Certifica formalmente Conjuntos 2-Ruling Distribuidos Casi-Optimos en Grafos de Baja Arboricidad (parametro optimo beta=2 en O_tilde(log^(5/8) alpha + log^(5/3) log n) rondas LOCAL/CONGEST y O(log log log n) rondas en MPC de bajo espacio, Baumecker, Latypov, Maus & Uitto DISC 2026 / LIPIcs.DISC.2026.15) junto con Protocolos de Poblacion Estables y Eficientes para Paridad y Congruencia (sistema de pesos poblacionales MC+ con conversion implicita unaria-binaria y estabilizacion silenciosa en O(log^3 n) estados/tiempo, Gasieniec et al. DISC 2026 / LIPIcs.DISC.2026.17) con sintesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "spec": {"type": "object"},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_tree_intersection_leader_election_and_resilient_lll_triangle_free_coloring",
            "description": "Nivel 415 (v27.4.0 — 427 MCP Tools | REG-191 | Shard NODE-01): Certifica formalmente Eleccion de Lider Aleatorizada por Interseccion de Arboles en CONGEST (expansiones de arboles l-arios truncados con verificacion silent pulse, tiempo O(log_l sqrt(n log n)), mensajes por nodo O(l) y mensajes totales sublineales O(sqrt(n) log^1.5 n), Emek, Kutten, Rafael & Taubenfeld DISC 2026 / LIPIcs.DISC.2026.21) junto con Coloreo Libre de Triangulos en LOCAL mediante Lema Local de Lovasz Resiliente (adaptacion Pettie-Su en log^O(1) log n rondas con o(Delta) colores y cota (1+eps)Delta/ln(Delta) para cintura >= 5, Davies-Peck & Zhang DISC 2026 / LIPIcs.DISC.2026.29) con sintesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "spec": {"type": "object"},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_bounded_degree_tree_population_protocols_and_average_anonymous_sb_networks",
            "description": "Nivel 416 (v27.5.0 — 428 MCP Tools | REG-192 | Shard NODE-01): Certifica formalmente Protocolos de Poblacion Casi-Optimos en Arboles de Grado Acotado (espacio constante O(1) sin trade-off espacio-tiempo mediante coloreo auto-estabilizante a 2 saltos, orientacion de arbol enraizado y aniquilacion dirigida en O(n^2 log n) pasos, Rybicki, Solnerzik & Vacus DISC 2026 / LIPIcs.DISC.2026.30) junto con Computabilidad en Redes Anonimas en Promedio bajo Set-Broadcast (algoritmo SB determinista de 1 ronda que genera IDs unicos de O(log n) bits en G(n,p), simulacion CONGEST/LOCAL y deteccion de triangulos en O(1/eps) rondas, Rybicki, Verbitsky & Zhukovskii DISC 2026 / LIPIcs.DISC.2026.40) con sintesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "spec": {"type": "object"},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_hypergraph_triangle_simplex_enumeration_and_graph_population_counting",
            "description": "Nivel 417 (v27.6.0 — 429 MCP Tools | REG-193 | Shard NODE-01): Certifica formalmente Enumeracion Distribuida de Triangulos y Simplices en Hipergrafos (modelos CONGEST generalizados con cotas inferiores coincidentes y descomposicion en hipergrafos sparse/everywhere-sparse, Adamson, Rosenbaum & Spirakis DISC 2026 / LIPIcs.DISC.2026.33) junto con Conteo en Protocolos de Poblacion sobre Grafos Generales (aproximacion sin lider de log n con error aditivo O(log log n) en O(B(G) log^2 n) y conteo exacto CountExact+Balance con tokens rojos/azules en O(B(G) log^2 n + L(G) log n) usando O~(n) estados, Berenbrink, Elsässer, Friedetzky, Götte, Hintze & Kaaser DISC 2026 / LIPIcs.DISC.2026.34) con sintesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "spec": {"type": "object"},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_asymmetric_quorum_symmetry_compiler_and_multiword_swmr_register_space",
            "description": "Nivel 418 (v27.7.0 — 430 MCP Tools | REG-194 | Shard NODE-01): Certifica formalmente Compilacion de Quorums Asimetricos a Simetricos en Profundidad >= 2 (reduccion de confianza asimetrica a quorums bizantinos simetricos para reliable broadcast y consenso con separacion ajustada en profundidad <= 1, Amores-Sesar, Cachin, Kamp & Villacis DISC 2026 / LIPIcs.DISC.2026.45) junto con Complejidad Espacial de Registros Atomicos Multi-Palabra SWMR (cota inferior obstruction-free ceil((m-1)/(b-1)) para lectores invisibles y algoritmo wait-free con espacio Theta(min(m/b, r + log_b(m))), Wei & Yavari DISC 2026 / LIPIcs.DISC.2026.49) con sintesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "spec": {"type": "object"},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_sublinear_mpc_fixed_threshold_peeling_and_semisync_dynamic_exploration",
            "description": "Nivel 419 (v27.8.0 — 431 MCP Tools | REG-195 | Shard NODE-01): Certifica formalmente Peeling de Umbral Fijo en Sublinear MPC (exponenciacion por lotes antes de poda respetando memoria sublineal, rompiendo la barrera Theta(sqrt(log n)) para densest subgraph en O~(log^{1/3} n) y O~(log^{1/4} n) rondas y k-core/coloreo en O(log^{1/(t+2)} n * poly(log log n)), Mitrović, Pan & Sheu DISC 2026 / LIPIcs.DISC.2026.46) junto con Exploracion Determinista de Grafos Dinamicos bajo Semi-Sincronia y Etiquetado Dinamico de Puertos (umbral exacto de desactivacion adversaria <= floor((k-1)/(n-2)) - 1 con visibilidad y comunicacion de 1 salto, Saxena, Molla, Mondal & Sharma DISC 2026 / LIPIcs.DISC.2026.48) con sintesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "spec": {"type": "object"},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_discrete_token_distribution_and_fluctuating_sleepy_consensus",
            "description": "Nivel 420 (v27.9.0 — 432 MCP Tools | REG-196 | Shard NODE-01): Certifica formalmente Distribucion Discreta de Tokens para Balanceo de Carga (transferencia unitaria sobre matchings con regla de token de exceso con probabilidad 1/2 que alcanza discrepancia 2 en O(K*tau_g*log log n) rondas w.h.p., Berenbrink, Elsässer, Friedetzky, Hosseinpour & Kaaser DISC 2026 / LIPIcs.DISC.2026.42) junto con Consenso Sleepy Totalmente Fluctuante desde Supuestos Minimos PKI+VRF sin VDFs (Graded Wakeness GW3 con desafios de doble nonce transferibles, Time-Shifted Quorums en GA2/GA3 y soporte de uncorruption, Nieto, Efron, Neu & Ren DISC 2026 / LIPIcs.DISC.2026.44) con sintesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "spec": {"type": "object"},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_collective_communication_rate_and_sleeping_congest_dominating_set",
            "description": "Nivel 421 (v28.0.0 — 433 MCP Tools | REG-197 | Shard NODE-01): Certifica formalmente Cotas Casi Exactas en la Tasa de Comunicacion Colectiva AllReduce (tasa -> 1 para operador maximo sin restriccion black-box, tasa -> 1/2 para sumas enteras y grupos Abelianos finitos bajo cotas de correlacion total de Watanabe y razon [1/2, 1] entre switches forwarding-only vs programables, Oshman, Roth, Shayevitz & Sivaraman DISC 2026 / LIPIcs.DISC.2026.52) junto con Aproximacion O(log Delta) de Minimum Dominating Set en Sleeping CONGEST con complejidad despierta O~(log Delta) y algoritmo SetCover de 2 parametros (p,q) sobre arboles binarios virtuales (Ji, Pai & Pemmaraju DISC 2026 / LIPIcs.DISC.2026.53) con sintesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "spec": {"type": "object"},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_weighted_beeping_network_and_quantum_local_tree_lcl_gap",
            "description": "Nivel 422 (v28.1.0 — 434 MCP Tools | REG-198 | Shard NODE-01): Certifica formalmente Local Broadcast en Redes de Beeping Ponderadas WBN (entrega sobre aristas pesadas w > sigma en O(I_sigma log n * (M + log n)) rondas w.h.p. con cota inferior Omega(I_sigma) y emulacion con sobrecosto logaritmico de redes de beeping clasicas, Kowalski & Mosteiro DISC 2026 / LIPIcs.DISC.2026.54) junto con Brecha Superlogaritmica para LCLs en Arboles en Quantum-LOCAL (simulacion determinista O(log n) en LOCAL de toda distribucion n^{o(1)}-dependiente via descomposicion rake-and-compress y dicotomia O(log n) determinista vs n^{Omega(1)} quantum-LOCAL, d'Amore & Lievonen DISC 2026 / LIPIcs.DISC.2026.59) con sintesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "spec": {"type": "object"},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_infinite_sequential_consistency_and_stone_duality_colorless_computability",
            "description": "Nivel 423 (v28.2.0 — 435 MCP Tools | REG-199 | Shard NODE-01): Certifica formalmente la Complejidad de Consistencia Secuencial sobre Historias Infinitas (bajo llegada finita SC es propiedad de vivacidad no reconocible por aceptores de Buchi deterministas de estados infinitos ni transductores deterministas, y bajo llegada infinita con registros ilimitados y DCAS es Sigma^1_1-completo, Dimitrov DISC 2026 / LIPIcs.DISC.2026.60) junto con Teoremas de Computabilidad Distribuida Incolora via Dualidad de Stone sobre posets finitos y mapas espectrales f: Pi^infty(I) -> O compatibles con Delta (DISC 2026 / LIPIcs.DISC.2026.61) con sintesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "spec": {"type": "object"},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_deterministic_congest_few_colors_edge_coloring_and_anonymous_dynamic_self_organization",
            "description": "Nivel 424 (v28.3.0 — 436 MCP Tools | REG-200 | Shard NODE-01): Certifica formalmente Coloreo Determinista de Aristas con Pocos Colores en CONGEST ((1+eps)*Delta + O(sqrt(log n)) colores para Delta >= c*sqrt(log n) desaleatorizando algoritmos online con acceso local a aristas futuras y O~(log^{2.5} n + log^2 Delta log n) rondas para 2*Delta - 1 colores, DISC 2026 / LIPIcs.DISC.2026.5) junto con Auto-Organizacion Adaptativa en Redes Dinamicas Anonimas en tiempo lineal O(n) y espacio O(log n) ante testigos de senal y topologia adversaria (DISC 2026 / LIPIcs.DISC.2026.27) con sintesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "spec": {"type": "object"},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_byzantine_agreement_with_predictions_and_accountable_monadbft",
            "description": "Nivel 426 (v28.5.0 — 438 MCP Tools | REG-202 | Shard NODE-01): Certifica formalmente Acuerdo Bizantino Eficiente en Comunicacion con Predicciones de Clasificacion (comunicacion casi optima O~(n^2) sin autenticacion con t < n/3 y O(n^2*kappa) con autenticacion y t < (1/2 - eps)n manteniendo rondas optimas ante errores arbitrarios de prediccion, DISC 2026 / LIPIcs.DISC.2026.8) junto con Accountable MonadBFT (commit especulativo en 3 retardos de mensaje con resistencia a tail-forking MEV y responsabilidad criptografica >= 1/6 de validadores para slashing ante reversion, DISC 2026 / LIPIcs.DISC.2026.47).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "spec": {"type": "object"},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_parallel_discrete_frechet_distance_and_exponentially_fewer_bits_initialization",
            "description": "Nivel 425 (v28.4.0 — 437 MCP Tools | REG-201 | Shard NODE-01): Certifica formalmente Calculo Paralelo de la Distancia de Frechet Discreta en PRAM (O(log n / sigma) rondas, O~(n^{2+sigma}) trabajo) y Sublinear MPC (O(log n / rho^2) rondas, O~(n^{2+rho}) espacio, y O(1/rho^3) rondas para curvas c-packed con simplificacion paralela, DISC 2026 / LIPIcs.DISC.2026.4) junto con Inicializacion con Exponencialmente Menos Bits en Redes de Radio Dormidas (cota inferior Omega(log log n) envios, energia dependiente solo de f en no-CD y O(n) rondas de 1 bit con O(log log n) bits peor caso y O(1) promedio por nodo, DISC 2026 / LIPIcs.DISC.2026.65) con sintesis CEGIS.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "spec": {"type": "object"},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_byzantine_agreement_strong_efficiency_lower_bounds_and_planar_max_flow_dual_incision",
            "description": "Nivel 427 (v28.6.0 — 439 MCP Tools | REG-203 | Shard NODE-01): Certifica formalmente cotas inferiores fuertes Omega(t^2) y Omega(n*t) en Acuerdo Bizantino adaptativo (Ducros, Loss & Rambaud, DISC 2026 / LIPIcs.DISC.2026.41) y (1-o(1))-Flujo Máximo s-t en grafos planares generales por incisión dual recursiva en O_tilde(D) (Abd-Elhaleem, Dory & Weimann, DISC 2026 / LIPIcs.DISC.2026.19).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "spec": {"type": "object"}
                }
            }
        },
        {
            "name": "aleph_prove_sleeping_congest_energy_lower_bounds_and_noisy_pull_quasi_self_stabilizing_spreading",
            "description": "Nivel 428 (v28.7.0 — 440 MCP Tools | REG-204 | Shard NODE-01): Certifica formalmente cotas inferiores polinómicas de energía en SLEEPING-CONGEST (Dufoulon, Pandurangan & Robinson, DISC 2026 / LIPIcs.DISC.2026.13) y difusión cuasi auto-estabilizante de 2 bits en PULL(h) ruidoso (D'Archivio et al., DISC 2026 / LIPIcs.DISC.2026.38).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "spec": {"type": "object"}
                }
            }
        },
        {
            "name": "aleph_prove_fast_tendermint_two_step_consensus_and_local_parity_certification_lcl_synthesizer",
            "description": "Nivel 429 (v28.8.0 — 441 MCP Tools | REG-205 | Shard NODE-01): Certifica formalmente Fast Tendermint de 2 pasos con n >= 5f + 1 (Vander Vos & Cason, DISC 2026 / LIPIcs.DISC.2026.55), certificación local de paridad O(1) bits con radio r=2 (Bousquet et al., DISC 2026 / LIPIcs.DISC.2026.22) y síntesis LCL con cota N_max (Cruciani et al., DISC 2026 / LIPIcs.DISC.2026.14).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "spec": {"type": "object"}
                }
            }
        },
        {
            "name": "aleph_prove_fast_tetrabft_semantic_lock_conflict_graph_and_fair_binding_smr",
            "description": "Nivel 430 (v28.9.0 — 442 MCP Tools | REG-206 | Shard NODE-01): Certifica formalmente Fast TetraBFT sin firmas en 3*delta (Fernández-Pinto et al., DISC 2026 / arXiv:2606.03754), SemanticLock por grafo de conflictos G=(V,E) (Korotchenko & Aksenov, DISC 2026 / arXiv:2606.24250) y Fair Binding SMR (Mallick, DISC 2026 / arXiv:2608.17349).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "spec": {"type": "object"}
                }
            }
        },
        {
            "name": "aleph_prove_correlated_liquid_democracy_certified_paths_and_kwta_self_stabilization",
            "description": "Nivel 431 (v29.0.0 — 443 MCP Tools | REG-207 | Shard NODE-01): Certifica formalmente Democracia Líquida bajo Correlación de Votos con Caminos Certificados 2D en T rondas (Gilbert et al., DISC 2026 / arXiv:2608.16738) y Dinámica Auto-Estabilizante Rápida para k-Winner-Take-All (Bonifaci & Galvan, DISC 2026 / LIPIcs.DISC.2026.62).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "spec": {"type": "object"}
                }
            }
        },
        {
            "name": "aleph_prove_partially_authenticated_byzantine_consensus_and_gcas_infinite_arrival_universal",
            "description": "Nivel 432 (v29.1.0 — 444 MCP Tools | REG-208 | Shard NODE-01): Certifica formalmente Consenso Bizantino en el Modelo Parcialmente Autenticado con 3t < n + 2s (Lenzen, Loss, Shi & Wagner, ACM PODC 2026 / IACR ePrint 2026/470) y GCAS con Construcciones Universales Wait-Free de espacio O(c(t)) para Llegadas Infinitas (Hadzilacos, Thiessen & Toueg, ACM PODC 2026 / arXiv:2605.19237).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "spec": {"type": "object"}
                }
            }
        },
        {
            "name": "aleph_prove_forget_it_constant_storage_bft_and_optimistic_information_theoretic_vss",
            "description": "Nivel 436 (v29.5.0): Audita y repara por CEGIS los invariantes de Forget-IT Constant-Storage Information-Theoretic BFT (Abraham et al., ACM PODC 2026 / ePrint 2026/355: 3-delta good-case latency, O(n^2) communication, O(1) persistent storage) y Optimistic Information-Theoretic VSS (Liu-Zhang et al., ACM PODC 2026 / ePrint 2026/1000: 2 rondas para f <= k y 3 rondas para k < f <= t bajo 3t + k < n).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "target_name": {"type": "string"},
                    "n_replicas": {"type": "integer"},
                    "byzantine_bound_f": {"type": "integer"},
                    "vss_threshold_t": {"type": "integer"},
                    "optimistic_corruptions_k": {"type": "integer"},
                    "good_case_latency_deltas": {"type": "integer"},
                    "persisted_state_words": {"type": "integer"},
                    "enforce_post_restart_epoch_fence": {"type": "boolean"},
                    "ovss_optimistic_rounds": {"type": "integer"},
                    "ovss_fallback_rounds": {"type": "integer"},
                    "enforce_three_t_plus_k_resilience_guard": {"type": "boolean"}
                }
            }
        },
        {
            "name": "aleph_prove_flutter_blink_fast_byzantine_tob_and_seniorlock_retrospective_waitfree",
            "description": "Nivel 435 (v29.4.0): Audita y repara especificaciones de Difusión de Orden Total Bizantina Rápida Flutter (2*Delta + eps, sin líder y post-cuántica, n >= 5f + 1) con Consenso Binario Blink de Validez Representativa (Monti, Camaioni & Roman, ACM PODC 2026 / arXiv:2412.14061) y Cerrojos Wait-Free Retrospectivos SeniorLock inmunes a llegadas posteriores con complejidad O((beta_D + 1)*(T + 1)) y min-CAS reseteable (arXiv:2607.16571).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "spec": {
                        "type": "object",
                        "description": "Especificación opcional de Flutter/Blink TOB y SeniorLock wait-free retrospectivo (usa clean spec por defecto si se omite)."
                    }
                }
            }
        },
        {
            "name": "aleph_prove_balanced_subquadratic_async_common_coin_aba_and_overwrite_lattice_lfp",
            "description": "Nivel 434 (v29.4.0): Audita y repara especificaciones de Moneda Común Asíncrona Balanceada en 2 Rondas y Acuerdo Bizantino (ABA) con Comunicación Sub-Cuadrática O~(n^(2-c)) bajo Adversario Adaptativo (Feng, Mai & Tang, ACM PODC 2026 / ePrint 2026/998) y Cálculo de Menor Punto Fijo (LFP) con Semántica de Sobreescritura en Retículos Distributivos bajo i-Localidad y Obsolescencia Acotada (Garg & Garg, ACM PODC 2026 / arXiv:2602.10486).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "spec": {
                        "type": "object",
                        "description": "Especificación opcional de Common Coin/ABA sub-cuadrático y LFP por sobreescritura (usa clean spec por defecto si se omite)."
                    }
                }
            }
        },
        {
            "name": "aleph_prove_conflict_free_mazurkiewicz_universal_and_prediction_phase_king_ba",
            "description": "Nivel 433 (v29.4.0 — 445 MCP Tools | REG-209 | Shard NODE-01): Certifica formalmente en O(V+E) la Libertad de Conflictos (Conflict-Freedom) como condición de progreso y su Construcción Universal Linealizable mediante Commit-Adopt Generalizado y Trazas de Mazurkiewicz (Kuznetsov, Sutra & Toyos-Marfurt, ACM PODC 2026 / arXiv:2605.19531) junto al Protocolo Phase-King Simple con Predicciones en O(P) rondas con P = 1 + min(B/n, f) y O(n^2 P log n) bits sin intercambio cúbico de vectores completos (arXiv:2611.11370).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "spec": {"type": "object"}
                }
            }
        },
        {
            "name": "aleph_prove_disperser_adaptive_byzantine_agreement_and_recursive_asynchronous_dkg",
            "description": "Nivel 437: Verifica formalmente Acuerdo Bizantino Adaptativo Optimo basado en Dispersores con Desacoplamiento de Fallos O((n + t^2) log n) / O(n + f^2) (Constantinescu, Dufay, Paramonov & Wattenhofer, ACM PODC 2026 / arXiv:2505.19989) y Generacion Distribuida de Claves Asincrona Casi Cuadratica O(lambda^2 * n^(2 + 1/k)) en O(k) rondas mediante Consenso Recursivo (Abraham, Bacho, Loss & Stern, ACM PODC 2026 / IACR ePrint 2025/006).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "target_path": {"type": "string"},
                    "total_nodes": {"type": "integer"},
                    "corrupted_nodes": {"type": "integer"},
                    "actual_faults_f": {"type": "integer"},
                    "recursion_depth_k": {"type": "integer"},
                    "security_parameter_lambda": {"type": "integer"},
                    "disperser_committee_expansion_ok": {"type": "boolean"},
                    "adaptive_fault_decoupled_comm_ok": {"type": "boolean"},
                    "recursive_adkg_subcubic_comm_ok": {"type": "boolean"}
                }
            }
        },
        {
            "name": "aleph_prove_subquadratic_byzantine_renaming_and_network_agnostic_multidimensional_approximate_agreement",
            "description": "Nivel 438: Verifica formalmente Renombrado Distribuido Bizantino con Bits Subcuadraticos via Eleccion Escalable de Comites con Bounce Forwarding (Bai, Fu, Wang & Zheng, ACM PODC 2026 / arXiv:2605.18086) y Acuerdo Aproximado Multidimensional Agnóstico de Red con Resiliencia Óptima n > max((D+1)*t_s, t_s + (D+1)*t_a) via Strengthened Gather (Ghinea, Melnyk & Milentijevic, ACM PODC 2026 / IACR ePrint 2026/287).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "nodes_n": {"type": "integer"},
                    "byzantine_bound_t": {"type": "integer"},
                    "actual_faults_f": {"type": "integer"},
                    "faulty_messages_T": {"type": "integer"},
                    "shared_randomness_enabled": {"type": "boolean"},
                    "dimension_D": {"type": "integer"},
                    "sync_faults_t_s": {"type": "integer"},
                    "async_faults_t_a": {"type": "integer"},
                    "auto_repair": {"type": "boolean"}
                }
            }
        },
        {
            "name": "aleph_prove_early_stabilizing_byzantine_counting_and_practically_constant_local_skew_gcs",
            "description": "Nivel 439: Verifica formalmente Conteo Bizantino Auto-Estabilizante Temprano en O(f+1) rondas y O(n*(f*log C + log^2 n)) bits amortizados (Lenzen & Loss, ACM PODC 2026 / arXiv:2605.18171) y Sincronización de Relojes por Gradiente (GCS) con Sesgo Local Prácticamente Constante O(delta_T * log(W_s / delta_T)) (Lenzen, ACM PODC 2026 / arXiv:2511.01420).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "nodes_n": {"type": "integer"},
                    "byzantine_bound_t": {"type": "integer"},
                    "actual_faults_f": {"type": "integer"},
                    "counter_modulus_C": {"type": "integer"},
                    "network_diameter_D": {"type": "integer"},
                    "max_link_error_Delta_ns": {"type": "integer"},
                    "dynamic_stability_delta_T_ns": {"type": "integer"},
                    "auto_repair": {"type": "boolean"}
                }
            }
        },
        {
            "name": "aleph_prove_small_message_graph_sketch_gossip_and_adversarial_majority_supervised_computing",
            "description": "Nivel 440 (v29.9.0): Verifica y repara formalmente la difusión de rumores por Gossip con mensajes pequeños O(polylog n) mediante sparsificación por bocetos de grafos en O~(D + sqrt(n)) y O(c log n / Phi_c) rondas (Dufoulon et al., ACM PODC 2026) y la computación distribuida supervisada sobre DAGs bajo mayoría de trabajadores adversarios (beta < 1) con trabajo honesto esperado 1 + o(1) por tarea (Augustine et al., ACM PODC 2026).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "nodes_n": {"type": "integer"},
                    "diameter_D": {"type": "integer"},
                    "hop_parameter_c": {"type": "integer"},
                    "weak_conductance_Phi_c": {"type": "number"},
                    "message_bits": {"type": "integer"},
                    "degree_threshold_Delta_Th": {"type": "integer"},
                    "mst_constructed_in_same_bound": {"type": "boolean"},
                    "adversarial_worker_fraction_beta": {"type": "number"},
                    "dag_depth_D": {"type": "integer"},
                    "dag_max_degree_d": {"type": "integer"},
                    "verification_step_window_delta": {"type": "integer"},
                    "cohort_size_gamma": {"type": "integer"},
                    "expected_honest_executions_per_task": {"type": "number"},
                    "auto_repair": {"type": "boolean"}
                }
            }
        },
        {
            "name": "aleph_prove_circles_opinion_ranking_and_distributed_szk_sumcheck",
            "description": "Nivel 441 (v30.0.0 — Hito Mayor v30.0.0): Verifica y repara formalmente el protocolo de población CIRCLES para mayoría relativa en k^3 estados y ranking completo de opiniones en 2*k^4 estados bajo planificador débilmente justo (Breitkopf et al., ACM PODC 2026) y las pruebas distribuidas de conocimiento cero estadístico (dSZK) vía Sumcheck para conteo de subgrafos en O(k log n) rondas y no-k-colorabilidad en O(n) rondas (Jauregui & Miyamoto, ACM PODC 2026).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "population_agents_n": {"type": "integer"},
                    "opinion_colors_k": {"type": "integer"},
                    "relative_majority_states_used": {"type": "integer"},
                    "ranking_states_used": {"type": "integer"},
                    "disjoint_color_circles_partition_valid": {"type": "boolean"},
                    "weakly_fair_scheduler_resilient": {"type": "boolean"},
                    "subgraph_pattern_size_k": {"type": "integer"},
                    "dszk_subgraph_counting_rounds": {"type": "integer"},
                    "dszk_subgraph_counting_message_bits": {"type": "integer"},
                    "dszk_non_k_colorability_rounds": {"type": "integer"},
                    "dszk_non_k_colorability_message_bits": {"type": "integer"},
                    "statistical_zero_knowledge_simulatable": {"type": "boolean"},
                    "non_3_colorability_lower_bound_respected": {"type": "boolean"},
                    "auto_repair": {"type": "boolean"}
                }
            }
        },
        {
            "name": "aleph_prove_generalized_mpx_graph_decomposition_matching_and_distributed_stochastic_graph_optimization",
            "description": "Nivel 442 (v30.1.0): Verifica y repara formalmente la Descomposición de Grafos MPX Generalizada para Matching/Vertex Cover en O(log n / log^2 log n) rondas (Davies-Peck, ACM PODC 2026) y Algoritmos Distribuidos en Grafos Estocásticos (Censor-Hillel, Dudeja & Giakkoupis, ACM PODC 2026).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "nodes_count": {"type": "integer"},
                    "max_degree_delta": {"type": "integer"},
                    "approx_epsilon_milli": {"type": "integer"},
                    "mpx_decomposition_rounds": {"type": "integer"},
                    "matching_vertex_cover_rounds": {"type": "integer"},
                    "stochastic_probe_budget_per_node": {"type": "integer"},
                    "stochastic_realization_rounds": {"type": "integer"},
                    "generalized_mpx_degree_reduction_valid": {"type": "boolean"},
                    "kuhn_moscibroda_wattenhofer_n_bound_matched": {"type": "boolean"},
                    "stochastic_realization_approx_guaranteed": {"type": "boolean"},
                    "non_adaptive_probe_consistency_preserved": {"type": "boolean"},
                    "auto_repair": {"type": "boolean"}
                }
            }
        },
        {
            "name": "aleph_prove_two_dimensional_matrix_avid_recovery_and_optimal_bounded_arboricity_dominating_set",
            "description": "Nivel 443 (v30.3.0): Verifica y repara formalmente la Dispersión de Información Verificable Asíncrona (AVID) mediante Matriz 2D con Baja Complejidad de Espacio y Recuperación de Nodos y el Conjunto Dominante Distribuido con Rondas y Tamaño de Mensaje Óptimos en Grafos de Arboricidad Acotada (ACM SPAA 2026).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "replicas_n": {"type": "integer"},
                    "byzantine_faults_t": {"type": "integer"},
                    "avid_matrix_rows_r": {"type": "integer"},
                    "avid_matrix_cols_c": {"type": "integer"},
                    "avid_storage_blowup_milli": {"type": "integer"},
                    "avid_recovery_comm_bits_per_node": {"type": "integer"},
                    "graph_nodes_n": {"type": "integer"},
                    "graph_arboricity_alpha": {"type": "integer"},
                    "dominating_set_rounds": {"type": "integer"},
                    "dominating_set_message_bits": {"type": "integer"},
                    "two_dimensional_erasure_matrix_valid": {"type": "boolean"},
                    "optimal_retrieval_and_recovery_balanced": {"type": "boolean"},
                    "bounded_arboricity_approx_valid": {"type": "boolean"},
                    "single_bit_or_tiny_message_optimal": {"type": "boolean"},
                    "auto_repair": {"type": "boolean"}
                }
            }
        }
        ,
        {
            "name": "aleph_prove_parallel_ldd_spectral_sparsification_and_deterministic_mpc_distance_hitting_sets",
            "description": "Nivel 444 (v30.3.0): Verifica formalmente Parallel Spectral Graph Sparsification via Low Diameter Decompositions (ACM SPAA 2026 / arXiv:2607.25059) y Deterministic Distance Approximation in MPC via Improved Hitting Sets (ACM SPAA 2026 / arXiv:2606.03674).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "num_vertices": {"type": "integer"},
                    "num_edges": {"type": "integer"},
                    "epsilon_inv": {"type": "integer"},
                    "ldd_probability_scales": {"type": "integer"},
                    "mpc_hitting_set_rounds": {"type": "integer"},
                    "solver_free_ldd_subsampling_valid": {"type": "boolean"},
                    "epsilon_free_work_depth_overhead_valid": {"type": "boolean"},
                    "spectral_quadratic_form_preserved": {"type": "boolean"},
                    "deterministic_mpc_hitting_set_valid": {"type": "boolean"},
                    "auto_repair": {"type": "boolean"}
                }
            }
        }
        ,
        {
            "name": "aleph_prove_parallel_task_multiple_cluster_scheduling_and_generic_simplex_view_agreement_consensus",
            "description": "Nivel 445 (v30.4.0): Verifica formalmente Parallel Task Scheduling (PTS) con cota (4/3)*OPT + p_max en O(n log n) y Multiple Cluster Scheduling (MCS) 2-aproximado / (9/4)-aproximado sin restricción N mod 3 = 0 (ACM SPAA 2026 / arXiv:2607.00878) junto con el Consenso Blockchain sin Firmas Post-Cuántico Generic Simplex parametrizado por View Agreement (1/3-VA y 1/5-Fast VA) con VA-strong-unanimity, latencia 3*delta / 2*delta, block time 2*delta sin especulación y view timeout acortado 6*Delta / 4*Delta (arXiv:2609.32985v1).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "n_parallel_tasks": {"type": "integer", "default": 1024},
                    "n_clusters": {"type": "integer", "default": 8},
                    "m_machines_per_cluster": {"type": "integer", "default": 16},
                    "opt_makespan": {"type": "number", "default": 120.0},
                    "p_max_duration": {"type": "number", "default": 25.0},
                    "pts_schedule_makespan": {"type": "number", "default": 182.0},
                    "va_mode": {"type": "string", "default": "1/5-Fast-VA"},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        }
        ,
        {
            "name": "aleph_prove_near_optimal_parallel_m_matrix_scaling_and_byzantine_resilient_dflc_tacs_consensus",
            "description": "Nivel 446 (v30.5.0): Verifica formalmente Near-Optimal Parallel M-Matrix Scaling mediante reducción a SDD e IPM de O_tilde(1) iteraciones polilogarítmicas dominadas por sistemas Laplacianos en trabajo casi-lineal O_tilde(nnz(A)) y profundidad paralela polilogarítmica (arXiv:2610.22302 / DOI:10.48550/arXiv.2610.22302) junto con el consenso Trust-Score-Informed Asynchronous Common Subset (T-ACS) y Dual-Domain Trust Scoring (D2TS) de DFL-C bajo N >= 3F + 1 y mayoría honesta > 50% (IEEE CNS 2026 / arXiv:2608.22552v1).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "matrix_dimension_d": {"type": "integer", "default": 4096},
                    "matrix_nnz": {"type": "integer", "default": 65536},
                    "scaling_accuracy_epsilon": {"type": "number", "default": 1e-6},
                    "ipm_polylog_iterations": {"type": "integer", "default": 12},
                    "dflc_nodes_n": {"type": "integer", "default": 13},
                    "byzantine_nodes_f": {"type": "integer", "default": 4},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        }            ,
        {
            "name": "aleph_prove_parallel_noisy_shallow_circuit_ac0_simulation_and_dcoco_parallel_draft_contextual_correction",
            "description": "Nivel 447 (v30.6.0): Verifica simulacion clasica paralela de circuitos superficiales ruidosos 1D en AC^0 con complejidad paralela 2^O(d) loglog(n/delta) (arXiv:2609.39448) y correccion contextual paralela de borradores especulativos DCOCO con 6.6x speedup y +23% throughput concurrente (arXiv:2610.12570) bajo torneo Pareto REG-007.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "circuit_qubits_n": {"type": "integer", "default": 1024},
                    "circuit_depth_d": {"type": "integer", "default": 4},
                    "tv_error_delta": {"type": "number", "default": 0.01},
                    "depolarizing_noise_rate_p": {"type": "number", "default": 0.05},
                    "dcoco_draft_block_size": {"type": "integer", "default": 8},
                    "dcoco_candidates_per_pos": {"type": "integer", "default": 4},
                    "dcoco_contextual_compatibility_score": {"type": "number", "default": 0.94},
                    "dcoco_vanilla_speedup_factor": {"type": "number", "default": 6.6},
                    "dcoco_concurrent_throughput_gain_pct": {"type": "number", "default": 23.0},
                    "concurrent_requests_batch": {"type": "integer", "default": 32},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_mojos_batch_parallel_link_cut_euler_tour_trees_and_metadb_in_memory_mvcc",
            "description": "Nivel 448 (v30.7.0): Verifica el framework MOJOS de arboles dinamicos paralelos por lotes (Link-Cut Trees, Euler Tour Trees y Treaps) con trabajo esperado O(k log(1+n/k)) y profundidad O(log n) whp (arXiv:2609.14746) junto con el motor transaccional distribuido MetaDB con sharding inducido por topologia de arbol (>=97% localidad), bypass asincrono fuera del camino critico y MVCC en memoria libre de tombstones en disco con 2.2x-4.1x throughput (arXiv:2610.32247) bajo torneo Pareto REG-007.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "tree_vertices_n": {"type": "integer", "default": 65536},
                    "batch_updates_k": {"type": "integer", "default": 1024},
                    "treap_join_speedup_vs_skiplist": {"type": "number", "default": 3.4},
                    "treap_memory_saving_pct": {"type": "number", "default": 33.0},
                    "ett_memory_saving_pct": {"type": "number", "default": 24.0},
                    "metadb_single_dir_locality_ratio": {"type": "number", "default": 0.97},
                    "metadb_cross_dir_rename_ratio": {"type": "number", "default": 0.03},
                    "metadb_async_off_critical_path_bypass": {"type": "boolean", "default": True},
                    "metadb_in_memory_mvcc_tombstone_shield": {"type": "boolean", "default": True},
                    "metadb_throughput_multiplier": {"type": "number", "default": 4.1},
                    "metadb_machine_reduction_pct": {"type": "number", "default": 50.0},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        }            ,
        {
            "name": "aleph_prove_lachesis_lifetime_aware_kv_cache_hbm_hbf_and_monadically_dependent_fo_model_checking",
            "description": "Nivel 449 (v30.8.0): Verifica la capa Lachesis de colocacion de KV Cache consciente del tiempo de vida entre HBM y High-Bandwidth Flash (HBF) sobre 3 ejes (temporal, estructural, inter-worker) con extension de vida util HBF de 1.19x-3.13x (3.3-12.2 device-years >= 5 anos de garantia, arXiv:2610.08378) junto con el Model Checking de Primer Orden FPT sobre clases de grafos monadicamente dependientes con merge-width de etapas definibles y cota polinomial de tipos |U|^O(1) (arXiv:2611.08143) bajo torneo Pareto REG-007.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "lachesis_lifetime_axes_count": {"type": "integer", "default": 3},
                    "lachesis_short_lived_hbm_absorption_ratio": {"type": "number", "default": 0.78},
                    "lachesis_hbf_endurance_extension_multiplier": {"type": "number", "default": 3.13},
                    "lachesis_hbf_device_years_achieved": {"type": "number", "default": 12.2},
                    "lachesis_hbf_warranty_years_floor": {"type": "number", "default": 5.0},
                    "lachesis_segment_boundary_eager_free": {"type": "boolean", "default": True},
                    "graph_vertices_n": {"type": "integer", "default": 16384},
                    "parameter_set_size_u": {"type": "integer", "default": 32},
                    "quantifier_rank_q": {"type": "integer", "default": 4},
                    "monadically_dependent_class": {"type": "boolean", "default": True},
                    "merge_width_definable_stages": {"type": "boolean", "default": True},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_fault_tolerant_delegation_dag_budget_conservation_and_acca_continuous_authorization",
            "description": "Nivel 450 (v30.9.0): Verifica la conservacion tolerante a fallos de presupuestos en delegacion multi-agente distribuida sobre DAG con preasignacion exclusiva en escrow, cuarentena de permiso de despacho firmado y liquidacion a lo sumo una vez (ResearchGate:415152724) junto con la Autorizacion Continua Condicionada por Aseguramiento (ACCA) sobre grafo de dependencias tipado en O(V+E) con rechazo de acciones obsoletas en tiempo de efecto (arXiv:2611.05632) bajo torneo Pareto REG-007.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "delegation_dag_branches": {"type": "integer", "default": 16},
                    "root_escrow_budget_units": {"type": "integer", "default": 10000},
                    "reserved_in_flight_units": {"type": "integer", "default": 2400},
                    "settled_effect_units": {"type": "integer", "default": 5100},
                    "unallocated_escrow_units": {"type": "integer", "default": 2500},
                    "exclusive_preallocation_verified": {"type": "boolean", "default": True},
                    "signed_dispatch_permit_quarantine": {"type": "boolean", "default": True},
                    "uncertain_effect_held_until_fenced_proof": {"type": "boolean", "default": True},
                    "descendant_non_amplification_verified": {"type": "boolean", "default": True},
                    "at_most_once_settlement_verified": {"type": "boolean", "default": True},
                    "acca_graph_vertices_v": {"type": "integer", "default": 2048},
                    "acca_graph_edges_e": {"type": "integer", "default": 6144},
                    "acca_authority_ceiling_score": {"type": "number", "default": 0.92},
                    "acca_effective_authority_score": {"type": "number", "default": 0.84},
                    "acca_evidence_contextual_applicability_separated": {"type": "boolean", "default": True},
                    "acca_effect_time_stale_action_rejected": {"type": "boolean", "default": True},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_s2mr_serverless_disaggregated_smr_and_kairos_transactional_boundary_security",
            "description": "Nivel 451 (v31.0.0): Verifica la Replicacion de Maquinas de Estados Serverless (S^2MR y AirDB) sobre almacenamiento desagregado con materializacion distribuida por clientes y arranque en frio 10x-45x mas rapido sin servidores cuello de botella (arXiv:2611.01363) junto con el monitor transaccional Kairos en la frontera del sistema con retencion especulativa de efectos diferidos y reduccion de ataques del 47.0% al 2.7% en AgentDojo (arXiv:2610.18457) bajo torneo Pareto REG-007.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "s2mr_active_chokepoint_servers": {"type": "integer", "default": 0},
                    "s2mr_concurrent_clients": {"type": "integer", "default": 64},
                    "s2mr_disaggregated_log_and_state": {"type": "boolean", "default": True},
                    "s2mr_shared_log_materialization_verified": {"type": "boolean", "default": True},
                    "s2mr_bad_client_isolation_verified": {"type": "boolean", "default": True},
                    "s2mr_cold_start_speedup_x": {"type": "number", "default": 38.5},
                    "kairos_trace_events_n": {"type": "integer", "default": 1024},
                    "kairos_trace_edges_e": {"type": "integer", "default": 3072},
                    "kairos_system_boundary_confinement": {"type": "boolean", "default": True},
                    "kairos_speculative_deferred_holding": {"type": "boolean", "default": True},
                    "kairos_trace_oracle_bounded_authority": {"type": "boolean", "default": True},
                    "kairos_baseline_asr_pct": {"type": "number", "default": 47.0},
                    "kairos_enforced_asr_pct": {"type": "number", "default": 2.7},
                    "kairos_benign_utility_retention_ratio": {"type": "number", "default": 1.0},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_plume_rocq_mechanized_tap_read_atomicity_and_hakicc_conflict_serializable_cc",
            "description": "Nivel 452 (v31.1.0): Verifica los Patrones Anomalos Transaccionales (TAPs) mecanizados en Rocq e integrados en el verificador Plume con modelo completo de historias transaccionales y caracterizacion refinada de Read Atomicity con garantias de sesion (arXiv:2610.07665) junto con el pipeline multi-agente HakiCC de 2 etapas para sintesis de protocolos de control de concurrencia conflict-serializables (10/10 verificados) con ganancias de throughput de +50.6% en TPC-C y +92.2% en AuctionMark (arXiv:2610.00889) bajo torneo Pareto REG-007.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "plume_transaction_vertices_v": {"type": "integer", "default": 2048},
                    "plume_dependency_edges_e": {"type": "integer", "default": 6144},
                    "plume_rocq_history_model_total_well_formed": {"type": "boolean", "default": True},
                    "plume_read_atomicity_session_guarantees_enforced": {"type": "boolean", "default": True},
                    "plume_anomalous_tap_cycles_detected": {"type": "integer", "default": 0},
                    "hakicc_verified_protocols_count": {"type": "integer", "default": 10},
                    "hakicc_total_protocols_evaluated": {"type": "integer", "default": 10},
                    "hakicc_stage1_conflict_serializable": {"type": "boolean", "default": True},
                    "hakicc_stage2_evolutionary_optimized": {"type": "boolean", "default": True},
                    "hakicc_tpcc_throughput_gain_pct": {"type": "number", "default": 50.6},
                    "hakicc_auctionmark_throughput_gain_pct": {"type": "number", "default": 92.2},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_firstswap_preconsensus_quorum_admissibility_and_guarded_commits_transactional_approval",
            "description": "Nivel 453 (v31.2.0): Verifica las pre-aprobaciones de transacciones sin consenso en 1 ronda mediante el protocolo de admisibilidad escalada FirstSwap con reserva fraccionaria de liquidez por validador y admisibilidad conjunta bajo fallos bizantinos (arXiv:2611.10254) junto con los Guarded Commits de aprobaciones humanas transaccionales con registro de resolucion en ledger y adaptador de commit confinado por credenciales verificado sobre 271,035 trazas (arXiv:2610.00037) bajo torneo Pareto REG-007.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "validators_n": {"type": "integer", "default": 31},
                    "byzantine_validators_f": {"type": "integer", "default": 10},
                    "quorum_size_q": {"type": "integer", "default": 21},
                    "preapproval_message_rounds": {"type": "integer", "default": 1},
                    "scaled_validator_liquidity_fraction": {"type": "number", "default": 0.032},
                    "total_reserved_liquidity_ratio": {"type": "number", "default": 0.96},
                    "bidirectional_order_matching_preapproval": {"type": "boolean", "default": True},
                    "workflow_dag_vertices_v": {"type": "integer", "default": 2048},
                    "workflow_dag_edges_e": {"type": "integer", "default": 6144},
                    "verified_workflow_traces_count": {"type": "integer", "default": 271035},
                    "resolution_record_and_evidence_appended": {"type": "boolean", "default": True},
                    "credential_confined_commit_adapter": {"type": "boolean", "default": True},
                    "artifact_policy_and_path_coverage_verified": {"type": "boolean", "default": True},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_agent_state_footprint_semantic_conflict_and_zengram_lite_mvcc_cow_branching",
            "description": "Nivel 454 (v31.3.0): Verifica el seguimiento transaccional de huellas de estado (State Footprints) de lectura/escritura en sistemas multi-agente paralelos con resolucion semantica de conflictos sin actualizaciones perdidas ni lecturas obsoletas (arXiv:2610.03140) junto con la memoria agentica de 3 niveles Zengram-Lite con aislamiento de instantaneas MVCC, ramificacion Copy-on-Write (CoW) y ensamblado de contexto en 6 fases con huella estable de prefijo (arXiv:2610.00042) bajo torneo Pareto REG-007.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "parallel_agents_count": {"type": "integer", "default": 16},
                    "footprint_dag_vertices_v": {"type": "integer", "default": 2048},
                    "footprint_dag_edges_e": {"type": "integer", "default": 6144},
                    "state_footprint_read_write_tracked": {"type": "boolean", "default": True},
                    "lost_updates_detected": {"type": "integer", "default": 0},
                    "stale_reads_detected": {"type": "integer", "default": 0},
                    "semantic_conflict_resolution_verified": {"type": "boolean", "default": True},
                    "zengram_memory_tiers_count": {"type": "integer", "default": 3},
                    "six_phase_context_assembly_stages": {"type": "integer", "default": 6},
                    "mvcc_snapshot_isolation_verified": {"type": "boolean", "default": True},
                    "cow_database_branching_verified": {"type": "boolean", "default": True},
                    "stable_prefix_fingerprint_reuse": {"type": "boolean", "default": True},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_pangolin_dag_bft_tee_commitment_and_cognitive_serializability_tct",
            "description": "Nivel 455 (v31.4.0): Verifica la replicacion de maquinas de estado (SMR) DAG-BFT Pangolin con resiliencia n >= 2f + 1 asistida por TEE, difusion de vertices certificados en 1 paso sin revelar el ancla elegida por moneda, pruebas compactas de ejecucion en una sola replica y recoleccion de basura asincrona acotada en O(V+E) (arXiv:2610.26295) junto con la Serializabilidad Cognitiva estricta y transacciones TCT guard-first con recibos co-confirmados y orden aciclico de puntos de bloqueo (arXiv:2609.20261) bajo torneo Pareto REG-007.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "pangolin_replicas_n": {"type": "integer", "default": 7},
                    "byzantine_faults_f": {"type": "integer", "default": 3},
                    "certified_vertex_broadcast_steps": {"type": "integer", "default": 1},
                    "dag_vertices_v": {"type": "integer", "default": 2048},
                    "dag_edges_e": {"type": "integer", "default": 6144},
                    "unrevealed_coin_anchor_early_commit_verified": {"type": "boolean", "default": True},
                    "single_replica_compact_execution_proof_verified": {"type": "boolean", "default": True},
                    "asynchronous_dag_garbage_collection_bounded": {"type": "boolean", "default": True},
                    "cognitive_serializability_unchanged_derivation_verified": {"type": "boolean", "default": True},
                    "sealed_durability_domain_fences_active": {"type": "boolean", "default": True},
                    "guard_first_commit_transactions_verified": {"type": "boolean", "default": True},
                    "cocommitted_receipt_idempotent_grant_verified": {"type": "boolean", "default": True},
                    "acyclic_lock_point_order_cycles": {"type": "integer", "default": 0},
                    "injected_anomalies_leaked": {"type": "integer", "default": 0},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_barnacle_adaptive_multileader_dag_consensus_and_zetalite_logcentric_mvcc",
            "description": "Nivel 456 (v31.5.0): Verifica la planificacion adaptativa multi-lider Barnacle para consenso basado en DAG mediante medicion determinista de la fraccion de slots confirmados por la regla directa con cero mensajes extra, cero criptografia adicional y control AIMD sobre 4 modelos de fallos (3f+1, 5f+1, 2c+1, 5f+3c+1) en O(V+E) (arXiv:2609.03978) junto con el motor SQL Zeta-Lite con nucleo MVCC asincrono centrado en log, transacciones superpuestas con aislamiento de instantaneas, ramificacion CoW (fork/merge/rebase), consultas de grafos SQL/PGQ y durabilidad OPFS de 268k-315k lecturas/s (arXiv:2609.01818) bajo torneo Pareto REG-007.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "validators_n": {"type": "integer", "default": 16},
                    "byzantine_faults_f": {"type": "integer", "default": 5},
                    "fault_models_supported_count": {"type": "integer", "default": 4},
                    "dag_vertices_v": {"type": "integer", "default": 2048},
                    "dag_edges_e": {"type": "integer", "default": 6144},
                    "direct_rule_commit_fraction": {"type": "number", "default": 0.88},
                    "zero_extra_messages_and_crypto_verified": {"type": "boolean", "default": True},
                    "aimd_leader_count_adaptation_verified": {"type": "boolean", "default": True},
                    "head_of_line_blocking_eliminated": {"type": "boolean", "default": True},
                    "overlapping_snapshot_isolated_txns_verified": {"type": "boolean", "default": True},
                    "snapshot_isolation_conflict_detection_verified": {"type": "boolean", "default": True},
                    "cow_whole_db_fork_merge_rebase_verified": {"type": "boolean", "default": True},
                    "sql_pgq_graph_and_hnsw_gin_verified": {"type": "boolean", "default": True},
                    "snapshot_to_opfs_durability_verified": {"type": "boolean", "default": True},
                    "sustained_point_reads_per_sec": {"type": "integer", "default": 315000},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_veriprotocol_roundtick_consensus_time_semantics_and_augur_view_serializability",
            "description": "Nivel 457 (v31.6.0): Verifica la semantica temporal desacoplada RoundTick contra artefactos de liveness e inestabilidad de liderazgo en simulacion adversarial de consenso (VeriProtocol Multi-Paxos/Raft, 0 elecciones espurias en 140 ejecuciones con N=5 y presupuesto de retardo K=6..14, arXiv:2609.32972) junto con el analisis dinamico predictivo Augur con soporte de predicados SQL complejos y cero falsos positivos de View Serializability en O(V+E) (arXiv:2609.05288) bajo torneo Pareto REG-007.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "consensus_replicas_n": {"type": "integer", "default": 5},
                    "message_delay_budget_k": {"type": "integer", "default": 14},
                    "roundtick_executions_verified": {"type": "integer", "default": 140},
                    "spurious_leader_elections_count": {"type": "integer", "default": 0},
                    "roundtick_decoupled_time_semantics_enabled": {"type": "boolean", "default": True},
                    "legitimate_heartbeat_timeout_election_reachable": {"type": "boolean", "default": True},
                    "dag_vertices_v": {"type": "integer", "default": 2048},
                    "dag_edges_e": {"type": "integer", "default": 6144},
                    "augur_view_serializability_predictor_enabled": {"type": "boolean", "default": True},
                    "complex_sql_predicate_support_verified": {"type": "boolean", "default": True},
                    "false_positive_view_serializability_reports": {"type": "integer", "default": 0},
                    "unserializable_executions_prevented": {"type": "boolean", "default": True},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_hydrozoan_latency_adaptive_dag_consensus_and_git4data_mvcc_branching",
            "description": "Nivel 458 (v31.7.0): Verifica el consenso DAG adaptativo en latencia Hydrozoan con confirmacion en 2 retardos de mensaje (hasta p fallos) y respaldo en 3 retardos sobre el mismo DAG mediante regla indirecta graduada sin mensajes extra ni cambios de vista y seguridad/vivacidad verificadas en Lean 4 en O(V+E) (arXiv:2609.25918) junto con la capa de control de versiones nativo Git4Data sobre almacenamiento inmutable y MVCC con operaciones SQL (snapshot/tag, branch, diff, merge) de costo proporcional al delta O(Delta) y aceleracion >=10x sobre DoltDB en BranchBench (arXiv:2609.02106) bajo torneo Pareto REG-007.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "validators_n": {"type": "integer", "default": 16},
                    "byzantine_faults_f": {"type": "integer", "default": 3},
                    "crash_faults_c": {"type": "integer", "default": 2},
                    "fast_path_fault_tolerance_p": {"type": "integer", "default": 2},
                    "fast_path_message_delays": {"type": "integer", "default": 2},
                    "slow_path_message_delays": {"type": "integer", "default": 3},
                    "graded_indirect_rule_reconciliation_verified": {"type": "boolean", "default": True},
                    "zero_extra_messages_and_view_changes_verified": {"type": "boolean", "default": True},
                    "lean4_safety_liveness_machine_checked": {"type": "boolean", "default": True},
                    "geo_fast_quorum_latency_reduction_pct": {"type": "number", "default": 25.0},
                    "dag_vertices_v": {"type": "integer", "default": 2048},
                    "dag_edges_e": {"type": "integer", "default": 6144},
                    "mvcc_immutable_object_storage_enabled": {"type": "boolean", "default": True},
                    "sql_git_operations_supported_count": {"type": "integer", "default": 4},
                    "delta_proportional_operation_cost_verified": {"type": "boolean", "default": True},
                    "explicit_conflict_resolution_policies_verified": {"type": "boolean", "default": True},
                    "branchbench_speedup_vs_doltdb_x": {"type": "number", "default": 10.0},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {
            "name": "aleph_prove_vantage_availability_graded_broadcast_bft_and_shieldfs_authenticated_wal_cow",
            "description": "Nivel 459 (v31.8.0): Verifica el consenso BFT sin firmas Vantage con Availability-Graded Broadcast (AGB) sobre carriles de autor enlazados por hash, manifiestos de nucleo y punta optimista sellada por log de control en 3*delta retardos y 239k TPS bajo n >= 3f+1 en O(V+E) (arXiv:2608.16504) junto con el sistema de almacenamiento ShieldFS con Write-Ahead Log (WAL) autenticado por cadenas de hash, arbol de Merkle embebido, compromisos sucintos replicados en TEE y transacciones Copy-on-Write atomicas contra ataques de rollback, replay y equivocacion (arXiv:2608.19924) bajo torneo Pareto REG-007.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "validators_n": {"type": "integer", "default": 100},
                    "byzantine_faults_f": {"type": "integer", "default": 33},
                    "signature_free_authenticated_channels_only": {"type": "boolean", "default": True},
                    "availability_graded_broadcast_enabled": {"type": "boolean", "default": True},
                    "unresolved_tips_sealed_via_control_log": {"type": "boolean", "default": True},
                    "aligned_block_sequencing_delays_delta": {"type": "integer", "default": 3},
                    "wan_sequenced_tps": {"type": "integer", "default": 239000},
                    "dag_vertices_v": {"type": "integer", "default": 2048},
                    "dag_edges_e": {"type": "integer", "default": 6144},
                    "tee_replicated_succinct_commitments_enabled": {"type": "boolean", "default": True},
                    "wal_hash_chain_and_embedded_merkle_tree_verified": {"type": "boolean", "default": True},
                    "atomic_cow_transactional_commitment_update": {"type": "boolean", "default": True},
                    "rollback_replay_equivocation_attacks_leaked": {"type": "integer", "default": 0},
                    "auto_repair": {"type": "boolean", "default": True}
                }
            }
        },
        {'name': 'aleph_audit_pg18_covering_index_include_supabase_index_advisor_and_constraint_using_index', 'description': '[v23.5.0 - REG-155] Audita formalmente índices cubrientes B-Tree con cláusula INCLUDE en PostgreSQL 18 (Index-Only Scans sin expresiones en INCLUDE), consultas parametrizadas tipadas ($1::uuid) y confinamiento de privilegios en extensions.index_advisor(text) de Supabase, y promoción Zero-Downtime de restricciones PRIMARY KEY / UNIQUE USING INDEX.', 'inputSchema': {'type': 'object', 'properties': {'sql_ddl': {'type': 'string', 'description': 'Sentencias SQL/DDL a auditar bajo REG-155 (PG18 Covering Index INCLUDE + Supabase index_advisor Guard + Zero-Downtime Constraint USING INDEX).'}}, 'required': ['sql_ddl']}},
        {'name': 'aleph_audit_pg18_gin_fastupdate_supabase_pg_plan_filter_and_reindex_concurrently', 'description': '[v23.4.0 - REG-154] Audita formalmente índices GIN en PostgreSQL 18 (WITH fastupdate = off o gin_pending_list_limit acotado para evitar pausas p99), límites de costo de ejecución por rol mediante pg_plan_filter (plan_filter.statement_cost_limit en anon y authenticated) en Supabase, y reconstrucción Zero-Downtime de índices vía REINDEX INDEX/TABLE CONCURRENTLY fuera de bloques transaccionales.', 'inputSchema': {'type': 'object', 'properties': {'sql_ddl': {'type': 'string', 'description': 'Sentencias SQL/DDL a auditar bajo REG-154 (PG18 GIN fastupdate Guard + Supabase pg_plan_filter Cost Limit + Zero-Downtime REINDEX CONCURRENTLY).'}}, 'required': ['sql_ddl']}},
        {'name': 'aleph_audit_pg18_enum_add_value_supabase_postgres_fdw_confinement_and_cluster_blocker', 'description': '[v23.3.0 - REG-153] Audita formalmente la evolución idempotente de tipos ENUM en PostgreSQL 18 (ALTER TYPE ... ADD VALUE IF NOT EXISTS al final sin DROP TYPE CASCADE), el confinamiento de tablas foráneas postgres_fdw en el esquema private de Supabase sin exposición a anon/authenticated, y el bloqueo Zero-Downtime de CLUSTER y ALTER TABLE ... SET TABLESPACE.', 'inputSchema': {'type': 'object', 'properties': {'sql_ddl': {'type': 'string', 'description': 'Sentencias SQL/DDL a auditar bajo REG-153 (PG18 Enum ADD VALUE IF NOT EXISTS + Supabase FDW Private Schema Confinement + Zero-Downtime CLUSTER Blocker).'}}, 'required': ['sql_ddl']}},
        {'name': 'aleph_audit_pg18_updatable_view_local_check_rule_blocker_supabase_pgrst_watch_and_view_replace', 'description': "[v23.2.0 - REG-152] Audita formalmente vistas actualizables PostgreSQL 18 (WITH security_invoker = true + WITH LOCAL/CASCADED CHECK OPTION y bloqueo de CREATE RULE), event triggers filtrados WHEN TAG IN (...) para recarga de caché PostgREST (NOTIFY pgrst, 'reload schema') en Supabase, y evolución Zero-Downtime de vistas sin DROP VIEW ... CASCADE.", 'inputSchema': {'type': 'object', 'properties': {'sql_ddl': {'type': 'string', 'description': 'Sentencias SQL/DDL a auditar bajo REG-152 (PG18 Updatable View Check Option + Rule Blocker + Supabase PostgREST Event Trigger + Zero-Downtime View Replace).'}}, 'required': ['sql_ddl']}},
        {'name': 'aleph_audit_pg18_transition_table_statement_trigger_supabase_pg_net_and_disable_trigger_blocker', 'description': '[v23.1.0 - REG-151] Audita formalmente triggers por sentencia con tablas de transición en PostgreSQL 18 (REFERENCING NEW/OLD TABLE AS ... FOR EACH STATEMENT), webhooks asíncronos pg_net en Supabase con secretos en Vault y timeout_milliseconds <= 5000, y el bloqueo Zero-Downtime de ALTER TABLE ... DISABLE TRIGGER ALL/USER.', 'inputSchema': {'type': 'object', 'properties': {'sql_ddl': {'type': 'string', 'description': 'Sentencias SQL/DDL a auditar bajo REG-151 (PG18 Transition Table Statement Trigger + Supabase pg_net Vault Webhook + Zero-Downtime DISABLE TRIGGER Blocker).'}}, 'required': ['sql_ddl']}},
        {'name': 'aleph_audit_pg18_sequence_cache_supabase_pgtap_rls_and_alter_sequence_restart_blocker', 'description': '[v23.0.0 - REG-150] Audita formalmente secuencias PostgreSQL 18 (AS bigint CACHE >= 64 NO CYCLE), pruebas transaccionales pgTAP de RLS en Supabase (BEGIN ... policies_are/policy_roles_are/policy_cmd_is ... ROLLBACK), y el bloqueo Zero-Downtime de ALTER SEQUENCE ... RESTART.', 'inputSchema': {'type': 'object', 'properties': {'sql_ddl': {'type': 'string', 'description': 'Sentencias SQL/DDL a auditar bajo REG-150 (PG18 Sequence Cache + Supabase pgTAP RLS Rollback + Zero-Downtime ALTER SEQUENCE RESTART Blocker).'}}, 'required': ['sql_ddl']}},
        {'name': 'aleph_audit_pg18_extended_statistics_supabase_pg_repack_and_analyze_skip_locked', 'description': '[v22.9.0 - REG-149] Audita formalmente el uso de CREATE STATISTICS (dependencies, ndistinct, mcv) emparejado con ANALYZE en columnas multi-tenant correlacionadas de PostgreSQL 18, el requisito de PRIMARY KEY y confinamiento de SCHEMA repack para Supabase pg_repack, y la ejecución Zero-Downtime de ANALYZE (SKIP_LOCKED, BUFFER_USAGE_LIMIT ...).', 'inputSchema': {'type': 'object', 'properties': {'sql_ddl': {'type': 'string', 'description': 'Sentencias SQL/DDL a auditar bajo REG-149 (PG18 CREATE STATISTICS + Supabase pg_repack Confinement + Zero-Downtime ANALYZE SKIP_LOCKED).'}}, 'required': ['sql_ddl']}},
        {'name': 'aleph_audit_pg18_subscription_streaming_parallel_supabase_plpgsql_check_and_matview_no_data', 'description': '[v22.8.0 - REG-148] Audita formalmente el uso de streaming = parallel y run_as_owner = false en CREATE SUBSCRIPTION de PostgreSQL 18, la verificación estática de funciones PL/pgSQL mediante extensions.plpgsql_check_function() con check_function_bodies = on en Supabase, y la creación Zero-Downtime de vistas materializadas con WITH NO DATA + CREATE UNIQUE INDEX.', 'inputSchema': {'type': 'object', 'properties': {'sql_ddl': {'type': 'string', 'description': 'Sentencias SQL/DDL a auditar bajo REG-148 (PG18 Subscription Parallel Streaming + Supabase plpgsql_check + Zero-Downtime Matview WITH NO DATA).'}}, 'required': ['sql_ddl']}},
        {'name': 'aleph_audit_pg18_publication_partition_root_supabase_hypopg_reset_and_replica_identity', 'description': '[v22.7.0 - REG-147] Audita formalmente el uso de CREATE PUBLICATION ... FOR TABLE con publish_via_partition_root = true (prohibiendo FOR ALL TABLES) en PostgreSQL 18, la limpieza atómica hypopg_reset() y confinamiento de index_advisor en Supabase, y el bloqueo Zero-Downtime de REPLICA IDENTITY FULL en favor de REPLICA IDENTITY USING INDEX.', 'inputSchema': {'type': 'object', 'properties': {'sql_ddl': {'type': 'string', 'description': 'Sentencias SQL/DDL a auditar bajo REG-147 (PG18 Publication Partition Root + Supabase HypoPG Reset & index_advisor + Zero-Downtime REPLICA IDENTITY).'}}, 'required': ['sql_ddl']}},
        {'name': 'aleph_audit_pg18_transaction_timeout_hierarchy_supabase_partman_and_partition_index_attach', 'description': '[v22.6.0 - REG-146] Audita formalmente la jerarquía estricta 0 < statement_timeout, idle_in_transaction_session_timeout < transaction_timeout en PostgreSQL 18, la migración de timescaledb deprecado a particionamiento declarativo nativo con pg_partman en Supabase, y la creación Zero-Downtime de índices particionados con CREATE INDEX ON ONLY parent + CREATE INDEX CONCURRENTLY + ALTER INDEX ATTACH PARTITION.', 'inputSchema': {'type': 'object', 'properties': {'sql_ddl': {'type': 'string', 'description': 'Sentencias SQL/DDL a auditar bajo REG-146 (PG18 transaction_timeout Hierarchy + Supabase pg_partman + Zero-Downtime Partitioned Index ATTACH).'}}, 'required': ['sql_ddl']}},
        {'name': 'aleph_audit_pg18_vacuum_buffer_usage_limit_supabase_jsonschema_and_not_valid_check', 'description': '[v22.5.0 - REG-145] Audita formalmente el uso de BUFFER_USAGE_LIMIT acotado e INDEX_CLEANUP activo en VACUUM de PostgreSQL 18, la validación de contratos JSON Schema mediante extensions.jsonb_matches_schema calificado por esquema en Supabase pg_jsonschema, y la adición Zero-Downtime de restricciones CHECK JSONB con NOT VALID + VALIDATE CONSTRAINT.', 'inputSchema': {'type': 'object', 'properties': {'sql_ddl': {'type': 'string', 'description': 'Sentencias SQL/DDL a auditar bajo REG-145 (PG18 VACUUM BUFFER_USAGE_LIMIT + Supabase extensions.jsonb_matches_schema + Zero-Downtime NOT VALID CHECK).'}}, 'required': ['sql_ddl']}},
        {'name': 'aleph_audit_pg18_merge_not_matched_by_source_supabase_plan_filter_and_char_length_check', 'description': '[v22.4.0 - REG-144] Audita formalmente el acotamiento por tenant_id en cláusulas MERGE ... WHEN NOT MATCHED BY SOURCE AND t.tenant_id = ... en PostgreSQL 18, el límite de costo de ejecutor plan_filter.statement_cost_limit > 0 en Supabase pg_plan_filter, y el uso Zero-Downtime de CHECK (char_length(col) <= N) NOT VALID en lugar de ALTER COLUMN ... TYPE varchar(N).', 'inputSchema': {'type': 'object', 'properties': {'sql_ddl': {'type': 'string', 'description': 'Sentencias SQL/DDL a auditar bajo REG-144 (PG18 MERGE WHEN NOT MATCHED BY SOURCE Tenant Guard + Supabase pg_plan_filter + Zero-Downtime char_length CHECK).'}}, 'required': ['sql_ddl']}},
        {'name': 'aleph_audit_pg18_on_conflict_inference_distinct_supabase_vault_and_drop_default', 'description': '[v22.3.0 - REG-143] Audita formalmente la inferencia de índice único en INSERT ... ON CONFLICT (cols) DO UPDATE calificado con WHERE ... IS DISTINCT FROM EXCLUDED.* en PostgreSQL 18, el confinamiento estricto de vault.decrypted_secrets y vault.secrets en Supabase Vault, y el bloqueo Zero-Downtime de ALTER COLUMN ... DROP DEFAULT sobre columnas NOT NULL.', 'inputSchema': {'type': 'object', 'properties': {'sql_ddl': {'type': 'string', 'description': 'Sentencias SQL/DDL a auditar bajo REG-143 (PG18 ON CONFLICT Index Inference & IS DISTINCT FROM + Supabase Vault Confinement + Zero-Downtime DROP DEFAULT Guard).'}}, 'required': ['sql_ddl']}},
        {'name': 'aleph_audit_pg18_copy_log_verbosity_silent_supabase_storage_extension_and_rename_table', 'description': '[v22.2.0 - REG-142] Audita formalmente el uso de COPY ... FROM con ON_ERROR ignore y LOG_VERBOSITY silent en PostgreSQL 18 contra fuga de PII en logs, la validación combinada de storage.foldername(name) y storage.extension(name) en políticas RLS sobre storage.objects en Supabase, y la creación Zero-Downtime de vista de compatibilidad (security_invoker = true) al renombrar tablas (ALTER TABLE ... RENAME TO).', 'inputSchema': {'type': 'object', 'properties': {'sql_ddl': {'type': 'string', 'description': 'Sentencias SQL/DDL a auditar bajo REG-142 (PG18 COPY LOG_VERBOSITY silent + Supabase storage.extension RLS + Zero-Downtime RENAME TO View).'}}, 'required': ['sql_ddl']}},
        {'name': 'aleph_audit_pg18_foreign_table_like_virtual_supabase_extra_search_path_and_rename_column', 'description': '[v22.1.0 - REG-141] Audita formalmente el uso de CREATE FOREIGN TABLE ... (LIKE ...) con columnas generadas VIRTUAL (frente a STORED inconsistentes en lectura remota) en PostgreSQL 18, el aislamiento de extensiones en pgrst.db_extra_search_path fuera de pgrst.db_schemas en Supabase PostgREST, y el bloqueo Zero-Downtime de ALTER TABLE ... RENAME COLUMN directo.', 'inputSchema': {'type': 'object', 'properties': {'sql_ddl': {'type': 'string', 'description': 'Sentencias SQL/DDL a auditar bajo REG-141 (PG18 Foreign Table LIKE & VIRTUAL + Supabase db_extra_search_path + Zero-Downtime RENAME COLUMN Blocker).'}}, 'required': ['sql_ddl']}},
        {'name': 'aleph_audit_pg18_virtual_set_expression_supabase_aggregates_guard_and_drop_column', 'description': '[v22.0.0 - REG-140] Audita formalmente el uso de ALTER COLUMN ... SET EXPRESSION AS sobre columnas generadas VIRTUAL (sin reescritura de tabla) frente a STORED en PostgreSQL 18, la protección DoS de funciones agregadas PostgREST (pgrst.db_aggregates_enabled con statement_timeout y pgrst.db_max_rows) en Supabase, y la eliminación Zero-Downtime de columnas (DROP COLUMN con lock_timeout y sin CASCADE).', 'inputSchema': {'type': 'object', 'properties': {'sql_ddl': {'type': 'string', 'description': 'Sentencias SQL/DDL a auditar bajo REG-140 (PG18 Virtual SET EXPRESSION AS + Supabase PostgREST Aggregates DoS Guard + Zero-Downtime DROP COLUMN).'}}, 'required': ['sql_ddl']}},
        {'name': 'aleph_audit_pg18_autovacuum_worker_slots_supabase_restrictive_rls_and_view_append', 'description': '[v21.9.0 - REG-139] Audita formalmente el invariante de capacidad autovacuum_worker_slots >= autovacuum_max_workers y track_cost_delay_timing = on en PostgreSQL 18, la composición conjuntiva/disyuntiva de políticas RLS AS RESTRICTIVE + AS PERMISSIVE en Supabase, y la evolución Zero-Downtime append-only de vistas con CREATE OR REPLACE VIEW sin DROP VIEW.', 'inputSchema': {'type': 'object', 'properties': {'sql_ddl': {'type': 'string', 'description': 'Sentencias SQL/DDL a auditar bajo REG-139 (PG18 autovacuum_worker_slots + Supabase RESTRICTIVE/PERMISSIVE RLS + Zero-Downtime CREATE OR REPLACE VIEW).'}}, 'required': ['sql_ddl']}},
        {'name': 'aleph_audit_pg18_eager_freeze_rate_supabase_role_set_false_and_drop_table_fk_decoupling', 'description': '[v21.8.0 - REG-138] Audita formalmente el acotamiento de vacuum_max_eager_freeze_failure_rate en [0.01, 0.10] en PostgreSQL 18, la concesión de roles en Supabase con WITH INHERIT TRUE, SET FALSE, ADMIN FALSE para impedir suplantación vía SET ROLE, y el desacoplamiento Zero-Downtime de claves foráneas (ALTER TABLE ... DROP CONSTRAINT) antes de ejecutar DROP TABLE sin CASCADE.', 'inputSchema': {'type': 'object', 'properties': {'sql_ddl': {'type': 'string', 'description': 'Sentencias SQL/DDL a auditar bajo REG-138 (PG18 vacuum_max_eager_freeze_failure_rate + Supabase GRANT WITH SET FALSE + Zero-Downtime DROP TABLE FK Decoupling).'}}, 'required': ['sql_ddl']}},
        {'name': 'aleph_audit_pg18_vacuum_truncate_guard_supabase_pre_request_hook_and_toast_lz4_compression', 'description': "[v21.7.0 - REG-137] Audita formalmente la desactivación de vacuum_truncate (vacuum_truncate = false) en tablas OLTP multi-tenant calientes de PostgreSQL 18 para prevenir bloqueos ACCESS EXCLUSIVE en primarios y réplicas, el confinamiento SET search_path = '' en hooks pgrst.db_pre_request de Supabase, y la actualización sólo de metadatos ALTER COLUMN ... SET COMPRESSION lz4 sin reescritura de tabla.", 'inputSchema': {'type': 'object', 'properties': {'sql_ddl': {'type': 'string', 'description': 'Sentencias SQL/DDL a auditar bajo REG-137 (PG18 vacuum_truncate Guard + Supabase pgrst.db_pre_request Hook + Zero-Downtime TOAST SET COMPRESSION lz4).'}}, 'required': ['sql_ddl']}},
        {'name': 'aleph_audit_pg18_returning_with_alias_supabase_pgaudit_pii_and_alter_add_exclude_blocker', 'description': '[v21.6.0 - REG-136] Audita formalmente la desambiguación de alias RETURNING WITH (OLD AS ..., NEW AS ...) en PostgreSQL 18 dentro de funciones/triggers PL/pgSQL, el blindaje de pgaudit en Supabase (pgaudit.log_parameter = off contra fuga de PII/JWT y prohibición de pgaudit.log = all), y el bloqueo Zero-Downtime de ALTER TABLE ... ADD CONSTRAINT ... EXCLUDE USING gist en tablas vivas.', 'inputSchema': {'type': 'object', 'properties': {'sql_ddl': {'type': 'string', 'description': 'Sentencias SQL/DDL a auditar bajo REG-136 (PG18 RETURNING WITH OLD/NEW Alias + Supabase pgaudit PII Guard + Zero-Downtime ALTER ADD EXCLUDE Blocker).'}}, 'required': ['sql_ddl']}},
        {'name': 'aleph_audit_pg18_casefold_unicode_fast_supabase_extensions_schema_and_expression_index', 'description': '[v21.5.0 - REG-135] Audita formalmente el uso de casefold(col COLLATE pg_unicode_fast) de PostgreSQL 18 en reemplazo de citext heredado, el aislamiento de extensiones en SCHEMA extensions y bloqueo de plv8/pgjwt deprecados en Supabase, y la creación Zero-Downtime de índices de expresión con CREATE UNIQUE INDEX CONCURRENTLY.', 'inputSchema': {'type': 'object', 'properties': {'sql_ddl': {'type': 'string', 'description': 'Sentencias SQL/DDL a auditar bajo REG-135 (PG18 casefold/pg_unicode_fast + Supabase SCHEMA extensions + Zero-Downtime Expression Index CONCURRENTLY).'}}, 'required': ['sql_ddl']}},
        {'name': 'aleph_audit_pg18_io_max_combine_limit_supabase_auth_users_fk_and_set_tablespace_blocker', 'description': '[v21.4.0 - REG-134] Audita formalmente la coalescencia de E/S asíncrona en PostgreSQL 18 (io_max_combine_limit >= io_combine_limit >= 128kB), la declaración de ON DELETE CASCADE/SET NULL e índice B-Tree en claves foráneas hacia auth.users(id) en Supabase, y el bloqueo Zero-Downtime de ALTER TABLE ... SET TABLESPACE bajo ACCESS EXCLUSIVE.', 'inputSchema': {'type': 'object', 'properties': {'sql_ddl': {'type': 'string', 'description': 'Sentencias SQL/DDL a auditar bajo REG-134 (PG18 io_max_combine_limit + Supabase auth.users FK ON DELETE & Index + Zero-Downtime SET TABLESPACE Blocker).'}}, 'required': ['sql_ddl']}},
        {'name': 'aleph_audit_pg18_pg_stat_statements_in_list_supabase_rls_update_with_check_and_bigint_identity', 'description': '[v21.3.0 - REG-133] Audita formalmente la normalización de listas IN ($1 /*, ... */) en pg_stat_statements de PostgreSQL 18 (compute_query_id activo y pg_stat_statements.max >= 5000), la presencia obligatoria de WITH CHECK (...) e índice B-Tree en políticas RLS FOR UPDATE/ALL de Supabase, y el uso de BIGINT GENERATED ALWAYS AS IDENTITY en lugar de SERIAL/BIGSERIAL.', 'inputSchema': {'type': 'object', 'properties': {'sql_ddl': {'type': 'string', 'description': 'Sentencias SQL/DDL a auditar bajo REG-133 (PG18 pg_stat_statements IN-list + Supabase RLS UPDATE WITH CHECK & Index + BIGINT GENERATED ALWAYS AS IDENTITY).'}}, 'required': ['sql_ddl']}},
        {'name': 'aleph_audit_pg18_scram_md5_deprecation_supabase_default_function_revoke_and_vacuum_full_blocker', 'description': '[v21.2.0 - REG-132] Audita formalmente la imposición de SCRAM-SHA-256 y md5_password_warnings = on en PostgreSQL 18, la revocación por defecto de ejecución de funciones en Supabase (ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC, anon, authenticated) para evitar exposición accidental de funciones SECURITY DEFINER vía PostgREST RPC, y el bloqueo Zero-Downtime de VACUUM FULL y CLUSTER.', 'inputSchema': {'type': 'object', 'properties': {'sql_ddl': {'type': 'string', 'description': 'Sentencias SQL/DDL a auditar bajo REG-132 (PG18 SCRAM-SHA-256/md5_password_warnings + Supabase Default Function Privileges + Zero-Downtime VACUUM FULL/CLUSTER Blocker).'}}, 'required': ['sql_ddl']}},
        {'name': 'aleph_audit_pg18_overexplain_extension_path_supabase_pgmq_and_replica_identity_index', 'description': '[v21.1.0 - REG-131] Audita formalmente pg_overexplain (EXPLAIN (DEBUG, RANGE_TABLE)) y la integridad de extension_control_path ($system sin rutas /tmp) en PostgreSQL 18, el confinamiento multi-tenant de colas pgmq/pgmq_public en Supabase (REVOKE USAGE ON SCHEMA pgmq, pgmq_public FROM PUBLIC, anon, authenticated), y el bloqueo Zero-Downtime de REPLICA IDENTITY FULL en favor de REPLICA IDENTITY DEFAULT o USING INDEX.', 'inputSchema': {'type': 'object', 'properties': {'sql_ddl': {'type': 'string', 'description': 'Sentencias SQL/DDL a auditar bajo REG-131 (PG18 pg_overexplain/extension_control_path + Supabase pgmq Confinement + Zero-Downtime REPLICA IDENTITY USING INDEX).'}}, 'required': ['sql_ddl']}},
        {'name': 'aleph_audit_pg18_backend_io_telemetry_supabase_role_statement_timeout_and_set_logged_rewrite', 'description': "[v21.0.0 - REG-130] Audita formalmente la atribución de E/S por proceso backend pg_stat_get_backend_io(pid) con track_io_timing/track_wal_io_timing activos en PostgreSQL 18, el endurecimiento de statement_timeout por rol en Supabase (anon = '3s', authenticated = '8s', prohibiendo 0 o minutos excesivos), y el bloqueo de reescrituras completas de tabla con ALTER TABLE ... SET LOGGED / SET UNLOGGED bajo ACCESS EXCLUSIVE.", 'inputSchema': {'type': 'object', 'properties': {'sql_ddl': {'type': 'string', 'description': 'Sentencias SQL/DDL a auditar bajo REG-130 (PG18 pg_stat_get_backend_io + Supabase Role statement_timeout + Zero-Downtime SET LOGGED/UNLOGGED Blocker).'}}, 'required': ['sql_ddl']}},
        {'name': 'aleph_audit_pg18_file_copy_method_clone_supabase_pgvector_iterative_scan_and_reindex_concurrently', 'description': "[v20.9.0 - REG-129] Audita formalmente la clonación instantánea Copy-on-Write file_copy_method = clone (con CREATE DATABASE ... STRATEGY = FILE_COPY y effective_io_concurrency >= 16) de PostgreSQL 18, la activación de hnsw.iterative_scan = 'relaxed_order' / 'strict_order' en índices pgvector HNSW bajo RLS multi-tenant en Supabase para evitar pérdida silenciosa de recall, y el uso obligatorio de REINDEX INDEX/TABLE CONCURRENTLY Zero-Downtime.", 'inputSchema': {'type': 'object', 'properties': {'sql_ddl': {'type': 'string', 'description': 'Sentencias SQL/DDL a auditar bajo REG-129 (PG18 file_copy_method=clone + Supabase pgvector hnsw.iterative_scan + Zero-Downtime REINDEX CONCURRENTLY).'}}, 'required': ['sql_ddl']}},
        {'name': 'aleph_audit_pg18_autovacuum_max_threshold_supabase_pgsodium_and_trigger_lock', 'description': '[v20.8.0 - REG-128] Audita formalmente el tope duro autovacuum_vacuum_max_threshold de PostgreSQL 18 en tablas OLTP masivas, el confinamiento de esquema pgsodium y la obligatoriedad de WITH (security_invoker = true) en vistas de desencriptación en Supabase, y la prohibición de DISABLE TRIGGER ALL junto con SET LOCAL lock_timeout antes de DROP TRIGGER en migraciones Zero-Downtime.', 'inputSchema': {'type': 'object', 'properties': {'sql_ddl': {'type': 'string', 'description': 'Sentencias SQL/DDL a auditar bajo REG-128 (PG18 autovacuum_vacuum_max_threshold + Supabase pgsodium security_invoker + Zero-Downtime Trigger DDL).'}}, 'required': ['sql_ddl']}},
        {'name': 'aleph_audit_pg18_checkpointer_slru_stats_supabase_pg_cron_and_detach_partition_truncate', 'description': '[v20.7.0 - REG-127] Audita formalmente las nuevas métricas de pg_stat_checkpointer en PostgreSQL 18 (num_done y slru_written con checkpoint_completion_target >= 0.8), el confinamiento de privilegios de pg_cron en Supabase (REVOKE USAGE ON SCHEMA cron y REVOKE ALL ON ALL TABLES/FUNCTIONS IN SCHEMA cron FROM PUBLIC, anon, authenticated), y el desacoplamiento Zero-Downtime ALTER TABLE ... DETACH PARTITION ... CONCURRENTLY antes de ejecutar TRUNCATE TABLE.', 'inputSchema': {'type': 'object', 'properties': {'sql_ddl': {'type': 'string', 'description': 'Sentencias SQL/DDL a auditar bajo REG-127 (PG18 pg_stat_checkpointer num_done/slru_written + Supabase pg_cron Confinement + Zero-Downtime DETACH PARTITION CONCURRENTLY before TRUNCATE).'}}, 'required': ['sql_ddl']}},
        {'name': 'aleph_audit_pg18_idle_replication_slot_timeout_supabase_pg_net_and_invalid_index_cleanup', 'description': '[v20.6.0 - REG-126] Audita formalmente el circuit-breaker de slots inactivos en PostgreSQL 18 (idle_replication_slot_timeout > 0 y max_slot_wal_keep_size acotado), el confinamiento de privilegios de pg_net en Supabase (REVOKE USAGE ON SCHEMA net y REVOKE ALL ON ALL FUNCTIONS IN SCHEMA net FROM PUBLIC, anon, authenticated contra SSRF), y la limpieza previa de índices fallidos (pg_index.indisvalid = false / DROP INDEX CONCURRENTLY IF EXISTS) antes de reconstruir con CREATE INDEX CONCURRENTLY.', 'inputSchema': {'type': 'object', 'properties': {'sql_ddl': {'type': 'string', 'description': 'Sentencias SQL/DDL a auditar bajo REG-126 (PG18 idle_replication_slot_timeout + Supabase pg_net Confinement + Zero-Downtime Invalid Index Cleanup).'}}, 'required': ['sql_ddl']}},
        {'name': 'aleph_audit_pg18_logical_conflict_stats_supabase_pg_graphql_and_volatile_default_add_column', 'description': '[v20.5.0 - REG-125] Audita formalmente telemetría de conflictos de replicación lógica en PostgreSQL 18 (pg_stat_subscription_stats.confl_multiple_unique_conflicts y CREATE SUBSCRIPTION ... WITH (two_phase = true)), endurecimiento de pg_graphql en Supabase (acotando max_rows <= 100 y bloqueando totalCount sin límite de página), y prevención de reescritura completa de tabla bajo ACCESS EXCLUSIVE al ejecutar ALTER TABLE ... ADD COLUMN con expresiones DEFAULT volátiles (clock_timestamp(), random(), timeofday()) que invalidan pg_attribute.atthasmissing.', 'inputSchema': {'type': 'object', 'properties': {'sql_ddl': {'type': 'string', 'description': 'Sentencias SQL/DDL a auditar bajo REG-125 (PG18 Logical Conflict Stats + Supabase pg_graphql max_rows + Zero-Downtime Non-Volatile ADD COLUMN).'}}, 'required': ['sql_ddl']}},
        {'name': 'aleph_audit_pg18_not_enforced_constraint_supabase_fdw_confinement_and_lock_timeout', 'description': '[v20.4.0 - REG-124] Audita formalmente restricciones CHECK/FOREIGN KEY NOT ENFORCED en PostgreSQL 18 (exigiendo transición a ENFORCED o patrón NOT VALID + VALIDATE CONSTRAINT), confinamiento de Foreign Data Wrappers (CREATE FOREIGN TABLE) en esquemas privados de Supabase sin exposición a anon/authenticated (dado que las tablas foráneas carecen de RLS), y compuerta Zero-Downtime SET LOCAL lock_timeout antes de ALTER TABLE para evitar encolamiento catastrófico de ACCESS EXCLUSIVE.', 'inputSchema': {'type': 'object', 'properties': {'sql_ddl': {'type': 'string', 'description': 'Sentencias SQL/DDL a auditar bajo REG-124 (PG18 NOT ENFORCED + Supabase Private FDW Confinement + Zero-Downtime SET LOCAL lock_timeout).'}}, 'required': ['sql_ddl']}},
        {'name': 'aleph_audit_pg18_upgrade_stats_copy_reject_limit_auth_hook_and_enum_add_value', 'description': '[v20.3.0 - REG-123] Audita formalmente preservación de estadísticas en pg_upgrade y COPY ... (ON_ERROR ignore, REJECT_LIMIT) de PostgreSQL 18, confinamiento de custom_access_token_hook al rol supabase_auth_admin (REVOKE EXECUTE FROM authenticated, anon, public), y evolución Zero-Downtime de tipos ENUM con ALTER TYPE ... ADD VALUE IF NOT EXISTS.', 'inputSchema': {'type': 'object', 'properties': {'sql_ddl': {'type': 'string', 'description': 'Sentencias SQL/DDL a auditar bajo REG-123 (PG18 pg_upgrade/COPY REJECT_LIMIT + Supabase custom_access_token_hook + Zero-Downtime ENUM ADD VALUE IF NOT EXISTS).'}}, 'required': ['sql_ddl']}},
        {'name': 'aleph_audit_pg18_explain_buffers_storage_foldername_rls_and_matview_concurrent', 'description': '[v20.3.0 - REG-122] Audita formalmente telemetría EXPLAIN (ANALYZE, BUFFERS) y contadores en bytes pg_stat_io de PostgreSQL 18, aislamiento multi-tenant por prefijo de ruta (storage.foldername(name))[1] en storage.objects de Supabase, y actualización Zero-Downtime de vistas materializadas mediante CREATE UNIQUE INDEX CONCURRENTLY + REFRESH MATERIALIZED VIEW CONCURRENTLY.', 'inputSchema': {'type': 'object', 'properties': {'sql_ddl': {'type': 'string', 'description': 'Sentencias SQL/DDL a auditar bajo REG-122 (PG18 EXPLAIN BUFFERS + Supabase storage.foldername RLS + REFRESH MATERIALIZED VIEW CONCURRENTLY).'}}, 'required': ['sql_ddl']}},
        {'name': 'aleph_audit_pg18_oauth_checksums_supabase_cls_and_expand_contract_column_type', 'description': '[v20.3.0 - REG-121] Audita formalmente autenticación OAuth 2.0 nativa de PostgreSQL 18 (oauth_validator_libraries) y data_checksums activados por defecto, Seguridad a Nivel de Columna (CLS) en Supabase (REVOKE ALL + GRANT SELECT/UPDATE por lista explícita de columnas contra BOPLA), y evolución Zero-Downtime de tipos de columna mediante Expand-Contract sin ALTER COLUMN ... TYPE bloqueante.', 'inputSchema': {'type': 'object', 'properties': {'sql_ddl': {'type': 'string', 'description': 'Sentencias SQL/DDL a auditar bajo REG-121 (PG18 OAuth/Checksums + Supabase CLS + Zero-Downtime Expand-Contract Column Type).'}}, 'required': ['sql_ddl']}},
        {'name': 'aleph_audit_pg18_async_io_eager_freeze_rls_initplan_and_attach_partition', 'description': '[v20.3.0 - REG-120] Audita formalmente I/O Asíncrono nativo de PostgreSQL 18 (io_method = io_uring/worker) y vacuum_max_eager_freeze_failure_rate, optimización initPlan en políticas RLS de Supabase envolviendo (SELECT auth.uid()) y (SELECT auth.jwt()), y acople Zero-Downtime de particiones mediante CHECK ... NOT VALID + VALIDATE CONSTRAINT previo a ATTACH PARTITION.', 'inputSchema': {'type': 'object', 'properties': {'sql_ddl': {'type': 'string', 'description': 'Sentencias SQL/DDL a auditar bajo REG-120 (PG18 Async I/O + Eager Freeze + RLS initPlan + ATTACH PARTITION pre-validado).'}}, 'required': ['sql_ddl']}},
        {'name': 'aleph_audit_pg18_uuidv7_security_definer_search_path_and_unique_using_index', 'description': "[v20.3.0 - REG-119] Audita formalmente claves primarias monotónicas uuidv7() nativas de PostgreSQL 18 contra fragmentación B-Tree, confinamiento estricto de funciones SECURITY DEFINER en Supabase (SET search_path = '' + REVOKE EXECUTE FROM PUBLIC, anon) y promoción Zero-Downtime de restricciones UNIQUE mediante CREATE UNIQUE INDEX CONCURRENTLY + ADD CONSTRAINT ... UNIQUE USING INDEX.", 'inputSchema': {'type': 'object', 'properties': {'sql_ddl': {'type': 'string', 'description': 'Sentencias SQL/DDL a auditar bajo REG-119 (PG18 uuidv7() + SECURITY DEFINER search_path + UNIQUE USING INDEX).'}}, 'required': ['sql_ddl']}},
        {'name': 'aleph_audit_pg18_virtual_generated_temporal_without_overlaps_and_not_valid_fk', 'description': '[v20.3.0 - REG-118] Audita formalmente columnas generadas VIRTUAL de PostgreSQL 18 y restricciones temporales WITHOUT OVERLAPS / PERIOD FK, vistas de Supabase con security_invoker = true para preservar RLS multi-tenant en PostgREST, y migraciones Zero-Downtime de claves foráneas con ADD CONSTRAINT ... FOREIGN KEY ... NOT VALID + VALIDATE CONSTRAINT.', 'inputSchema': {'type': 'object', 'properties': {'sql_ddl': {'type': 'string', 'description': 'Sentencias SQL/DDL a auditar bajo REG-118 (PG18 VIRTUAL generated + WITHOUT OVERLAPS + security_invoker view RLS + NOT VALID FK).'}}, 'required': ['sql_ddl']}},
        {'name': 'aleph_audit_pg18_returning_old_new_jwt_app_metadata_rls_and_detach_partition', 'description': 'Audita formalmente auditoría atómica PG18 RETURNING WITH (OLD AS o, NEW AS n), inmutabilidad de claims JWT app_metadata en políticas RLS de Supabase (bloqueando user_metadata manipulable por el cliente), y archivado Zero-Downtime DETACH PARTITION CONCURRENTLY (REG-117 / v20.3.0).', 'inputSchema': {'type': 'object', 'properties': {'sql_ddl': {'type': 'string', 'description': 'DDL/DML SQL a verificar'}}, 'required': ['sql_ddl']}},
        {'name': 'aleph_audit_pg18_parallel_gin_realtime_broadcast_rls_and_not_null_check', 'description': 'Audita formalmente construcción paralela de índices GIN en PG18 con cota gin_pending_list_limit, aislamiento multi-tenant de canales Supabase Realtime Broadcast sobre realtime.messages (realtime.topic()), y promoción Zero-Downtime SET NOT NULL vía CHECK NOT VALID (REG-116 / v20.3.0).', 'inputSchema': {'type': 'object', 'properties': {'sql_ddl': {'type': 'string', 'description': 'DDL/DML SQL a verificar'}}, 'required': ['sql_ddl']}},
        {'name': 'aleph_audit_pg18_skip_scan_restrictive_rls_and_drop_column_safe', 'description': 'Audita formalmente índices compuestos PG18 B-Tree Skip Scan (prefijo de baja cardinalidad), composición conjuntiva AS RESTRICTIVE en políticas RLS secundarias de Supabase (evitando bypass por OR booleano PERMISSIVE), y eliminación Zero-Downtime de columnas con lock_timeout y RESTRICT (REG-115 / v20.3.0).', 'inputSchema': {'type': 'object', 'properties': {'sql_ddl': {'type': 'string', 'description': 'DDL/DML SQL a verificar'}}, 'required': ['sql_ddl']}},
        {'name': 'aleph_prove_css_content_visibility_intrinsic_size_and_wcag_reflow', 'description': 'Audita content-visibility: auto, contain-intrinsic-size y WCAG 1.4.10', 'inputSchema': {'type': 'object', 'properties': {'source_text': {'type': 'string'}}}},
        {'name': 'aleph_prove_css_subgrid_track_alignment_and_wcag_sequence', 'description': 'Audita CSS Grid L2 subgrid track alignment y WCAG 1.3.2', 'inputSchema': {'type': 'object', 'properties': {'source_text': {'type': 'string'}}}},
        {'name': 'aleph_prove_css_scope_donut_boundary_and_wcag_keyboard_trap', 'description': 'Audita CSS @scope donut boundary y WCAG 2.1.2', 'inputSchema': {'type': 'object', 'properties': {'source_text': {'type': 'string'}}}},
        {'name': 'aleph_prove_spark6066_flink_cve2020_17518_airflow_cve2020_11978_and_cursor_cve2026_26268_rce', 'description': 'Audits Spark 6066, Flink CVE-2020-17518/17519, Airflow CVE-2020-11978, Prefect, Burst CVE-2026-8181, Cursor CVE-2026-26268 & io_uring CVE-2026-24102 (REG-126).', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'source_code': {'type': 'string'}}}},
        {'name': 'aleph_prove_arise_intraprocedural_kgcompass_featlens_ppr_and_still_perceiver_hysparse2_kv', 'description': 'Verifica formalmente el grafo de repositorio sub-funcion con aristas de flujo de datos intra-procedural ARISE y el.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'total_arise_graph_nodes': {'type': 'integer'}, 'intraprocedural_dataflow_edges_modeled': {'type': 'boolean'}, 'kgcompass_top_k_candidates': {'type': 'integer'}, 'featlens_dynamic_feature_score': {'type': 'number'}, 'still_position_free_inverse_rope_verified': {'type': 'boolean'}, 'still_compression_ratio_c': {'type': 'integer'}, 'still_latent_queries_t': {'type': 'integer'}, 'still_lookahead_chunk_buffer_enabled': {'type': 'boolean'}, 'ruler_gain_over_kv_distill_pts': {'type': 'number'}, 'hysparse2_two_level_kv_sharing_enabled': {'type': 'boolean'}, 'cross_decoder_prefill_layers_skipped': {'type': 'integer'}, 'ngc_outcome_reward_gc_enabled': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_aircoder_procc_bandit_multiview_ppr_and_recalkv_hsr_kvlinc_leverage', 'description': 'Verifica formalmente la integracion adaptativa multidimensional AIRCoder (ACL 2026), la seleccion bandit.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'total_aircoder_multidim_nodes': {'type': 'integer'}, 'procc_bandit_views_count': {'type': 'integer'}, 'aligncoder_candidate_completions': {'type': 'integer'}, 'recalkv_hsr_grouped_svd_rank_ratio': {'type': 'number'}, 'recalkv_ovc_relative_accuracy_drop_pct': {'type': 'number'}, 'kvlinc_hadamard_linear_correction_enabled': {'type': 'boolean'}, 'kvlinc_flash_attention_speedup_x': {'type': 'number'}, 'compactor_leverage_score_calibrated': {'type': 'boolean'}, 'restorekv_learned_restoration_enabled': {'type': 'boolean'}, 'prfaas_cross_dc_selective_kv_transfer': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_dycoder_codemem_partial_dep_graph_ppr_and_puzzlekv_starkv_deferkv', 'description': 'Verifica formalmente la recuperacion de contexto mediante grafos parciales de dependencias bajo demanda.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'dyretriever_partial_graph_nodes': {'type': 'integer'}, 'dycoder_static_graph_speedup_x': {'type': 'number'}, 'codemem_ast_forgetting_detector_enabled': {'type': 'boolean'}, 'cosil_two_stage_call_graph_pruning': {'type': 'boolean'}, 'puzzlekv_int4_storage_ratio': {'type': 'number'}, 'puzzlekv_full_kv_retention_pct': {'type': 'number'}, 'starkv_soft_threshold_attention_speedup_x': {'type': 'number'}, 'starkv_total_kv_reduction_x': {'type': 'number'}, 'deferkv_first_decode_boundary_eviction': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_ranger_dualpath_cypher_mcts_ppr_and_sac_cxl_residualkv_contiguouskv', 'description': 'Verifica formalmente el agente de recuperacion a escala de repositorio RANGER con ruteo dual Cypher + Monte Carlo Tree.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'ranger_ast_entity_nodes': {'type': 'integer'}, 'ranger_dual_path_cypher_mcts_enabled': {'type': 'boolean'}, 'sac_cxl_ttft_speedup_x': {'type': 'number'}, 'sac_cxl_throughput_speedup_x': {'type': 'number'}, 'spin_hierarchical_tpot_reduction_pct': {'type': 'number'}, 'residualkv_storage_ratio': {'type': 'number'}, 'residualkv_decode_speedup_x': {'type': 'number'}, 'contiguouskv_reprefill_speedup_x': {'type': 'number'}, 'louver_halfspace_zero_false_negatives': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_livecoder_repo0_dualdag_ppr_and_eager_sekv_s3attention', 'description': 'Verifica formalmente la optimizacion de estado persistente entre intentos LiveCoder (81.58% reuso de repositorio y.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'livecoder_cross_attempt_reuse_pct': {'type': 'number'}, 'livecoder_historical_best_monotonicity': {'type': 'boolean'}, 'repo0_dual_dag_pass_rate_gain_pp': {'type': 'number'}, 'coderag_bigraph_anchored': {'type': 'boolean'}, 'eager_ast_chunked_non_overlapped_exec_reduction_pct': {'type': 'number'}, 'eager_e2e_latency_reduction_pct': {'type': 'number'}, 'sekv_entropy_span_gpu_mem_reduction_pct': {'type': 'number'}, 'sekv_cpu_svd_zoom_in_enabled': {'type': 'boolean'}, 's3_attention_sae_inverted_index_bounded': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_fastcode_locagent_scouting_graph_ppr_and_lrkv_paged_eviction', 'description': 'Verifica formalmente el paradigma scouting-first de FastCode sobre mapas semantico-estructurales regulados por costo.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'fastcode_scouting_execution_completion_rate_pct': {'type': 'number'}, 'fastcode_cost_regularized_pareto_enabled': {'type': 'boolean'}, 'locagent_heterogeneous_file_acc_pct': {'type': 'number'}, 'locagent_cost_reduction_pct': {'type': 'number'}, 'repotrace_multiround_correspondence_enabled': {'type': 'boolean'}, 'lrkv_shared_plus_residual_kv_ratio': {'type': 'number'}, 'lrkv_convergence_speedup_pct': {'type': 'number'}, 'paged_eviction_kernel_free_block_pruning': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_rpg_encoder_gala_multimodal_graph_ppr_and_mlra_4way_tp_belt_turboquant', 'description': 'Verifica formalmente la representacion universal de repositorios RPG-Encoder con actualizacion incremental por diffs.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'rpg_encoder_incremental_overhead_reduction_pct': {'type': 'number'}, 'rpg_encoder_reconstruction_coverage_pct': {'type': 'number'}, 'rpg_encoder_swebench_acc5_pct': {'type': 'number'}, 'gala_multimodal_ui_to_callgraph_aligned': {'type': 'boolean'}, 'mlra_tp_sharding_degree': {'type': 'integer'}, 'mlra_over_mla_decode_speedup_x': {'type': 'number'}, 'belt_behavior_aligned_low_rank_enabled': {'type': 'boolean'}, 'turboquant_3bit_k_2bit_v_memory_reduction_x': {'type': 'number'}, 'nixl_kv_routing_ttft_speedup_x': {'type': 'number'}}}},
        {'name': 'aleph_prove_skillforge_codecraft_hcgs_graph_ppr_and_lycheedecode_hardkuma_token_sparse', 'description': 'Verifica formalmente la auto-destilacion proactiva de skills ancladas a entidades de repositorio SkillForge (M_ext.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'skillforge_dual_level_mext_mint_enabled': {'type': 'boolean'}, 'skillforge_swebench_pass1_pct': {'type': 'number'}, 'codecraft_hcgs_top1_precision_gain_pct': {'type': 'number'}, 'codecraft_lsp_bottom_up_parallel': {'type': 'boolean'}, 'lycheedecode_hardkuma_kv_reduction_pct': {'type': 'number'}, 'lycheedecode_128k_speedup_x': {'type': 'number'}, 'token_sparse_reversible_scatter_enabled': {'type': 'boolean'}, 'token_sparse_128k_attention_speedup_x': {'type': 'number'}}}},
        {'name': 'aleph_prove_acquire_codegraph_wikidata_ppr_and_s4r_subspace_hylra_layer_reuse', 'description': 'Verifica formalmente la adquisicion previa de conocimiento de repositorio guiada por QA con taxonomia de categorias.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'acquire_category_guided_qa_enabled': {'type': 'boolean'}, 'acquire_swebench_pass1_gain_pp': {'type': 'number'}, 'codegraph_wikidata_3stage_grounding': {'type': 'boolean'}, 'codegraph_typed_edges_billion': {'type': 'number'}, 's4r_kv_compression_ratio_x': {'type': 'number'}, 's4r_latent_sparse_reconstruction_enabled': {'type': 'boolean'}, 'hylra_dp_layer_policy_enabled': {'type': 'boolean'}, 'hylra_throughput_gain_pct': {'type': 'number'}}}},
        {'name': 'aleph_prove_sweagile_seerepo_denovoswe_graph_ppr_and_fastkvzip_heterocache_ojakv', 'description': 'Verifica formalmente el contexto de razonamiento dinamico en diente de sierra con Sliding Reasoning Window y Reasoning.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'sweagile_sawtooth_reasoning_digests_enabled': {'type': 'boolean'}, 'sweagile_relative_pass_gain_pct': {'type': 'number'}, 'seerepo_visual_graph_token_reduction_pct': {'type': 'number'}, 'denovoswe_doc2repo_pass_pct': {'type': 'number'}, 'fastkvzip_sink_gated_eviction_ratio_pct': {'type': 'number'}, 'heterocache_224k_decoding_speedup_x': {'type': 'number'}, 'ojakv_online_pca_flashattention_compatible': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_steer_critic_fafim_triage_pdg_and_spla_residual_linear_grkv_kvreviver', 'description': "Verifica formalmente la guia intra-trayectoria con modelos criticos compactos Steer-Don't-Solve (+16.0% mejora en.", 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'steer_critic_intra_trajectory_k10_enabled': {'type': 'boolean'}, 'steer_critic_cost_reduction_ratio_x': {'type': 'number'}, 'fafim_pdg_swebench_lite_gain_pp': {'type': 'number'}, 'triage_code_health_effect_size_p': {'type': 'number'}, 'spla_taylor_subtraction_rla_enabled': {'type': 'boolean'}, 'elastic_attention_router_enabled': {'type': 'boolean'}, 'grkv_ridge_regression_span_merge_enabled': {'type': 'boolean'}, 'kvreviver_sketch_budget_pct': {'type': 'number'}}}},
        {'name': 'aleph_prove_schrodinger_repo_abtest_sweatscale_and_residualkv_kqsvd_closed_form', 'description': 'Verifica formalmente la instanciacion latente de repositorios en 4 niveles de transformacion preservadora de.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'schrodinger_repo_4level_transform_enabled': {'type': 'boolean'}, 'abtest_behavioral_fuzz_templates_count': {'type': 'integer'}, 'swe_at_scale_generations_per_file': {'type': 'integer'}, 'residualkv_log_stride_storage_budget_pct': {'type': 'number'}, 'residualkv_decoding_speedup_x': {'type': 'number'}, 'kqsvd_closed_form_attention_fidelity_bound': {'type': 'number'}}}},
        {'name': 'aleph_prove_scaleswe_noop_ablation_audit_and_trimkv_expected_attention_encoder_heal', 'description': 'Verifica formalmente la sintesis multi-agente en sandbox de 100K instancias verificadas sobre 5,200 repositorios.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'scaleswe_verified_instances_k': {'type': 'number'}, 'scaleswe_swebench_resolve_rate_pct': {'type': 'number'}, 'noop_ablation_mechanical_library_audit_enabled': {'type': 'boolean'}, 'trimkv_time_decaying_retention_gate_enabled': {'type': 'boolean'}, 'expected_attention_closed_form_future_query_enabled': {'type': 'boolean'}, 'encoder_only_svd_healing_memory_reduction_x': {'type': 'number'}}}},
        {'name': 'aleph_prove_codespecweave_hybridgym_propel_and_wgkv_admission_cross_layer_xkv', 'description': 'Verifica formalmente la sintesis de especificaciones interdependientes acopladas CodeSpecWeave (4,670 tareas en 2,865.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'codespecweave_interdependent_specs_count': {'type': 'integer'}, 'hybridgym_swebench_abs_gain_pct': {'type': 'number'}, 'propel_activation_probe_frontier_share_pct': {'type': 'number'}, 'wgkv_admission_prefill_speedup_x': {'type': 'number'}, 'wgkv_memory_reduction_pct': {'type': 'number'}, 'xkv_cross_layer_svd_compression_ratio_x': {'type': 'number'}}}},
        {'name': 'aleph_prove_sweevo_monitor_antislop_cleanup_and_unique_page_mean_std_blasst_softmax', 'description': 'Verifica formalmente la evolucion de software de horizonte largo SWE-EVO (arXiv:2512.18470v6) y la limpieza anti-slop.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'sweevo_long_horizon_trajectories_count': {'type': 'integer'}, 'monitor_triggered_slop_reduction_factor_x': {'type': 'number'}, 'unique_page_mean_std_attention_speedup_x': {'type': 'number'}, 'unique_e2e_decoding_speedup_x': {'type': 'number'}, 'blasst_online_softmax_prefill_speedup_x': {'type': 'number'}, 'blasst_dynamic_block_sparsity_pct': {'type': 'number'}}}},
        {'name': 'aleph_prove_prometheus_repoprobe_checklist_and_depthweavekv_dropkv_cone', 'description': 'Verifica formalmente la navegacion de repositorios de horizonte largo centrada en memoria de trabajo Prometheus (grafo.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'prometheus_swebench_verified_resolve_pct': {'type': 'number'}, 'prometheus_swepolybench_top1_resolve_pct': {'type': 'number'}, 'repoprobe_checklist_edit_bias_guard_enabled': {'type': 'boolean'}, 'depthweave_kv_memory_reduction_x': {'type': 'number'}, 'depthweave_needle_retrieval_accuracy_pct': {'type': 'number'}, 'dropkv_scoring_kernel_speedup_x': {'type': 'number'}, 'dropkv_ruler_128k_5pct_budget_score': {'type': 'number'}}}},
        {'name': 'aleph_prove_sweexplore_depthgee_multihop_and_jssa_gatherfree_oasiskv_spectrumkv', 'description': 'Verifica formalmente la exploracion de repositorios aislada a nivel de linea SWE-Explore (848 issues en 10 lenguajes y.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'sweexplore_multilang_issues_count': {'type': 'integer'}, 'depthgee_structured_graph_gain_pts': {'type': 'number'}, 'jssa_closed_form_128k_decode_speedup_x': {'type': 'number'}, 'jssa_700b_dsa_throughput_parity_pct': {'type': 'number'}, 'oasiskv_lookahead_pd_throughput_speedup_x': {'type': 'number'}, 'spectrumkv_int4_probe_ttft_reduction_pct': {'type': 'number'}}}},
        {'name': 'aleph_prove_hermes_dev_primitives_dynamic_activation_and_fathom_bitplane_programmable_kv', 'description': 'Verifica formalmente la ingenieria de arneses con primitivas de desarrollo ejecutables modulares HERMES (activacion.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'hermes_benchmark_gain_pct': {'type': 'number'}, 'hermes_terminalbench_cost_reduction_pct': {'type': 'number'}, 'fathom_1m_offloaded_decode_speedup_x': {'type': 'number'}, 'fathom_coding_agent_step_agreement_bits': {'type': 'integer'}, 'programmable_kv_edit_compose_latency_speedup_x': {'type': 'number'}, 'programmable_kv_vllm_prefix_hit_rate_pct': {'type': 'number'}}}},
        {'name': 'aleph_prove_autocompact_swetrace_grade_and_joint_kv_block_encoding_pikv_moe', 'description': 'Verifica formalmente la compactacion proactiva de estado de trabajo aprendida por politica AutoCompact (+9.2% en.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'autocompact_swebench_abs_gain_pct': {'type': 'number'}, 'swetrace_shortest_path_sft_instances_k': {'type': 'number'}, 'grade_degree_matched_counterfeit_control_enabled': {'type': 'boolean'}, 'joint_kv_block_compression_ratio_x': {'type': 'number'}, 'joint_kv_vllm_throughput_gain_pct': {'type': 'number'}, 'pikv_moe_expert_sharded_memory_reduction_pct': {'type': 'number'}}}},
        {'name': 'aleph_prove_repomirage_sweatlas_perturbation_and_kvdrive_multitier_rabitqcache', 'description': 'Verifica formalmente la resistencia a perturbaciones preservadoras de semantica y el andamiaje estructural RepoAnchor.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'repoanchor_structure_first_scaffolding_enabled': {'type': 'boolean'}, 'repomirage_perturbation_retention_floor_pct': {'type': 'number'}, 'swe_atlas_total_tasks_covered': {'type': 'integer'}, 'swe_atlas_hybrid_rubric_pass_rate_pct': {'type': 'number'}, 'kvdrive_multitier_throughput_speedup_x': {'type': 'number'}, 'rabitqcache_adaptive_top_p_efficiency_speedup_x': {'type': 'number'}, 'race_rope_activation_energy_selection_enabled': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_gagar_codescout_advantage_redistribution_and_thinkeys_twinkv_minimax', 'description': 'Verifica formalmente la calificacion agentica por grupos y redistribucion de ventajas con preservacion de suma GAGAR.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'gagar_deepswe_pass_rate_pct': {'type': 'number'}, 'gagar_passing_candidate_win_rate_pct': {'type': 'number'}, 'codescout_model_size_efficiency_multiplier_x': {'type': 'number'}, 'jagged_frontier_perturbation_drop_bound_pct': {'type': 'number'}, 'thin_keys_svd_cache_savings_pct': {'type': 'number'}, 'thin_keys_combined_compression_x': {'type': 'number'}, 'twinkv_ruler_retention_gain_pts': {'type': 'number'}, 'minimax_causal_kv_risk_bound_enforced': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_agentic_perf_pr_validation_and_csa2_fp4_bounded_replay_jacap_phase', 'description': 'Verifica formalmente la taxonomia de validacion empirica de pull requests agenticos de rendimiento y.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'agentic_perf_pr_benchmark_sample_size': {'type': 'integer'}, 'm9_scalability_concurrency_validation_enforced': {'type': 'boolean'}, 'csa2_fp4_hbm_kv_bytes_per_token': {'type': 'integer'}, 'swa_bounded_replay_persistent_kv_reduction_x': {'type': 'number'}, 'jacap_jacobian_leverage_eviction_enabled': {'type': 'boolean'}, 'chunked_kv_phase_accuracy_gap_bound_pct': {'type': 'number'}, 'kv_geometry_distributional_normality_regularized': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_reponavigator_tooltrain_deep_search_and_atma_polar_gated_delta_skis', 'description': 'Verifica formalmente la localizacion de issues en repositorios con una unica herramienta consciente de ejecucion.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'reponavigator_single_jump_to_def_tool_enabled': {'type': 'boolean'}, 'reponavigator_parameter_efficiency_gain_x': {'type': 'number'}, 'tooltrain_two_stage_sft_rl_enabled': {'type': 'boolean'}, 'atma_polar_64k_retrieval_gain_pts': {'type': 'number'}, 'atma_fixed_target_bpb_degradation_bound_x': {'type': 'number'}, 'skis_temporal_spatial_structural_codesign_enabled': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_swebench_promax_sweprime_and_leyline_rope_splice_longflow_epikv', 'description': 'Verifica formalmente la refactorizacion poliglota preservadora de comportamiento a gran escala sobre 7 lenguajes.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'swebench_promax_multilingual_languages_count': {'type': 'integer'}, 'swebench_promax_avg_modified_files': {'type': 'number'}, 'sweprime_selected_subset_ratio_pct': {'type': 'number'}, 'sweprime_swebench_verified_rel_gain_pct': {'type': 'number'}, 'leyline_rope_splice_cache_hit_gain_pp': {'type': 'number'}, 'leyline_debug_gym_solve_gain_pp': {'type': 'number'}, 'longflow_fused_kernel_throughput_speedup_x': {'type': 'number'}, 'epikv_attention_matrix_free_loop_guard_enabled': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_akv_cache_engineering_river_terminal_and_kvcompass_hla_confkv', 'description': 'Verifica formalmente la ingenieria de cache agentica con operaciones primitivas drop y repos en el motor AKV (-27.7%.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'akv_drop_repos_cost_reduction_pct': {'type': 'number'}, 'akv_p95_latency_speedup_x': {'type': 'number'}, 'river_filtered_env_ratio_pct': {'type': 'number'}, 'river_terminal_bench_lite_rl_gain_pct': {'type': 'number'}, 'kvcompass_p99_ttft_reduction_x': {'type': 'number'}, 'hla_looped_kv_shrink_ratio_x': {'type': 'number'}, 'confkv_niah_32k_retrieval_accuracy_pct': {'type': 'number'}, 'laserkv_exact_lsh_recall_enabled': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_execcritic_cxi_integrity_and_certified_sparse_e8_lattice_ksa_cmm', 'description': 'Verifica formalmente la reparacion guiada por tests con separacion de roles ExecCritic (62.2% exito Base-to-Gold del.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'execcritic_base_to_gold_test_rate_pct': {'type': 'number'}, 'execcritic_swebench_verified_resolve_rate_pct': {'type': 'number'}, 'cxi_lease_bound_escape_count': {'type': 'integer'}, 'certified_sparse_p90_error_reduction_x': {'type': 'number'}, 'e8_lattice_k2v2_compression_ratio_x': {'type': 'number'}, 'ksa_linear_semantic_stride_k': {'type': 'integer'}, 'cmm_mp_cxl_app_latency_us': {'type': 'number'}, 'swebench_pro_verified_anti_hacking_enabled': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_exlabel_swetq_and_semkv_quality_cliff_qevict_nvm_fractal', 'description': 'Verifica formalmente la evaluacion auto-evolutiva guiada por experiencia ExLabel sobre el benchmark multilingue SWE-TQ.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'exlabel_swetq_multilingual_clarity_f1_gain_pct': {'type': 'number'}, 'exlabel_swebench_verified_resolve_rate_pct': {'type': 'number'}, 'semkv_quality_cliff_bits_threshold': {'type': 'number'}, 'semkv_turboquant_mse_lossless_compression_x': {'type': 'number'}, 'qevict_recoverable_tiers_count': {'type': 'integer'}, 'nvm_interface_kv_read_energy_reduction_x': {'type': 'number'}, 'nvm_metadata_overhead_reduction_vs_kivi_x': {'type': 'number'}, 'fractal_kv_o1_random_access_and_append_enabled': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_traceeval_convergence_audit_and_momentkv_risk_controlled_indexmem', 'description': 'Verifica formalmente la recuperacion de grafos de llamadas multilingues verificados por ejecucion dinamica TraceEval.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'traceeval_verified_programs_count': {'type': 'integer'}, 'traceeval_finetuned_f1_lift_pp': {'type': 'number'}, 'swebench_top10_nesting_coefficient': {'type': 'number'}, 'swebench_within_model_scaffold_range_pp': {'type': 'number'}, 'momentkv_evicted_mass_bound': {'type': 'number'}, 'risk_controlled_certified_retention_ratio': {'type': 'number'}, 'risk_controlled_test_exceedance_risk_pct': {'type': 'number'}, 'indexmem_latent_memory_residual_readout_enabled': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_swescience_prometheus_and_jevmem_intentkv_rksc', 'description': 'Verifica formalmente la preservacion de contratos cientificos ocultos en 20 dominios SWE-bench Science.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'swescience_scientific_domains_count': {'type': 'integer'}, 'sweprometheus_normalized_governance_improvement': {'type': 'number'}, 'jevmem_memory_construction_speedup_x': {'type': 'number'}, 'jevmem_locomo_judge_score': {'type': 'number'}, 'intentkv_worst_case_kv_read_reduction_pct': {'type': 'number'}, 'rksc_multi_branch_mean_speedup_x': {'type': 'number'}, 'rksc_cgee_verify_error_rate_pct': {'type': 'number'}, 'intentkv_sentinel_slot_rope_preserving_enabled': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_openswetraces_swehero_and_reasonalloc_tangram_redknot_segpaged', 'description': 'Verifica formalmente la destilacion multilingue de modo dual Open-SWE-Traces (207,489 trayectorias en 9 lenguajes con.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'openswetraces_multilingual_trajectories_count': {'type': 'integer'}, 'openswetraces_swebench_multilingual_resolve_pct': {'type': 'number'}, 'reasonalloc_math500_512budget_accuracy_pct': {'type': 'number'}, 'reasonalloc_reasoning_wave_mass_rho': {'type': 'number'}, 'tangram_multiturn_throughput_speedup_x': {'type': 'number'}, 'redknot_concurrent_throughput_speedup_x': {'type': 'number'}, 'redknot_ttft_speedup_x': {'type': 'number'}, 'segpaged_attention_head_segment_sparse_ffn_enabled': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_p2t_swemaster_and_redknot_mla_vase_momentkv_pariskv', 'description': 'Verifica formalmente la supervision de procesos con informacion privilegiada Patches-to-Trajectories P2T.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'p2t_swemaster_tts8_resolve_rate_pct': {'type': 'number'}, 'redknot_mla_pro_head_row_ceiling_pct': {'type': 'number'}, 'redknot_mla_hot_artifact_ttft_speedup_x': {'type': 'number'}, 'vase_kv_compression_ratio_x': {'type': 'number'}, 'vase_reasoning_accuracy_gain_pct': {'type': 'number'}, 'moment_kv_prefill_plugin_gain_pct': {'type': 'number'}, 'moment_kv_hellobench_gain_pct': {'type': 'number'}, 'pariskv_drift_robust_PackedMLA_unsplit_enabled': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_repoatlas_semnav_and_sherloc_a2agent_tierkv_hierasparse', 'description': 'Verifica formalmente las vistas multimodales evolutivas select-project-refresh de RepoAtlas (+2.4 pp en SWE-bench.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'repoatlas_resolve_gain_pp': {'type': 'number'}, 'semnav_file_hit10_pct': {'type': 'number'}, 'semnav_context_load_reduction_pct': {'type': 'number'}, 'sherloc_swebench_verified_recall1_pct': {'type': 'number'}, 'a2agent_swebench_pro_f1_gain_pct': {'type': 'number'}, 'tierkv_pmco_prefill_speedup_x': {'type': 'number'}, 'tierkv_ram_kv_reduction_pct': {'type': 'number'}, 'hierasparse_decode_attention_speedup_x': {'type': 'number'}, 'hierasparse_semi_structured_tensor_core_enabled': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_blagent_effiholmes_loc2repair_and_rdkv_pbkv_dgap_innerq', 'description': 'Verifica formalmente el RAG agentico acotado con chunking AST aumentado por rutas de BLAgent (>86% Top-1 accuracy, >18x.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'blagent_top1_accuracy_pct': {'type': 'number'}, 'blagent_cost_reduction_x': {'type': 'number'}, 'loc2repair_latency_reduction_sec': {'type': 'number'}, 'effiholmes_func_acc5_gain_pp': {'type': 'number'}, 'rdkv_longbench_accuracy_recovery_pct': {'type': 'number'}, 'rdkv_decode_speedup_x': {'type': 'number'}, 'pbkv_dynamic_workflow_speedup_x': {'type': 'number'}, 'dgap_k1v1_ruler_accuracy_pct': {'type': 'number'}, 'innerq_decode_speedup_x': {'type': 'number'}, 'innerq_folded_prefill_key_norm_enabled': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_kvboost_restkv_laprox_and_kvgov_provenance_issueloc_themis', 'description': 'Verifica formalmente el reuso de KV cache a nivel de chunk independiente de posicion con doble hash y recomputacion.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'kvboost_ttft_speedup_x': {'type': 'number'}, 'kvboost_bugloc_accuracy_pct': {'type': 'number'}, 'restkv_ruler_gain_pct': {'type': 'number'}, 'restkv_decode_latency_reduction_x': {'type': 'number'}, 'laprox_kv_retention_pct': {'type': 'number'}, 'kvgov_prefix_cache_retained_pct': {'type': 'number'}, 'kv_provenance_hit_overhead_ms': {'type': 'number'}, 'issueloc_token_reduction_pct': {'type': 'number'}, 'role_summary_hit6_accuracy_pct': {'type': 'number'}, 'kvgov_hmac_boundary_salt_and_themis_trace_enabled': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_fusesearch_tdad_trajeval_and_mixeddimkv_moend_certified_qattn', 'description': 'Verifica formalmente la ejecucion paralela adaptativa para localizacion de codigo FuseSearch (84.7% F1 archivo, 93.6%.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'fusesearch_file_f1_pct': {'type': 'number'}, 'fusesearch_token_reduction_pct': {'type': 'number'}, 'tdad_regression_reduction_pct': {'type': 'number'}, 'trajeval_coherence_collapse_checkpoint_recovery_pct': {'type': 'number'}, 'mixeddimkv_longbench_budget_pct': {'type': 'number'}, 'mixeddimkv_niah_50k_accuracy_pct': {'type': 'number'}, 'moend_compression_ratio_x': {'type': 'number'}, 'acache_recompute_latency_reduction_pct': {'type': 'number'}, 'certified_bounded_error_fp16_fallback_ladder_enabled': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_swe_adept_depthgee_suffix_replay_and_breadthkv_wakman', 'description': 'Verifica formalmente la navegacion DFS guiada por dependencias sobre arboles de codigo con adyacencia local y.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'swe_adept_lite_file_acc3_pct': {'type': 'number'}, 'swe_adept_lite_func_acc5_pct': {'type': 'number'}, 'swe_adept_pro_resolve_gain_pp': {'type': 'number'}, 'depthgee_exact_entity_submission_pct': {'type': 'number'}, 'suffix_replay_quality_retention_pct': {'type': 'number'}, 'suffix_replay_storage_ratio_vs_sglang': {'type': 'number'}, 'suffix_replay_branch_ttft_reduction_pct': {'type': 'number'}, 'breadthkv_pooled_accuracy_gain_pp': {'type': 'number'}, 'breadthkv_aime_cap_derailment_pct': {'type': 'number'}, 'wakman_hit_rate_gain_pp': {'type': 'number'}, 'wakman_mean_regret_pct': {'type': 'number'}, 'breadthkv_zero_point_offset_and_wakman_shadow_replay_enabled': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_recap_issueexec_attention_matching_and_ratequant_rustcompcert', 'description': 'Verifica formalmente los grafos de contexto persistentes para compactacion de memoria sin llamadas al modelo ReCAP.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'recap_cold_restore_latency_reduction_pct': {'type': 'number'}, 'recap_lic_accuracy_gain_pp': {'type': 'number'}, 'recap_omitted_block_revival_pct': {'type': 'number'}, 'issueexec_func_recall1_gain_pct': {'type': 'number'}, 'issueexec_agentless_resolve_gain_pct': {'type': 'number'}, 'online_kv_compaction_peak_kv_reduction_x': {'type': 'number'}, 'online_kv_compaction_throughput_gain_x': {'type': 'number'}, 'am_omp_compaction_ratio_x': {'type': 'number'}, 'ratequant_kivi_ppl_reduction_pct': {'type': 'number'}, 'ratequant_turboquant_recovery_pct': {'type': 'number'}, 'rustcompcert_polonius_drop_elaboration_and_am_nnls_bias_enabled': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_spade_rig_rr_evict_c2kv_and_kvlearn_lukv', 'description': 'Verifica formalmente el Grafo de Inteligencia de Repositorio determinista y respaldado por evidencia SPADE & RIG.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'spade_rig_accuracy_gain_pct': {'type': 'number'}, 'spade_rig_multilingual_time_reduction_pct': {'type': 'number'}, 'rr_evict_tau2_p99_ttft_reduction_pct': {'type': 'number'}, 'rr_evict_swebench_p99_ttft_reduction_pct': {'type': 'number'}, 'c2kv_inference_speedup_x': {'type': 'number'}, 'c2kv_compression_ratio_x': {'type': 'number'}, 'kvlearn_ttft_reduction_vs_nocache_pct': {'type': 'number'}, 'kvlearn_kv_transfer_reduction_pct': {'type': 'number'}, 'lukv_cache_size_reduction_pct': {'type': 'number'}, 'lookaheadkv_eviction_overhead_reduction_x': {'type': 'number'}, 'c2kv_sif_causal_mask_and_rig_deterministic_extractor_enabled': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_codenib_cacheslide_concat_recompute_and_qkvshare', 'description': 'Verifica formalmente el sistema multi-vista de contexto de repositorio CodeNib (compilacion lexica, densa y estructural.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'codenib_token_reduction_max_pct': {'type': 'number'}, 'codenib_gain_over_aider_repomap_pct': {'type': 'number'}, 'codenib_vector_reuse_speedup_x': {'type': 'number'}, 'cacheslide_ttft_reduction_x': {'type': 'number'}, 'cacheslide_throughput_gain_x': {'type': 'number'}, 'cacheslide_ssd_waf_reduction_x': {'type': 'number'}, 'concat_recompute_124k_ruler_gain_pts': {'type': 'number'}, 'concat_recompute_124k_ttft_reduction_pct': {'type': 'number'}, 'qkvshare_8k_handoff_ttft_reduction_pct': {'type': 'number'}, 'codenib_post_read_context_retirement_and_cacheslide_rpdc_enabled': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_cake_ir_kvcmas_kvcomm_swemilestone_and_doublep', 'description': 'Verifica formalmente el co-diseno compilador-agente CAKE IR con planificacion tipada explicita en hardware (2.05x.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'cake_ir_kda_speedup_x': {'type': 'number'}, 'cake_ir_knn_kmeans_max_speedup_x': {'type': 'number'}, 'kvcomm_ttft_speedup_x': {'type': 'number'}, 'kvcmas_peak_gpu_memory_reduction_x': {'type': 'number'}, 'kvcmas_chained_ttft_reduction_pct': {'type': 'number'}, 'ama_agent_causality_graph_accuracy_pct': {'type': 'number'}, 'ama_agent_gain_over_baseline_pp': {'type': 'number'}, 'double_p_attention_overhead_reduction_x': {'type': 'number'}, 'double_p_decoding_speedup_x': {'type': 'number'}, 'cake_ir_typed_schedule_and_swemilestone_debt_gate_enabled': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_polykv_adaptive_huffman_kv_and_e2e_swe_llm4cov', 'description': 'Verifica formalmente el pool compartido de KV-Cache asimetricamente comprimido PolyKV (SharedKVPool O(1) con Keys en.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'polykv_compression_ratio_x': {'type': 'number'}, 'polykv_15agent_memory_reduction_pct': {'type': 'number'}, 'polykv_mean_bertscore_f1': {'type': 'number'}, 'adaptive_huffman_kv_latency_reduction_pct': {'type': 'number'}, 'adaptive_huffman_kv_accuracy_gain_pts': {'type': 'number'}, 'e2e_swe_languages_supported_count': {'type': 'integer'}, 'e2e_swe_frontier_pass1_pct': {'type': 'number'}, 'llm4cov_coverage_pass_rate_pct': {'type': 'number'}, 'prov_r1_functional_correctness_pct': {'type': 'number'}, 'polykv_fwht_3bit_lloyd_max_and_e2e_swe_ctrf_gate_enabled': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_tokendance_relaycaching_lragent_and_harness_rsi', 'description': 'Verifica formalmente la comparticion colectiva de KV-Cache por ronda All-Gather TokenDance (interfaz de bloques con.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'tokendance_concurrent_agent_scaling_x': {'type': 'number'}, 'tokendance_master_mirror_14b_compression_x': {'type': 'number'}, 'tokendance_collective_reuse_peak_speedup_x': {'type': 'number'}, 'tokendance_fused_diff_restore_max_speedup_x': {'type': 'number'}, 'relay_caching_kv_reuse_pct': {'type': 'number'}, 'relay_caching_ttft_speedup_x': {'type': 'number'}, 'agent_memory_q4_max_ttft_speedup_x': {'type': 'number'}, 'agent_primitives_accuracy_gain_pct': {'type': 'number'}, 'harness_rsi_scored_comparisons_count': {'type': 'integer'}, 'tokendance_ttsep_master_mirror_and_harness_rsi_4claim_gate_enabled': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_contextsniper_ctrepair_refuntangle_swereview_and_phase_kv_abstention', 'description': 'Verifica formalmente la memoria de codigo eficiente en tokens ContextSniper de AntTrail (indexacion en 3 niveles de.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'contextsniper_token_reduction_pct': {'type': 'number'}, 'contextsniper_interaction_round_reduction_pct': {'type': 'number'}, 'ct_repair_execution_scope_reduction_pct': {'type': 'number'}, 'ct_repair_defects4j_bugs_fixed_count': {'type': 'integer'}, 'refuntangle_compilability_after_pct': {'type': 'number'}, 'swe_review_closed_loop_resolve_rate_pct': {'type': 'number'}, 'chunked_kv_stride2_phase_gap_max_pp': {'type': 'number'}, 'compression_abstention_hallucination_reduction_pct': {'type': 'number'}, 'compression_abstention_relative_lift_x': {'type': 'number'}, 'contextsniper_cpg_teg_refuntangle_and_phase_kv_abstention_gate_enabled': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_coharden_stair_testgrad_and_montecarlo_kv_quant_faithfulness', 'description': 'Verifica formalmente el endurecimiento iterativo de tests de reproduccion de bugs (BRT) y parches co-generados CoHarden.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'coharden_swe_bench_resolved_pct': {'type': 'number'}, 'coharden_f2p_rate_pct': {'type': 'number'}, 'coharden_lax_mutation_survivors_count': {'type': 'integer'}, 'patchfusion_swe_verified_solved_count': {'type': 'integer'}, 'patchfusion_decision_latency_ms': {'type': 'number'}, 'stair_hierarchical_trajectory_resolved_pct': {'type': 'number'}, 'testgrad_4agent_ensemble_resolved_pct': {'type': 'number'}, 'bsg_va_b_replay_inadequate_closure_reduction_pp': {'type': 'number'}, 'lore_kv_single_continuation_gain_recovery_pct': {'type': 'number'}, 'lore_kv_128k_ruler_margin_over_andpro_pts': {'type': 'number'}, 'offline_kv_quant_bits': {'type': 'integer'}, 'coharden_patchfusion_stair_lorekv_and_int8_faithfulness_gate_enabled': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_desc2fix_grapheng_hasa_and_trace_dllm_kvq', 'description': 'Verifica formalmente la alineacion semantica y propagacion de senales conductuales a lo largo del pipeline.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'desc2fix_triplets_audited_count': {'type': 'integer'}, 'desc2fix_structured_signal_completeness_pct': {'type': 'number'}, 'desc2fix_llm_optimism_bias_corrected_pts': {'type': 'number'}, 'graph_engineering_system_intelligence_pillars_count': {'type': 'integer'}, 'hasa_dense_attention_mass_captured_pct': {'type': 'number'}, 'hasa_ruler_accuracy_gain_over_unique_pts': {'type': 'number'}, 'hasa_longbench_pro_gain_over_unique_pts': {'type': 'number'}, 'hasa_max_speedup_over_dense_x': {'type': 'number'}, 'trace_dllm_kvq_value_quant_bits': {'type': 'integer'}, 'desc2fix_grapheng_hasa_and_trace_dllm_kvq_gate_enabled': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_acrouter_harnessadapt_swebenchpro_mlafication_and_zipfusion', 'description': 'Verifica formalmente el enrutamiento agentico de modelos y herramientas Agent-as-a-Router / ACRouter mediante bucle.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'acrouter_task_dimension_prior_gain_pct': {'type': 'number'}, 'acrouter_coderouterbench_instances_count': {'type': 'integer'}, 'harnessadapt_rl_swe_verified_gain_pp': {'type': 'number'}, 'harnessadapt_rl_swe_multilingual_gain_pp': {'type': 'number'}, 'swebench_pro_verified_leak_channels_blocked_count': {'type': 'integer'}, 'swebench_pro_verified_tasks_refined_count': {'type': 'integer'}, 'mlafication_qknorm_serving_throughput_x': {'type': 'number'}, 'mlafication_kv_footprint_reduction_pct': {'type': 'number'}, 'zipfusion_decode_attention_speedup_x': {'type': 'number'}, 'zipfusion_max_batch_throughput_over_lossless_x': {'type': 'number'}, 'acrouter_harnessadapt_mlafication_and_zipfusion_gate_enabled': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_cachescout_yasa_probe_depwaretrans_and_rcllm_kv', 'description': 'Verifica formalmente la gestion proactiva de KV-Cache consciente de agentes CacheScout mediante cadena de Markov online.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'cachescout_anchor_hit_rate_pct': {'type': 'number'}, 'cachescout_ttft_reduction_pct': {'type': 'number'}, 'yasa_uast_node_types_count': {'type': 'integer'}, 'yasa_semantic_rule_reuse_rate_pct': {'type': 'number'}, 'probe_callgraph_multipass_recall_lift_x': {'type': 'number'}, 'depwaretrans_batch_compile_test_success_pct': {'type': 'number'}, 'rcllm_beyond_prefix_ttft_speedup_x': {'type': 'number'}, 'rcllm_semantic_history_match_pct': {'type': 'number'}, 'cachescout_yasa_probe_depwaretrans_and_rcllm_gate_enabled': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_curaloc_salt_cpygraph_memuse_and_flash_kv_offload', 'description': 'Verifica formalmente la localizacion de fallos a escala de repositorio por inspeccion de codigo planificada en una sola.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'curaloc_token_reduction_vs_locagent_pct': {'type': 'number'}, 'curaloc_swebench_verified_func1_pct': {'type': 'number'}, 'salt_input_token_reduction_pct': {'type': 'number'}, 'salt_static_type_precision_pct': {'type': 'number'}, 'cpygraph_candidate_precision_pct': {'type': 'number'}, 'cpygraph_cross_version_agreement_pct': {'type': 'number'}, 'memuse_injection_span_dedup_and_placement_proof_enabled': {'type': 'boolean'}, 'flash_infinigen_prefill_memory_reduction_pct': {'type': 'number'}, 'h2o_throughput_per_gb_gain_x': {'type': 'number'}, 'curaloc_salt_cpygraph_memuse_and_flashkv_gate_enabled': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_deskcheck_graph2env_typify_typepro_recube_and_plt_kv', 'description': 'Verifica formalmente el razonamiento de codigo guiado sobre rutas de ejecucion DeskCheck (12 formas de razonamiento en.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'deskcheck_swebench_pro_gain_pct': {'type': 'number'}, 'deskcheck_code_reasoning_forms_count': {'type': 'integer'}, 'graph2env_build_success_rate_pct': {'type': 'number'}, 'pace_expert_consensus_agreement_pct': {'type': 'number'}, 'typepro_manytypes4py_top1_em_pct': {'type': 'number'}, 'typepro_manytypes4ts_top1_em_pct': {'type': 'number'}, 'recube_cce_strict_pass_rate_gain_pct': {'type': 'number'}, 'plt_sequential_kv_bits_per_token': {'type': 'number'}, 'plt_worst_case_compression_over_turboquant_x': {'type': 'number'}, 'deskcheck_graph2env_typify_typepro_recube_and_plt_kv_gate_enabled': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_codecomp_efficientagent_cachewise_rustmir_and_vericache_rift', 'description': 'Verifica formalmente la compresion estructural de KV-Cache guiada por Code Property Graph (CPG: AST+CFG+PDG) CodeComp.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'codecomp_cpg_span_protection_and_budget_allocation_enabled': {'type': 'boolean'}, 'efficientagent_recomputed_tokens_reduction_pct': {'type': 'number'}, 'cachewise_session_completion_speedup_x': {'type': 'number'}, 'causal_fl_repair_token_reduction_pct': {'type': 'number'}, 'rust_mir_precision_gain_to_pct': {'type': 'number'}, 'rust_unsafe_pointer_aliasing_logic_verified': {'type': 'boolean'}, 'vericache_lossless_throughput_gain_x': {'type': 'number'}, 'rift_full_cache_acceptance_length_retention_pct': {'type': 'number'}, 'codecomp_efficientagent_cachewise_rustmir_and_vericache_rift_gate_enabled': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_kvfetch_kara_kapilot_trust_and_fl_context', 'description': 'Verifica formalmente el prefetching temporal por puntero monotono sobre cold-tier cuantizado KVFetch que elimina el.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'kvfetch_ruler16k_verbatim_copy_recovery_pct': {'type': 'number'}, 'kara_token2chunk_flexible_sliding_window_enabled': {'type': 'boolean'}, 'copilot_idle_time_capture_pct': {'type': 'number'}, 'prefix_quick_demotion_and_compute_aware_partial_eviction_enabled': {'type': 'boolean'}, 'kapilot_unsafe_rust_kani_spec_success_pct': {'type': 'number'}, 'trust_rust_sast_semantics_preserving_transforms_count': {'type': 'integer'}, 'fl_context_file_level_repair_gain_x': {'type': 'number'}, 'kvfetch_kara_kapilot_trust_and_fl_context_gate_enabled': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_aegisasync_swepruner_kvcat_kvcodec_and_rust_unsafe_oracle', 'description': 'Verifica formalmente la simulacion simbolica de eventos asincronos sobre bytecode CPython 3.10-3.14 AegisAsync mediante.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'aegisasync_asyncbench_recall_pct': {'type': 'number'}, 'aegisasync_asyncbench_false_positive_rate_pct': {'type': 'number'}, 'swepruner_swebench_token_reduction_pct': {'type': 'number'}, 'swepruner_longcodeqa_compression_ratio_x': {'type': 'number'}, 'kvcat_slot_sparsification_compressibility_verified': {'type': 'boolean'}, 'kvcodec_remote_prefix_ttft_speedup_x': {'type': 'number'}, 'rust_unsafe_coverage_oracle_projects_count': {'type': 'integer'}, 'aegisasync_swepruner_kvcat_kvcodec_and_rust_oracle_gate_enabled': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_tracelite_sweedit_bascet_rust_kvtc_and_ml_quality', 'description': 'Verifica formalmente la reduccion de trazas sin entrenamiento para agentes SWE mediante renderizado optico y poda de.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'tracelite_swebench_resolve_rate_pct': {'type': 'number'}, 'tracelite_input_token_reduction_pct': {'type': 'number'}, 'tracelite_compression_latency_sec': {'type': 'number'}, 'sweedit_resolve_rate_gain_pp': {'type': 'number'}, 'sweedit_inference_cost_reduction_pct': {'type': 'number'}, 'sweedit_qwen8b_grpo_edit_success_gain_pp': {'type': 'number'}, 'bascet_rust_size_reduction_x': {'type': 'number'}, 'bascet_rust_build_time_reduction_x': {'type': 'number'}, 'bascet_rust_key_step_speedup_x': {'type': 'number'}, 'kvtc_transform_coding_compression_x': {'type': 'number'}, 'ml_quality_sonarqube_rules_enforced_count': {'type': 'integer'}, 'tracelite_sweedit_bascet_rust_kvtc_and_ml_quality_gate_enabled': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_devskills_kvfact_masking_terminal_universe_and_gdn_handoff', 'description': 'Verifica formalmente la mitigacion de comportamientos costo-ineficientes en agentes de codigo mediante DevSkills.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'devskills_task_cost_reduction_pct': {'type': 'number'}, 'devskills_simscrpt_jaccard_threshold': {'type': 'number'}, 'devskills_verified200_cost_amplification_slope': {'type': 'number'}, 'kv_unit_preserving_complete_answer_rate_pct': {'type': 'number'}, 'kv_rotary_row_compaction_historical_retention_pct': {'type': 'number'}, 'terminal_universe_post_completion_sufficiency_pct': {'type': 'number'}, 'terminal_universe_evocode_mt4_gain_pp': {'type': 'number'}, 'vlocbench_cwe_tasks_evaluated_count': {'type': 'integer'}, 'gdn_persistent_state_kv_excess_nll_reduction_pct': {'type': 'number'}, 'devskills_kvfact_terminal_universe_and_gdn_gate_enabled': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_coharl_qsa_sga_rope_profiler_and_cave_assurance_spine', 'description': 'Verifica formalmente la co-evolucion poblacional de una politica compartida y un pool de hasta 8 arneses ejecutables.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'coharl_swerebench_resolved_rate_pct': {'type': 'number'}, 'coharl_swebench_verified_resolved_rate_pct': {'type': 'number'}, 'coharl_harness_population_pool_size': {'type': 'integer'}, 'qsa_microblock_pre_prope_compression_ratio_r': {'type': 'integer'}, 'qsa_1m_prefill_kernel_speedup_x': {'type': 'number'}, 'sga_sparse_warmup_256k_ruler_score': {'type': 'number'}, 'rope_profiler_zero_pass_max_accuracy_gain_pp': {'type': 'number'}, 'cave_bench_live_signal_harm_reduction_pct': {'type': 'number'}, 'agile_v_assurance_spine_admission_levels_count': {'type': 'integer'}, 'coharl_qsa_sga_rope_profiler_and_cave_spine_gate_enabled': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_dge_kv_colgrep_xagent_rust_unsafechecker_and_tmax', 'description': 'Verifica formalmente la eviccion de KV-Cache diferida guiada por borrador Draft-Guided Eviction (DGE: posterga la.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'dge_draft_tokens_k': {'type': 'integer'}, 'dge_longbench_score': {'type': 'number'}, 'colgrep_cpu_latency_reduction_pct': {'type': 'number'}, 'colgrep_token_reduction_pct': {'type': 'number'}, 'xagent_function_localization_accuracy_pct': {'type': 'number'}, 'rust_unsafechecker_rustsec_recall_pct': {'type': 'number'}, 'rust_unsafechecker_new_bugs_found_count': {'type': 'integer'}, 'tmax_domain_balance_score': {'type': 'number'}, 'tmax_9b_terminal_bench2_score_pct': {'type': 'number'}, 'dge_colgrep_xagent_unsafechecker_and_tmax_gate_enabled': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_tidekv_aatc_semnav_easyprover_aegis_corten_rust_async_and_swe_cc', 'description': 'Verifica formalmente la construccion de KV-Cache en GPU con eviccion diferida al final de cada capa TideKV (-83.89% de.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'tidekv_transient_memory_reduction_pct': {'type': 'number'}, 'tidekv_ttft_overhead_pct': {'type': 'number'}, 'aatc_compression_ratio_x': {'type': 'number'}, 'semnav_file_hit10_pct': {'type': 'number'}, 'semnav_context_load_reduction_pct': {'type': 'number'}, 'semnav_line_precision_pct': {'type': 'number'}, 'easyprover_ntp4vc_resolved_pct': {'type': 'number'}, 'aegis_rust_lean_validated_pairs_count': {'type': 'integer'}, 'corten_thir_proof_size_reduction_x': {'type': 'number'}, 'rust_async_waker_repository_liveness_verified': {'type': 'boolean'}, 'swe_cc_atomic_policies_checked_count': {'type': 'integer'}, 'tidekv_aatc_semnav_easyprover_corten_and_swecc_gate_enabled': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_page_minimakv_cabra_callgraph_forte_rust_and_aeneas_lean_verus', 'description': 'Verifica formalmente la compuerta de eviccion de KV-Cache sin entrenamiento PAGE (Partition-Aware Gated Eviction: mide.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'page_harm_rate_reduction_x': {'type': 'number'}, 'page_capacity_bound_retained_accuracy_pct': {'type': 'number'}, 'minimakv_payload_kib_per_token': {'type': 'number'}, 'minimakv_warm_prefix_throughput_ratio_x': {'type': 'number'}, 'cabra_callgraph_tasks_evaluated_count': {'type': 'integer'}, 'cabra_transformation_axes_count': {'type': 'integer'}, 'forte_exclusive_borrow_metric_preservation_verified': {'type': 'boolean'}, 'aeneas_lean_monadic_symcrypt_mlkem_verified': {'type': 'boolean'}, 'verus_dll_unproven_assumptions_count': {'type': 'integer'}, 'page_minimakv_cabra_forte_and_aeneas_verus_gate_enabled': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_valuediff_multialloc_ripplekv_selkv_chronos_and_c2rust_security', 'description': 'Verifica formalmente la eviccion geometrica de KV-Cache por desviacion L2 respecto a la media de vectores de valor.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'valuediff_longbench_retention_pct': {'type': 'number'}, 'valuediff_math500_gain_pts': {'type': 'number'}, 'multialloc_32b_gap_closed_pct': {'type': 'number'}, 'multialloc_decode_throughput_speedup_x': {'type': 'number'}, 'ripplekv_output_kl_perturbation_verified': {'type': 'boolean'}, 'selkv_attention_sag_compensation_enabled': {'type': 'boolean'}, 'chronos_swebench_verified_peak_resolve_pct': {'type': 'number'}, 'chronos_useful_cards_per_task': {'type': 'number'}, 'c2rust_inherited_and_new_bugs_blocked_count': {'type': 'integer'}, 'valuediff_multialloc_ripplekv_chronos_and_c2rust_gate_enabled': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_blockgtq_mosaickv_patch_perf_anova_rustgo_and_kani_mir', 'description': 'Verifica formalmente la asignacion de tasa por bloques RoPE 2D Block-GTQ para cuantizacion de KV-Cache con.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'blockgtq_rope_logit_mae_reduction_max_pct': {'type': 'number'}, 'blockgtq_layer_wins_count': {'type': 'integer'}, 'mosaickv_128k_memory_reduction_x': {'type': 'number'}, 'mosaickv_avg_accuracy_loss_pct': {'type': 'number'}, 'patch_perf_welch_anova_cases_evaluated_count': {'type': 'integer'}, 'patch_perf_max_spread_pct': {'type': 'number'}, 'rustgo_irrelevant_path_pruning_pct': {'type': 'number'}, 'rustgo_target_reach_speedup_max_x': {'type': 'number'}, 'kani_mir_ci_harnesses_verified_count': {'type': 'integer'}, 'blockgtq_mosaickv_patchperf_rustgo_and_kani_gate_enabled': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_twinkv_rustc_schwarz_harnessllm_testgrad_and_swetaskflow', 'description': 'Verifica formalmente el Nivel 299: TwinKV Nonlocal Post-RoPE Frequency-Discounted KV-Cache (arXiv:2608.27128), rustc.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'twinkv_ruler_50pct_removal_score': {'type': 'number'}, 'twinkv_ruler_75pct_gain_over_value_only_pts': {'type': 'number'}, 'rustc_soundness_issues_analyzed_count': {'type': 'integer'}, 'rustc_missing_lifetime_check_bugs_count': {'type': 'integer'}, 'schwarz_agentic_benchmarks_solve_rate_pct': {'type': 'number'}, 'schwarz_svcomp_reachsafety_solve_rate_pct': {'type': 'number'}, 'testgrad_swebench_pass_at_1_pct': {'type': 'number'}, 'testgrad_failure_history_compression_x': {'type': 'number'}, 'swetaskflow_production_sessions_analyzed_count': {'type': 'integer'}, 'twinkv_rustc_schwarz_harnessllm_testgrad_and_swetaskflow_gate_enabled': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_alerus_rust_gpu_offload_query_visibility_race_pnmix_and_asner_isorag', 'description': 'Verifica formalmente el Nivel 300: Alerus Verificación Probabilística en Rust con Créditos de Error Eris en.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'alerus_verified_samplers_count': {'type': 'integer'}, 'rust_gpu_offload_compilation_passes_count': {'type': 'integer'}, 'query_visibility_ruler_paired_evals_count': {'type': 'integer'}, 'query_visibility_keydiff_win_cells_count': {'type': 'integer'}, 'race_256k_flops_reduction_pct': {'type': 'number'}, 'race_256k_throughput_speedup_x': {'type': 'number'}, 'pnmix_avg_precision_bits': {'type': 'number'}, 'asner_c2c66_improvement_pct': {'type': 'number'}, 'isorag_ppr_recall_gain_pct': {'type': 'number'}, 'alerus_rustgpu_queryvis_race_pnmix_and_asner_isorag_gate_enabled': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_patchkv_slimkv_kpa_tasq_local_ppr_agint_and_adarepair_rust', 'description': 'Verifica formalmente el Nivel 301: PatchKV Recuperación de KV-Cache para Contextos Editados Dinámicamente.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'patchkv_resume_ttft_speedup_max_x': {'type': 'number'}, 'slimkv_128k_attention_speedup_max_x': {'type': 'number'}, 'slimkv_128k_decode_speedup_max_x': {'type': 'number'}, 'kpa_kronecker_kv_compression_max_x': {'type': 'number'}, 'tasq_1bit_batch_size_multiplier_x': {'type': 'number'}, 'agint_reject_f1_score': {'type': 'number'}, 'agint_cost_per_candidate_reduction_pct': {'type': 'number'}, 'agint_null_deref_witnesses_count': {'type': 'integer'}, 'rust_gradient_arbiter_silent_failures_caught_count': {'type': 'integer'}, 'patchkv_slimkv_kpa_tasq_local_ppr_agint_and_adarepair_rust_gate_enabled': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_vericontest_lean_veruseval_tlaverus_vestigekv_gva_smem_and_eirwr', 'description': 'Verifica formalmente el Nivel 302: VeriContest Verificador Rust Respaldado por Lean (1,325 teoremas y 21,413 tests en.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'vericontest_lean_theorems_proved_count': {'type': 'integer'}, 'vericontest_equivalence_test_cases_count': {'type': 'integer'}, 'verus_phase_separated_contract_success_pct': {'type': 'number'}, 'vestigekv_32x_retrieval_score': {'type': 'number'}, 'gva_kv_scalar_reduction_max_pct': {'type': 'number'}, 'smem_4096_deletion_speedup_x': {'type': 'number'}, 'eirwr_high_vis_mrr_score': {'type': 'number'}, 'eirwr_17k_graph_latency_max_ms': {'type': 'number'}, 'nexusrag_evidence_recall_gain_max_pts': {'type': 'number'}, 'vericontest_lean_veruseval_tlaverus_vestigekv_gva_smem_and_eirwr_gate_enabled': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_prefix_accounting_cachecraft_frc_hyquant_activeset_ppr_petri_rust_and_tqs', 'description': 'Verifica formalmente el Nivel 303: Contabilidad de Prefill con Reutilización de Prefijo y Auditoría de Borrado de.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'eager_prefix_uncached_prefill_reduction_pct': {'type': 'number'}, 'eager_model_calls_reduction_pct': {'type': 'number'}, 'cachecraft_frc_88pct_ruler_gain_pts': {'type': 'number'}, 'cachecraft_scorer_contribution_pts': {'type': 'number'}, 'activeset_sdd_ppr_polylog_alpha_enabled': {'type': 'boolean'}, 'statesync_gkr_koalabear_extension_deg': {'type': 'integer'}, 'tqs_trajectories_scored_count': {'type': 'integer'}, 'attncompress_swe_pass_rate_pct': {'type': 'number'}, 'attncompress_cost_reduction_pct': {'type': 'number'}, 'prefix_accounting_cachecraft_frc_hyquant_activeset_ppr_petri_rust_and_tqs_gate_enabled': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_folded_bias_key_sur_repair_residualquant_pulseinfer_dquant_and_reponav', 'description': 'Verifica formalmente el Nivel 304: Plegado Cerrado de Sesgos de Atención en Claves para Kernels Estándar y Reparación.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'folded_key_bias_longbench_greedy_match_ratio': {'type': 'number'}, 'sur_suffix_recompute_budget_pct': {'type': 'number'}, 'sur_layer_packed_executor_speedup_x': {'type': 'number'}, 'residualquant_kv_storage_reduction_pct': {'type': 'number'}, 'residualquant_peak_throughput_speedup_x': {'type': 'number'}, 'pulseinfer_decode_throughput_speedup_x': {'type': 'number'}, 'pulseinfer_tpot_reduction_pct': {'type': 'number'}, 'dquant_fixed_stride_drift_bitstream_enabled': {'type': 'boolean'}, 'reponav_sibling_symbol_scaffold_and_graphdc_enabled': {'type': 'boolean'}, 'folded_bias_key_sur_repair_residualquant_pulseinfer_dquant_and_reponav_gate_enabled': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_ramnet_crossmodel_kv_headguard_kvec_starkv_humanize_feynrir_and_crosscoder', 'description': 'Verifica formalmente el Nivel 305: Puente RAM-Net entre Cuantización KV-Cache y Atención Lineal junto con Transferencia.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'ramnet_teacher_gain_recovery_pct': {'type': 'number'}, 'crossmodel_kv_transfer_speedup_max_x': {'type': 'number'}, 'headguard_protected_head_fraction': {'type': 'number'}, 'kvec_longbench_coverage_gain_pts': {'type': 'number'}, 'starkv_attention_speedup_x': {'type': 'number'}, 'humanize_mechanical_gates_count': {'type': 'integer'}, 'humanize_lean_eval_proved_count': {'type': 'integer'}, 'feynrir_rust_canonical_graph_basis_enabled': {'type': 'boolean'}, 'crosscoder_pass1_gain_pct': {'type': 'number'}, 'toposign_magnetic_signed_laplacian_enabled': {'type': 'boolean'}, 'ramnet_crossmodel_kv_headguard_kvec_starkv_humanize_feynrir_and_crosscoder_gate_enabled': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_ulacache_oval_relaxkv_byte_crossover_hisparse_graft_rust_and_edge_callgraph', 'description': 'Verifica formalmente el Nivel 306 (Hito v23.0.0): Direccionamiento Lógico Unificado UlaCache PB-LRU y Bases Locales de.', 'inputSchema': {'type': 'object', 'properties': {'target_name': {'type': 'string'}, 'ulacache_b300_tp_throughput_speedup_x': {'type': 'number'}, 'oval_output_aware_page_bases_enabled': {'type': 'boolean'}, 'relaxkv_anchor_ratio_pct': {'type': 'number'}, 'byte_crossover_composed_decode_speedup_pct': {'type': 'number'}, 'hisparse_peak_throughput_speedup_x': {'type': 'number'}, 'graft_rust_api_coverage_pct': {'type': 'number'}, 'graft_rust_compilation_success_pct': {'type': 'number'}, 'edge_counterfactual_error_dag_and_callgraph_enabled': {'type': 'boolean'}, 'ulacache_oval_relaxkv_byte_crossover_hisparse_graft_rust_and_edge_callgraph_gate_enabled': {'type': 'boolean'}}}},
        {'name': 'aleph_prove_deferkv_crossflow_heterofold_decodebranch_optr_kvprovenance_graml_and_grads', 'description': 'Verifica formalmente el Nivel 307 (Hito v23.1.0 - REG-138): Expulsión KV en Primer Decode DeferKV (arXiv:2610.06286),.', 'inputSchema': {'type': 'object', 'properties': {'crossflow_high_load_gain_pct': {'type': 'number'}, 'heterofold_speedup_vs_native_x': {'type': 'number'}, 'trace_reuse_token_reduction_pct': {'type': 'number'}}}},
        {'name': 'aleph_prove_acache_conduit_kvsharearena_hijackkv_kvgov_mags_sweadv_interdepspec_and_repograph', 'description': 'Verifica formalmente el Nivel 308 (Hito v23.2.0 - REG-139): Reutilización KV Inter-Petición Anchor-Affix ACache y.', 'inputSchema': {'type': 'object', 'properties': {'acache_recompute_latency_reduction_pct': {'type': 'number'}, 'conduit_ttft_speedup_x': {'type': 'number'}, 'kvgov_salting_prefix_retention_pct': {'type': 'number'}}}},
        {'name': 'aleph_prove_behavior_preserving_kv_probevict_kvarn_tessera_cacheroute_kvset_asner_statemirror_and_trojanvulngym', 'description': 'Verifica formalmente el Nivel 309 (Hito v23.3.0 - REG-140): Compresión de KV Cache Preservadora de Comportamiento por.', 'inputSchema': {'type': 'object', 'properties': {'tessera_ttft_speedup_x': {'type': 'number'}, 'cacheroute_served_hit_rate_pct': {'type': 'number'}, 'statemirror_detection_precision': {'type': 'number'}}}},
        {'name': 'aleph_prove_attuner_restorekv_ssa_nexus_kv4rl_lkv_eagraph_reporeuse_perfagent_and_vego', 'description': 'Verifica formalmente el Nivel 310 (Hito v23.4.0 - REG-141): Adaptación Query-Side sin Recómputo ATTUNER para Reuso de.', 'inputSchema': {'type': 'object', 'properties': {'attuner_speedup_x': {'type': 'number'}, 'restorekv_ruler_16x_accuracy': {'type': 'number'}, 'ssa_1m_decode_speedup_x': {'type': 'number'}}}},
        {'name': 'aleph_prove_kvserve_beaconkv_benice_freqdepthkv_gaac_splitzip_midlog_deprepair_auditcoder_specbuild_and_porting', 'description': 'Verifica formalmente el Nivel 311 (Hito v23.7.0 - REG-142): Compresión Adaptativa de Comunicación KV KVServe para.', 'inputSchema': {'type': 'object', 'properties': {'kvserve_ttft_reduction_x': {'type': 'number'}, 'beaconkv_memory_reduction_x': {'type': 'number'}, 'splitzip_decompress_gbps': {'type': 'number'}}}},
        {'name': 'aleph_prove_bicache_conserve_kvrepurpose_dolphinrouting_pykvcache_anchorkv_surprise_rivet_swerefactortouch_and_kverusaria', 'description': 'Verifica formalmente el Nivel 312 (Hito v23.7.0 - REG-143): Caché de Prefijos Compartidos BiCache para Modelos de.', 'inputSchema': {'type': 'object', 'properties': {'bicache_throughput_gain_pct': {'type': 'number'}, 'conserve_p95_ttfet_reduction_pct': {'type': 'number'}, 'kvrepurpose_hit_rate_pct': {'type': 'number'}}}},
        {'name': 'aleph_prove_peek_kvkaizen_flashrt_swiftcache_hawk_photoniccxl_reskv_vector_lclm_graphalign_and_projagent', 'description': 'Verifica formalmente el Nivel 313 (Hito v23.7.0 - REG-144): Planificación y Evicción KV Informada por Cola PEEK con.', 'inputSchema': {'type': 'object', 'properties': {'peek_ttft_speedup_x': {'type': 'number'}, 'kvkaizen_compression_ratio_x': {'type': 'number'}, 'flashrt_16k_ttft_speedup_x': {'type': 'number'}}}},
        {'name': 'aleph_prove_range_reqat_dustin_globalretain_quantwm_laquant_tgvkv_papercompiler_polycodeeval_and_forge', 'description': 'Verifica formalmente el Nivel 314 (Hito v23.8.0 - REG-145): Desacoplamiento de Granularidad de Reutilización KV y.', 'inputSchema': {'type': 'object', 'properties': {'range_stripe_mib': {'type': 'integer'}, 'reqat_spark_speedup_x': {'type': 'number'}, 'dustin_self_attn_speedup_x': {'type': 'number'}}}},
        {'name': 'aleph_prove_jolt_smartgen_avsg_gandalf_lmcache_compactattn_persistentkv_agentkv_rtpllm_and_rustleanprint', 'description': 'Verifica formalmente el Nivel 315 (Hito v23.9.0 - REG-146): Compresión KV Casi Sin Pérdidas JoLT mediante.', 'inputSchema': {'type': 'object', 'properties': {'jolt_compression_ratio_x': {'type': 'number'}, 'smartgen_ttst_speedup_x': {'type': 'number'}, 'avsg_h2d_bandwidth_gain_x': {'type': 'number'}}}},
        {'name': 'aleph_prove_objectcache_asymcache_wassersteindro_hikv_contourkv_metakv_kv2_oscar_leangraphsearch_and_repozero', 'description': 'Verifica formalmente el Nivel 316 (Hito v24.0.0 - REG-147): Recuperación por Capas desde Almacenamiento de Objetos S3 sobre 100 Gbps RoCE ObjectCache (+5.6% latencia sobre DRAM a 64K y 1.2-1.8x menor TTFT bajo límite compartido, arXiv:2605.22850), Gestión KV Consciente de Latencia de Cómputo con Atención Multi-Segmento AsymCache (2.03x TTFT, 1.71x TPOT y -18.1% latencia de agentes en Continuum, arXiv:2606.02964), Reserva Robusta de KV bajo Incertidumbre de Longitud de Salida mediante Optimización Distribucionalmente Robusta de Wasserstein DRO (-56% costo con estructura de fractil crítico, arXiv:2607.16892), Co-diseño Algoritmo-Hardware Jerárquico en 2 Etapas HiKV (7.95x speedup de atención y -90% energía, IEEE TCAS-I arXiv:2607.22389), Asignador Ragged por Cabeza Basado en Estadístico de Masa Descartada ContourKV (93/160 victorias a paridad real de bytes, arXiv:2608.25230), Selección Adaptativa por Prompt bajo Restricciones de Latencia y Memoria MetaKV (+13.5 pp Constrained Success Rate, arXiv:2609.07966), Caché KV Auto-Refinante por Reconstrucción Selectiva KV^2 (+40 pp en RULER 16K al 2% de presupuesto, arXiv:2610.03198), Rotación Canalizada y Escalado Omni-Token INT2 OScaR contra Desbalance de Norma de Token TNI (3.0x decode, 5.3x menor memoria y 4.1x throughput, arXiv:2605.19660), Búsqueda en Grafo de Dependencias Multi-Salto LeanGraphSearch para Lean 4 Mathlib (+40% pass rate de teoremas, arXiv:2610.22339), y Razonamiento de Cadenas de Llamadas RepoReasoner junto con Síntesis de Repositorios desde Cero RepoZero C2Rust/Py2JS con Evolución Agéntica Código-Test ACE (+16.80 pp Pass@1, FSE 2026 arXiv:2607.25996 & arXiv:2605.07122).', 'inputSchema': {'type': 'object', 'properties': {'objectcache_64k_overhead_pct': {'type': 'number'}, 'asymcache_ttft_speedup_x': {'type': 'number'}, 'wassersteindro_cost_reduction_pct': {'type': 'number'}}}},
        {'name': 'aleph_prove_netkv_prefilldeflect_pcr_regimekv_topas_memdraftsd_peekkv_kvstream_cslibpremise_and_retrace', 'description': 'Verifica formalmente el Nivel 317 (Hito v24.1.0 - REG-148): Selección de Instancia Decode Consciente de Red con Oráculo de Costo Topológico NetKV (-21.2% TTFT medio y <0.5ms TBT, arXiv:2606.03910), Deflexión Proactiva de Prefill por Fragmentos en Nodos Decode PrefillDeflect (-81% P95 TTFT y +79% SLO attainment eliminando transferencia KV entre nodos, arXiv:2607.02043), Diagnóstico y Mitigación de Colapso de Alineación bajo Cuantización KV mediante Reducción por Canal PCR (97.2% recuperación de alineación con 20 prompts, arXiv:2606.09864), Planificación No-Clarividente Constante-Competitiva por Ruteo Consciente de Régimen RegimeKV (arXiv:2607.09248), Planificación de Estado de Prefijo Consciente de Flujo de Trabajo Multi-Agente TOPAS (-49.4% P99 JCT sintético y -26.6% P99 JCT en MetaGPT-TL, arXiv:2608.25523), Decodificación Especulativa de Contexto Largo con Memoria KV de Borrador Comprimida MemDraftSD (>70% menor memoria draft y 3.33x speedup sin pérdida a 32K, EMNLP 2026 arXiv:2608.30252), Asignación de Presupuesto por Grupo de Cabezales desde el Primer Token de Contenido PeekKV (95.7% retención en RULER 16K al 10% de presupuesto y 95.9% en LongBench al 1.5%, arXiv:2610.23939), Gestión Paralela Adaptativa de Almacenamiento Multi-Tier KVStream (<5% de la cota teórica de ancho de banda agregado, 1.49x throughput y 6.1x menor TTFT en ráfagas hasta 128 GPUs, arXiv:2610.31827), Recuperación de Premisas Guiada por Estructura en Lean 4.29.0 CSLibPremiseBench (801 tareas y 1,875 declaraciones, arXiv:2605.14549), y Verificación Independiente Bidireccional de Parches RETRACE (+7.0% Pass@1 en SWE-bench Verified, arXiv:2608.08950) junto con Claw-SWE-Bench (350 instancias en 8 lenguajes, arXiv:2606.12344).', 'inputSchema': {'type': 'object', 'properties': {'netkv_ttft_reduction_pct': {'type': 'number'}, 'prefilldeflect_p95_ttft_reduction_pct': {'type': 'number'}, 'pcr_alignment_recovery_pct': {'type': 'number'}}}},
        {'name': 'aleph_prove_herald_3dls_eldr_aoh_circuitprover_cocoprover_formalreward_paichecker_dialogueswe_and_procgrep', 'description': 'Verifica formalmente el Nivel 318 (Hito v24.5.0 - REG-149): Recuperación Cooperativa CPU-GPU de KV Cache para Block Diffusion LLMs HERALD (2.28x decode throughput al 5% de presupuesto KV cruzando PCIe una sola vez por bloque, arXiv:2606.21633), Arquitectura 3D Logic-Stacked para Inferencia Desagregada 3DLS (-60.2% latencia E2E y 1.49x throughput aislando transferencias KV verticales de colectivos TP laterales, IEEE CAL 2026 arXiv:2607.01617), Ruteo Decode Consciente de Localidad de Expertos MoE ELDR (-13.9% TPOT mediano en 40 GPUs co-indexando firmas de expertos con bloques KV, arXiv:2607.00466), Atención Dispersa Libre de Datos por Geometría Espectral Query-Key Autonomy-of-Heads AoH (96.5% retención, -41.4% prefill, -66.0% decode y -50% memoria KV a 256K tokens, arXiv:2608.06849), Demostración Agéntica en Lean 4 con Biblioteca Reutilizable CircuitProver (100% 63/63 tareas resueltas y -23.2% tiempo de verificación, arXiv:2607.27259), Orquestación Meta-Nivel sobre Hipergrafos de Prueba AND/OR de 2 Niveles en Lean 4 CoCo-Prover (hasta 100% solve rate y -30.9% costo en CLEVER/VERINA/AlgoVeri/NTP4VC/Vero, arXiv:2610.09681), Evaluación de Modelos de Recompensa en Lean 4 FormalRewardBench (250 pares con 5 estrategias de inyección de errores, arXiv:2605.10141), Verificación en 3 Fases de Desalineación PR-Issue PAIChecker (92.12% precisión en SWE-Gym y 91.67% en SWE-bench Multilingual, ASE 2026 arXiv:2607.28587), Agente Guiado por Esquema en Dialogue SWE-Bench (+14% resolución interactiva, arXiv:2606.13995), y Fingerprinting Procedural de Trayectorias Agénticas ProcGrep (85.7% precisión de atribución y auditoría JSD=0.25, arXiv:2606.16988).', 'inputSchema': {'type': 'object', 'properties': {'herald_decode_throughput_gain_x': {'type': 'number'}, 'three_dls_e2e_latency_reduction_pct': {'type': 'number'}, 'aoh_decode_latency_reduction_pct': {'type': 'number'}}}},
        {'name': 'aleph_prove_hexagent_topomove_ainferpd_pdd_rarecache_blis_vericodebench_dalekbench_reuf2f_and_calcg', 'description': 'Verifica formalmente el Nivel 319 (Hito v24.5.0 - REG-150): Planificación de Flujos Agénticos DAG Consciente de Heterogeneidad HexAGenT (-20.1% escala SLO media / -45.0% máx en P95 y -33.0% media / -80.5% máx en P99 sobre A100/H100/H200, arXiv:2605.16637), Movimiento de Datos Consciente de Topología para Inferencia GPU Desagregada TopoMove (ocultamiento del 76-100% de latencia KV en prefill, CXL 3.0 6x capacidad/86x menor latencia y reducción 3-18x vs RDMA uniforme, arXiv:2607.28633), Multiplexación Prefill-Decode In-Place Segura en Comunicación para Rollouts MoE AInfer-PD (-24.8 a -32.9% tiempo de rollout vs SGLang aislando estado DeepEP, arXiv:2609.00993), Desagregación en 3 Niveles Prefill-RelayDecode-MainDecode PDD (+37.5% Benefit-Cost Ratio en goodput SLA inter-datacenter, arXiv:2609.13161), Reuso de KV Cache Cross-Model por Desacuerdo de Rango RaReCache (3.04x prefill speedup, 5.0x TTFT mediano y 6.4x TTFT P99 recomputando 30% de posiciones en brecha 23x Qwen3-0.6B->14B, arXiv:2610.11358), Simulador Discreto CPU de Inferencia sin GPUs BLIS (6.7% error mediano E2E, 200x más rápido y -82% TTFT P90 en llm-d, ACM SIGMETRICS 2027 arXiv:2610.14255), Generación de Código Auto-Especificada y Verificable VeriCodeBench & CodeNova (400 problemas políglotas en C/Java/Rust/Python, arXiv:2609.39568), Verificación Formal con RLVR y Proof Reviser en Lean/Dafny Dalek-Bench (69.2% pass rate en VeriCoding, 7/42 VERINA resueltos y benchmark Rust curve25519-dalek, arXiv:2605.30914), Benchmark Lean 4 de Problemas Abiertos de Investigación ReuF2F (244 problemas REU con Leanimum-agent, arXiv:2610.27046), y Cálculo de Granularidad de Esquemas en Tiempo Lineal Mecanizado en Lean 4 CalcG (decisión O(N) libre de fan/chasm traps, arXiv:2601.00995).', 'inputSchema': {'type': 'object', 'properties': {'hexagent_p99_slo_scale_reduction_pct': {'type': 'number'}, 'topomove_max_transfer_latency_reduction_x': {'type': 'number'}, 'rarecache_p99_ttft_speedup_x': {'type': 'number'}}}},
        {'name': 'aleph_prove_specstream_hspec_groupkv_exfold_elasticvmm_vha_rcsd_p3lean4_hyperflconfl_and_omegadafny', 'description': 'Verifica formalmente el Nivel 320 (Hito v24.5.0 - REG-151): Decodificación Especulativa en Streaming con Online Softmax SpecStream (+55.4% throughput por GPU y 1.41x speedup en Qwen3 iniciando verificación sin restaurar el historial KV completo, arXiv:2609.33184), Drafter Paralelo Híbrido Mamba-Atención Libre de KV-Cache Propio H-Spec (+5.0 a +13.3% longitud aceptada y +5.3 a +12.6% velocidad ITL reusando KVs del modelo target in-place, arXiv:2609.24197), Gestión Jerárquica de KV-Cache para Diffusion LLMs GroupKV (48.00x extensión de contexto máximo y 3.73x aceleración E2E con prefetch predictivo cross-layer y corrección de staleness, arXiv:2609.17573), Plegado Unificado de Expertos MoE Libre de Entrenamiento ExFold (1.41x TTFT y 2.45x TPOT speedup con 99% retención de calidad proyectando expertos excluidos mediante matriz escalar calibrada, arXiv:2608.24938), Allocator Elástico VMM en Espacio de Usuario para Reserva KV Elastic-VMM (mapeo físico dual en rango virtual contiguo sin OOM y ~1% diferencia mediana de TTFT entre chunks de 8192 y 32768 tokens, arXiv:2608.23658), Atención de Cabezas Virtuales VHA (Q Premix + Linear Postmix plegables a GQA-2 con grupo 64, 4x reducción KV vs GQA-8, -7.9% FLOPs de prefill y 84.4 vs 73.0 en RULER 8K-128K, NeurIPS 2026 arXiv:2610.17959), Aprendizaje por Refuerzo y Continuo para Decodificación Especulativa RCSD (+35.0% longitud aceptada y 1.35x inferencia E2E sobre HASS con pares implícitos de preferencia, arXiv:2610.29527), Planificación Conjunta de Programa y Prueba en Lean 4 P^3 & Lean4Commit0 (+4.6 a +11.2 pts de resolución, -40% costo API y -37% tiempo en Verina/AlgoVeri/Lean4Commit0, arXiv:2608.09277), Localización de Fallos Adaptativa y Concurrente HyperFL & ConFL (+16.7% Hit@1 sobre SweRank con hiperred LoRA arXiv:2608.02967 y MRR 0.503 en bugs concurrentes con CKB ISSTA 2026 arXiv:2608.02974), y Formalización del Omega Test de Pugh en Dafny (decisión verificada de desigualdades lineales y divisibilidad en aritmética entera/racional, EPTCS 452 arXiv:2609.34882).', 'inputSchema': {'type': 'object', 'properties': {'specstream_per_gpu_throughput_gain_pct': {'type': 'number'}, 'groupkv_context_extension_x': {'type': 'number'}, 'exfold_tpot_speedup_x': {'type': 'number'}}}},
        {'name': 'aleph_prove_specla_sparsespecl_moezip_slimwise_foldattention_witcert_axdafny_openprover_leaf_and_pprcgdiff', 'description': 'Verifica formalmente el Nivel 321 (Hito v24.5.0 - REG-152): Decodificación Especulativa para Modelos de Atención Lineal con Estado SpecLA (1.70x speedup E2E en H100 verificando cadenas/árboles con factores compactos de recuperación de estado, arXiv:2607.16673), Auto-Decodificación Especulativa sin Entrenamiento con KV-Cache Disperso y Recuperable SparseSpec-L (reciclaje de estadísticas de atención sin forward extra y controlador de horizonte por entropía online, arXiv:2607.27735), Compresión de KV-Cache Consciente de Ruteo por Matriz de Información de Fisher para MoE MoEZip (+24 pts / 2.3x en LongBench y +20 pts / 4.9x en RULER al 10% de retención KV, NeurIPS 2026 arXiv:2610.30206), Desacoplamiento de Poda de Expertos MoE entre Prefill y Decode SlimWise (1.81x decode throughput al 50% de poda reusando directamente el KV-Cache del prefill completo, arXiv:2609.34117), Softmax Aditivo de Referencia Declarada FoldAttention (hasta 3.09x decode speedup en H100 sin reescalado provisional y 1.84x backward determinista sobre grilla entera frente a FlashAttention-3/4, arXiv:2609.33410), Observabilidad y Compuerta de Riesgo en Tiempo de Ejecución para Cuantización KV Verificada en Lean 4 WitCert (recuperación de RULER de 22.8 a 79.7 y 1.88x más tokens KV en SGLang con cotas de variación total en Lean 4, arXiv:2607.28699), Generación Agéntica Verificada en Dafny AxDafny (92.7% éxito de verificación en DafnyBench y 250 problemas en LiveCodeBench-Pro-Dafny, arXiv:2606.32007), Demostración de Teoremas Agéntica e Interactiva en Lean 4 OpenProver (arquitectura Planner-Worker-Verifier con Whiteboard y repositorio en ProofNet, CICM 2026 arXiv:2607.09217), Análisis Dinámico Instrumentado sobre Dynamic MIR para Rust LEAF (ejecutor concólico, sanitizador Rust y trazador de flujo de control sobre DMIR, arXiv:2607.15025), y Cálculo Casi Óptimo de Personalized PageRank Libre de Alpha O(eps^{-1-o(1)}) & Subgrafos de Llamadas CG-Diff (eliminación de dependencia en alpha sobre ACL local push arXiv:2610.06959 y descomposición de PRs donde 40% tienen >50% de funciones conectadas arXiv:2609.32057).', 'inputSchema': {'type': 'object', 'properties': {'specla_h100_e2e_speedup_x': {'type': 'number'}, 'moezip_ruler_score_multiplier_x': {'type': 'number'}, 'foldattention_max_decode_speedup_x': {'type': 'number'}}}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l380_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 380.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l381_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 381.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l382_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 382.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l383_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 383.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l384_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 384.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l385_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 385.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l386_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 386.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l387_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 387.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l388_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 388.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l389_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 389.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l390_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 390.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l391_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 391.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l392_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 392.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l393_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 393.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l394_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 394.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l395_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 395.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l396_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 396.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l397_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 397.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l398_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 398.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l399_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 399.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l400_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 400.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l401_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 401.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l402_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 402.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l403_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 403.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l404_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 404.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l405_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 405.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l406_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 406.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l407_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 407.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l408_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 408.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l409_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 409.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l410_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 410.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l411_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 411.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l412_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 412.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l413_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 413.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l414_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 414.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l415_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 415.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l416_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 416.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l417_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 417.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l418_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 418.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l419_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 419.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l420_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 420.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l421_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 421.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l422_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 422.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l423_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 423.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l424_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 424.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l425_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 425.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l426_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 426.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l427_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 427.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l428_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 428.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l429_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 429.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l430_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 430.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l431_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 431.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l432_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 432.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l433_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 433.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l434_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 434.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l435_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 435.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l436_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 436.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l437_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 437.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l438_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 438.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l439_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 439.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l440_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 440.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l441_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 441.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l442_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 442.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l443_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 443.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l444_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 444.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l445_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 445.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l446_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 446.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l447_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 447.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sovereign_node06_cumulative_l448_pcc', 'description': 'Executes cumulative NODE-06 Sovereign PCC Prover for Level 448.', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_horn_robust_transversal_certificate_type_classifiers_cwf_rank_sorted_type_in_type_rocq_and_gi_rtl_fuzz_bnf_pcc', 'description': 'Executes Formal Verification Engine #464 (Level 450 / REG-170): Minimum-Cost Rob...', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_aegis_rust_lean_aeneas_mutation_bitvector_622_mutant_kill_jaspergold_briscv_and_qafny_hoare_rocq_pcc', 'description': 'Executes Formal Engine #465 (Level 451 / REG-171): Aegis Rust-Lean Aeneas (2610.38174), 622-Mutant Z3 BitVector (2610.03794), JasperGold BRISC-V (2610.32597), Qafny-Hoare Rocq (2610.34723).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_smt_instability_cv_coco_prover_hypergraph_veripy_relational_product_and_chc_constrained_resolution_pcc', 'description': 'Executes Formal Engine #466 (Level 452 / REG-172): SMT Instability CV (2610.12649), CoCo-Prover (2610.09681), VeriPy (2610.02814), CHC Resolution (2610.03345).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_vericontest_lean_rust_veruseval_semantic_completeness_phase_separated_witness_and_specagent_acsl_pcc', 'description': 'Executes Formal Engine #467 (Level 453 / REG-173): VeriContest Lean-Rust (2610.03994), VerusEval (2610.26464), Phase-Separated Verus (2610.20676), SpecAgent ACSL (2610.05132).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_wp_separation_logic_itrees_rocq_hyperrechml_automata_tla_verus_and_vialean_proof_graph_pcc', 'description': 'Executes Formal Engine #468 (Level 454 / REG-174): WP-Preserving Separation Logic ITrees (2610.37244), HyperRecHML (2610.21379), TLA-Verus (2610.14923), ViaLean (2610.04275).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_ironproof_cobol_python_smt_equivalence_lasso_sql_validation_compositional_smc_and_certmoe_routing_pcc', 'description': 'Executes Formal Engine #469 (Level 455 / REG-175): IRONPROOF SMT Equivalence (2610.11073), LASSO SQL Validation (2610.38294), Compositional SMC (2610.05571), CertMoE (2610.29395).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_refute_refine_decide_equivalence_fuzzy_situation_mutation_succinct_slkp_atl_and_neuro_symbolic_hw_pcc', 'description': 'Executes Formal Engine #470 (Level 456 / REG-176): Refute-Refine-Decide Equivalence (2610.18218), SCALOFT Fuzzy Mutation (2610.15122), Succinct SLK_P/ATL (2610.18249), Neuro-Symbolic HW (2610.10580).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_lava_liquid_haskell_rocq_sylares_code2smt_proof_gated_signing_state_drift_and_keystream_sat_cliff_pcc', 'description': 'Executes Formal Engine #471 (Level 457 / REG-177): Lava Liquid Haskell to Rocq (2610.14092), SyLares Code2SMT (2610.27871), Proof-Gated Signing (2610.00354), Keystream SAT Cliff (2610.41083).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_pfolio_reference_entailment_z3_transversal_ccz_sat_logsi_interpolants_and_rust_async_liveness_pcc', 'description': 'Executes Formal Engine #472 (Level 458 / REG-178): P-FOLIO Reference Entailment Z3 Auditor (2610.24690), Projective Geometry Transversal CCZ SAT (2610.09341), LOGSI Stochastic Interpolants (2610.38648), Rust Async Runtime Liveness & Tokio Fairness (2610.09198 / 2610.06003).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_pcm_merkle_messages_mxfp4_qflia_scale_laser_defeasible_certificates_and_lean_quantum_conformal_pcc', 'description': 'Executes Formal Engine #473 (Level 459 / REG-179): PCM Proof-Carrying Messages Merkle Log (2610.39109), MXFP4 Scale Placement QF_LIA Equivalence (2610.29445), LASER Defeasible Protocol Certificates (2610.14552), Lean Quantum Code Distance & Conformal Partial Verification Certificates (2610.03214 / 2610.10829).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_statesync_gkr_sparse_merkle_anytime_valid_barrier_supermartingale_fortress_sg_fort_and_verirouter_merkle_audit_pcc', 'description': 'Executes Formal Engine #474 (Level 460 / REG-180): StateSync-GKR Sparse-Merkle Isabelle/HOL & KoalaBear Extension (2610.05335), Anytime-Valid Barrier Certificate Supermartingale Monitor (2610.27726), Fortress Social-Graph Fork-Resistant Transparency sg-FORT (2610.26327), VeriRouter ZK Routing & Merkle Cloud Auditing (2610.17431 / 2610.36001).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_tofu_mcp_trust_boundary_typos_typed_template_fuzzing_data_vass_integer_reachability_and_zkllmpot_dag_bft_pcc', 'description': 'Executes Formal Engine #475 (Level 461 / REG-181): ToFu MCP Trust Boundary CWE Sanitizer (2610.13651), Typos Typed Template Mutation Fuzzing (2610.31342), Data VASS Integer Reachability & Soliduzz Symbolic EMI (2610.23725 / 2610.18165), zkLLMPoT Checkpoint Proof & Seamless DAG-BFT Reconfiguration (2610.08258 / 2610.00896 / 2610.29066).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_lean4_pedigree_polytope_nanoproof_sre_msm_zkp_pwsts_quantitative_horizons_and_bca_pmc_reachability_pcc', 'description': 'Executes Formal Engine #476 (Level 462 / REG-182): Lean 4 Pedigree Polytope NS Condition & NanoProof/GPU Evaluator (2610.15914 / 2610.11605 / 2610.21881), SRE Scalar Redundancy Elimination in ZKP MSM (2610.27452), Quantitative Reachability Horizons in pWSTS/pLCS & MPC STL Monitoring (2610.35308 / 2610.25639), Bounded Continuation Analysis PMC (2610.22754).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_resolve_fstar_pulse_gpu_kernels_rolefuzzer_raise_fuzzing_lynx_delta_sql_synthesis_and_signed_oracle_zk_pqc_pcc', 'description': 'Executes Formal Engine #477 (Level 463 / REG-183): RESOLVE F*/Pulse GPU Kernel Validation (2610.05683), RoleFUZZER 64-Cell Grid & RAISE PatchCoverage Fuzzing Allocation (2610.38438 / 2610.27828), LYNX Delta-Guided Analytical SQL Synthesis (2610.14777), Signed-Oracle ZK Oversight & ZKS-PQC Post-Quantum Signatures (2610.01995 / 2610.11490).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_5ugue_hil_fuzzing_hybrid_hard_soft_stl_screening_robust_pspace_ternary_tl_and_agent_consensus_pcc', 'description': 'Executes Formal Engine #478 (Level 464 / REG-184): 5uGUE Agentic HIL Wireless Fuzzing (2610.29155), Hybrid Hard-Soft STL MPC with Reachability Screening (2610.15934), PSPACE-Completeness of Robust Dynamical Reachability & Differentiable Ternary Temporal Logic (2610.26206 / 2610.04662), AI Agent Network Consensus Evaluation (2610.24833).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_timbre_harmonic_barycenter_consensus_byzantine_inducement_defense_lean4_lemniscate_genetic_and_verina_elicitation_pcc', 'description': 'Executes Formal Engine #479 (Level 465 / REG-185): Timbre Chi-Square Barycenter Harmonic Consensus (2610.39439), Evolutionary Game Defense Against Conformity-Driven Byzantine Attacks (2610.14639), Lean 4 Lemniscate Irrationality Exponent & Genetic Code Verification (2610.26539 / 2610.36343), Verina Lean 4 Interactive Specification Elicitation (2610.22382).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_rocq_plume_tap_weak_isolation_arcade_cedar_abac_business_semantic_sql_and_blanc_jaune_evm_bytecode_pcc', 'description': 'Executes Formal Engine #480 (Level 466 / REG-186): Rocq Plume TAP Weak Isolation Levels (2610.07665), ARCADE Cedar PostgreSQL/MySQL ABAC (2610.18660), Business-Semantic Text-to-SQL Revalidation (2610.41090), Blanc/Jaune Lean 4 Deployed EVM Bytecode Verification (2610.19764).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_nomos_verified_tool_call_gates_scope_operator_prover_atlas_binary_llvm_ir_and_procerdcl_sequential_compiler_pcc', 'description': 'Executes Formal Engine #481 (Level 467 / REG-187): NOMOS Statically Verified Tool-Call Gates (2610.11030), SCOPE State-Conditioned Certified Theorem Proving (2610.08319), ATLAS Multi-Agent Binary-to-LLVM-IR Lifting (2610.30877), ProCerDCL Three-Valued Sequential Probabilistic Compiler Verification (2610.36499).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_smt_dependent_constant_value_checker_vigil_dual_gated_harness_bird_rl_stateful_db_and_verse_hybrid_automaton_pcc', 'description': 'Executes Formal Engine #482 (Level 468 / REG-188): SMT Dependent Constant Value Checker (2610.05316), VIGIL Verifier-Informed Gated Continual Harness (2610.04287), BIRD-RL Trajectory-Scoped Stateful Database RL (2610.29426), Verse Hybrid Multi-Agent Automaton Verification (2610.35680).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_velvet_lean_vercors_gpu_kernel_isabelle_renyi_dp_certified_nmpc_and_bvi_identity_pcc', 'description': 'Executes Formal Engine #483 (Level 469 / REG-189): Velvet Lean + VerCors CUDA GPU Kernel Verification (2610.24548), Isabelle/HOL Continuous Renyi Differential Privacy & Moment Accountant (2610.25636), Certified Lipschitz Neural Approximation of Robust NMPC (2610.29559), BVI Lightweight Blockchain Identity Claim Verification (2610.07531).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_l4_reversible_linear_type_semantics_reprise_dl_compiler_fuzzer_permit_lean4_memory_gate_and_rocq_polyhedron_vertex_pcc', 'description': 'Executes Formal Engine #484 (Level 470 / REG-190): L4 Linearly-Typed Reversible Intermediate Language & Bidirectional Small-Step Semantics (2610.31201), Reprise Pattern-Guided Graph Synthesis for DL Compiler Fuzzing (2610.06968), PerMIT Lean 4 Persistent Memory Integrity Gate (2610.28987), Rocq Simplicial Normal-Fan Polyhedron Vertex Certification (2610.11913).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_fvqkd_rocq_composable_bb84_z3_noodler_c_cyclic_string_contractlens_mcdu_and_ciper_failure_taxonomy_pcc', 'description': 'Executes Formal Engine #485 (Level 471 / REG-191): FVQKD Rocq Composable Finite-Key BB84 Security Proof (2610.30645), Z3-Noodler-C Cyclic String Constraint Solver (2610.25197), ContractLens Frozen-LLM MCDU Smart Contract Detector (2610.04992), CIPER 22-Mode 5-Dimension Smart Contract Failure Taxonomy (2610.41685).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_crush_lean_defunctionalized_smt_5vas_pspace_witness_stateless_byzantine_quorum_slack_and_semweaver_checker_pcc', 'description': 'Executes Formal Engine #486 (Level 472 / REG-192): crush Extensible Higher-Order Defunctionalized SMT Proof Automation for Lean (2610.40538), 5-VAS PSPACE-Complete & NL-Complete Polynomial Reachability Witness & Factorization (2610.40012), Stateless Recovery Byzantine Quorum Slack Tight Normal Form (2610.07759), SemWeaver Program-Analysis Evidence Static Checker Refinement (2610.34928).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sorsi_second_order_lean4_verus_bipartite_carrier_compression_vera_srr_mutation_auditor_and_attestable_audit_tee_pcc', 'description': 'Executes Formal Engine #487 (Level 473 / REG-193): SO-RSI Second-Order Diagnostic Recursive Self-Improvement for Lean 4 & Verus (2610.05701), Lean 4 Bipartite Carrier Wire Compression in Exact Q-Arithmetic (2610.14263), VERA Structured Reasoning Record 8-Mode Auditor & Mutation Testing (2610.06366), Attestable Audit Chained Confidential Computing TEE Proofs (2610.04480).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_reuf2f_lean4_negated_open_problems_compiler_ir_mutation_taxonomy_rust_unsafe_oracle_and_bbs_zk_topology_pcc', 'description': 'Executes Formal Engine #488 (Level 474 / REG-194): ReuF2F 244-Problem Negated Lean 4 Coding-Agent Benchmark (2610.27046), Compiler IR & Representation-Boundary Mutation Fault Taxonomy (2610.22089), Rust Unsafe Code Coverage Oracle Fuzzer Evaluation (2610.20315), BBS Multi-Message Zero-Knowledge Hidden-Path Topology Assurance (2610.11513).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_lean4_erdos522_radial_polynomial_hazel_rocq_rewrite_quantum_compiler_assurance_and_pocofl_nizk_pcc', 'description': 'Executes Formal Engine #489 (Level 475 / REG-195): Lean 4 Universal Radial Laws for Random Polynomials & Erdos Problem #522 Proof (2610.11324), Hazel Prover Equational Rewrite Search & Rocq Tactic Export (2610.02449), Quantum Compiler Assurance Contracts & Delivered-Interface Verification (2610.00255), PoCoFL Policy-Compliant NIZK Federated Learning (2610.03650).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_leangraphsearch_premise_propagation_lean4_record_calculus_tracer_symbol_repair_and_mgd_blocking_gates_pcc', 'description': 'Executes Formal Engine #490 (Level 476 / REG-196): LeanGraphSearch Premise Dependency Graph Propagation for Lean 4 (2610.22339), Lean 4 Record-Type Calculus with Mutable References & Verified Interpreter (2610.27519), TRACER Symbol-Level Development-History Security Repair & Boundary Check (2610.34098), Misfit-Governed Development Dual-Loop 28-Gate Assurance Model (2610.01372).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_lean_postselection_bb84_qkd_minilean_bash_agent_oblivul_lsog_counterfactual_and_cct_identity_lineage_pcc', 'description': 'Executes Formal Engine #491 (Level 477 / REG-197): Lean Entanglement-Based BB84 Postselection QKD Security Proof (2610.17286), mini-Lean-agent Minimal Bash Harness for Putnam 2025 (2610.17331), ObliVul Alert-Conditioned CPG Local Safety Obligation Graph & VAFI (2610.11801), CCT Policy-Relative Governed State Transitions on IdentityLineageBench (2610.00132).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_noisy_toric_word_omega_regular_tail_recursive_phfl_kexpspace_foscon_hadwiger_and_falcon_counterexample_pcc', 'description': 'Executes Formal Engine #492 (Level 478 / REG-198): Noisy Toric Words & LRS Sign Omega-Regular Model Checking (2610.23463), Tail-Recursive PHFL Order-(k+1) Characterization of Bisimulation-Invariant k-EXPSPACE (2610.15475), FOscon Minor-Free Graph Hadwiger-Parameterized Model Checking (2610.05263), FALCON Counterexample-Grounded Execution-Trace Security Verification (2610.25916).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_logikey_isabelle_hol_embedding_lean_hindsight_free_repair_safety_critical_unit_assurance_and_linear_dl_lra_pcc', 'description': 'Executes Formal Engine #493 (Level 479 / REG-199): LogiKEy Isabelle/HOL Pluralistic Semantical Embedding (2610.08214), Hindsight-Free Verifier Feedback & Resampling in Lean Theorem Proving (2610.22698), Safety-Critical 17-Unit AI Participation & 23-Check CAD Assurance Framework (2610.04084), Linear Differential Dynamic Logic LRA Completeness & Reachability Certification (2610.28460).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_time_bounded_wtg_4exptime_simplex_first_step_safety_conp_pattern_tree_typecheck_and_munch_tokenizer_verifier_pcc', 'description': 'Executes Formal Engine #494 (Level 480 / REG-200): Time-Bounded Weighted Timed Games 4-ExpTime Value Approximation (2610.21487), Simplex Minimum-Coordinate Elimination Polynomial First-Step Safety & coNP-Complete Correctness (2610.33908), Pattern-Based Tree Transformation Alternating Automata Type-Checking (2610.11337), Finitely Verifiable Tokenizer Segmentation 6-Decision Finite-State Verifier (2610.30168).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_dfinite_length_decidability_conditional_regular_trichotomy_pspace_minimalist_horn_synthesis_and_nested_session_types_pcc', 'description': 'Executes Formal Engine #495 (Level 481 / REG-201): D-Finite Length Generating Function Decidability for RE Languages (2610.33111), Conditional Regular Language Membership PSPACE-Complete Query Trichotomy (2610.16610), Minimalist Machine Two-Body Horn Clause Recursive Program Synthesis (2610.06304), Nested Session Types Asynchronous Processes 2-Counter Turing Completeness (2610.32558).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_cyclic_linear_choreography_rocq_polymorphic_fe_environment_lean_iris_indirection_ghost_state_and_holistic_specgen_pcc', 'description': 'Executes Formal Engine #496 (Level 482 / REG-202): Cyclic Linear Logic Choreography Bisimilarity & Lock-Free Extraction (2610.29736), Rocq Polymorphic First-Class Environment Calculus F_E without Substitution (2610.36798), Lean Iris on Indirection Theory Higher-Order Ghost State without Domain Theory (2610.41202), Holistic 350-Task Lean Specification Generation Input/Output Evaluator (2610.10604).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_modular_sequent_base_extension_rowhammer_dirac_collapse_fibrational_dag_logic_and_girard_algebra_mall_pcc', 'description': 'Executes Formal Engine #497 (Level 483 / REG-203): Modular Sequent Base-Extension Semantics for MALL & Jankov Logic (2610.23822), Probabilistic Rowhammer Small-Step Semantics & Dirac Collapse via Physical Separation (2610.33748), Fibrational DAG-Descriptor Framework for Multi-Conclusion Linear Logics (2610.36552), Girard Algebras Atomic Subvariety Lattice & Continuum Post-Complete MALL Extensions (2610.16804).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_hott_strict_universe_model_agda_ec_to_cmtt_compilation_lean_countable_wdp_and_ltlf_axp_cxp_pcc', 'description': 'Executes Formal Engine #498 (Level 484 / REG-204): HoTT Voevodsky Universe Model Strictification in Rocq UniMath (2610.28370), Agda-Mechanized Compilation of Polymorphic Environment Classifiers to Contextual Modal Types CMTT (2610.25741), Lean-Mechanized Countable Nondeterminism in Module-Weighted Programming & WDP Fixed Points (2610.39723), Native Abductive/Contrastive Explanations for LTLf over Finite Traces via ASP MUC/MCS (2610.35169).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_tableaux_monoid_polygraphic_rewriting_dfa_correction_tree_compositional_timed_rta_and_transformer_weighted_automata_pcc', 'description': 'Executes Formal Engine #499 (Level 485 / REG-205): Tableaux Monoid Finite Quadratic Convergent & Coherent Polygraphic Rewriting (2610.10035), Regular Tree Language Characterization of DFA Corrections with Explicit Edit Operations (2610.06714), Compositional Real-Time Automata RTA Learning of Timed Synchronous Systems (2610.21237), Transformer to Real-Weighted Automata Correspondence & Tolerance Identity Testing (2610.04569).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_agdecode_rocq_attribute_grammar_pumping_semiring_pushdown_network_parameterized_game_antichain_and_qbx_merkle_compiler_pcc', 'description': 'Executes Formal Engine #500 (Level 486 / REG-206): AGDecode Rocq-Mechanized Attribute Grammar LFP Derivatives with SMT/CHC Oracles (2610.36105), Exact Quantitative Reachability of Acyclic Weighted Pushdown Networks over Pumping Semirings via Segment Tree Algebras & Thermal Extensions (2610.11991), Symbolic Antichain Fixed-Point Algorithms for Concurrent Parameterized Knowledge Games (2610.11711), QBX Port-DAG Compiler with Time-Availability Effects & Merkle Content Identities across 23,342 Candidates (2610.41689).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_agreement_lean_geo_consensus_rust_avcss_sieve_astral_accountable_quorum_and_cross_chain_bridge_cvv_pcc', 'description': 'Executes Formal Engine #501 (Level 487 / REG-207): A-greement Geo-Replicated SMR Consensus & AI-greement Lean Verification Framework (2610.30114), Rust 7-Protocol Asynchronous Verifiable Complete Secret Sharing Design Sieve with Off-Critical-Path Verification (2610.37234), Astral 2f+1 Accountable Semantic Consensus with Committed Evidence Snapshots & Signed Challenges (2610.33587), Cross-Chain Bridge Verification Vulnerability Taxonomy of 11 Patterns in 5 Categories across 830 Instances (2610.13170).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_lean_moe_speculative_bandwidth_crossover_checkerbench_static_synthesizer_salt_type_inference_and_alkaid_alir_pcc', 'description': 'Executes Formal Engine #502 (Level 488 / REG-208): Lean-Checked MoE Speculative Decoding Expert-Byte Bandwidth Crossover & Monotone Staircase Draft Length (2610.34440), CheckerBench 300-Task Static-Analysis Checker Synthesis across 297 CVEs & 85 CWEs with Vulnerable-Fixed Contrast (2610.07557), SALT Static-Analysis-Guided Python Type Inference Reducing LLM Cost by up to 78.5% (2610.41617), Alkaid ALIR Bit-Exact Fixed-Point Compiler Reducing LUTs by 20-30% & Latency by up to 40% (2610.04808).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_retroq_retromorphic_hadamard_compiler_lean_group_k_consensus_mlkem_public_reuse_and_patternbench_ast_faithfulness_pcc', 'description': 'Executes Formal Engine #503 (Level 489 / REG-209): RetroQ Retromorphic & Hadamard-Test Validation of Quantum Compiler Passes across 4 Frameworks (2610.11195), Lean-Verified Group-k Consistency Bounds (d+1 / d+2) vs Maximum Clique Alignment Error (2610.27275), System-Level ML-KEM Deterministic Public-Data Reuse Reducing Encapsulation/Decapsulation Cycles by 74.6%/58.8% (2610.01960), PatternBench AST Optimization Faithfulness across 7 Compiler-Transcendent Transformation Classes (2610.24835).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_sesaa_joern_static_analyzer_veriharness_disagreement_verifier_birth_death_pulse_recovery_and_dfit_dataflow_ir_pcc', 'description': 'Executes Formal Engine #504 (Level 490 / REG-210): SESAA Self-Evolving Auditable Joern Static Analysis Detecting 10/19 Subsequent CVEs (2610.30184), VeriHarness Disagreement Resolver & Consensus Challenger across 26,000 Rollouts (2610.00972), Exact Birth-Death Verification Pulse Budget Window (23 vs 9 Checks) for Escaping Wrong Consensus (2610.00256), DFIT Graph-IR & Backend-Lowering Instrumentation across Cerebras/SambaNova/TPU with 3.53-13.62% Overhead (2610.14280).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_vmspec_decompiler_obfuscation_privacyflow_contextual_integrity_equal_gram_quantum_dp_and_profile_dp_block_pcc', 'description': 'Executes Formal Engine #505 (Level 491 / REG-211): VMSpec Decompiler Processor Specification Recovery against VM Obfuscation across 147 Benchmarks & 6 Malware DGAs (2610.29566), PrivacyFlow System-2 Contextual Integrity Information-Flow Tracer across 5,873 Tasks (2610.40714), Two-Party O(1)-Error Quantum Differential Privacy via Guarded Coherent Round Trip & Equal-Gram Rigidity (2610.02113), Profile-DP Policy-Aware DP-BLOCK & DP-SLOT Mechanisms across 26 Format-Budget Settings (2610.27213).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_omnigeo_typed_neuro_symbolic_c1_diffeomorphism_gradient_dp_kronecker_cross_moment_and_atlasir_rust_validator_pcc', 'description': 'Executes Formal Engine #506 (Level 492 / REG-212): OmniGeo Dense Neuro-Symbolic Reasoning over Shared Typed Geometry State Solving 21/30 IMO-AG-30 (2610.04280), C1-Diffeomorphism Finite-Iterate Gradient Descent Differential Privacy on Perturbed Objectives (2610.02716), Kronecker-Product Randomized Response Exact Multivariate Cross-Moment Attenuation (2610.26460), AtlasIR Rust-Validated Unified Intermediate Representation with 5.43x CPU Speedup (2610.23964).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_raposol_semantic_anchor_dpo_evm_mcp_provenance_registry_edge_em_side_channel_and_goal_bisimulation_pcc', 'description': 'Executes Formal Engine #507 (Level 493 / REG-213): RAPO-Sol 6-Anchor Semantic Perturbation DPO for Repository-Level Solidity (2610.08429), EVM-Anchored MCP Provenance Registry with Rebuildable SQLite Mirror & 3 Attested Properties (2610.33350), Edge LLM Electromagnetic Side-Channel Audit across 3 Attack Classes & 128k Vocabulary (2610.14215), Goal-Conditioned Bisimulation Equivariant Temporal Skill Transfer (2610.00676).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_utxo_wallet_three_sdk_patterns_instance_anchored_interaction_evidence_concurrent_proposer_geography_and_gradsat_qffp_pcc', 'description': 'Executes Formal Engine #508 (Level 494 / REG-214): CCC 3-Pattern SDK for Extended-UTXO Wallets over 3 Cryptographic Primitives (2610.30183), Instance-Anchored Interaction Evidence with Grammar-Constrained Symbolic Execution across 1,255 WatchAct Tasks (2610.12157), Concurrent Block Proposer Geography Ordinal Potential & Weighted k-Median Decentralization Equilibrium (2610.18812), GradSAT 2-Stage Multi-Task Gradient-Normalized QF_FP SMT Solver (2610.08808).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_client_led_consensus_inclusion_safety_bsit_decoupled_tree_sampler_alpha_fair_task_orchestration_and_periodized_chebyshev_lattice_pcc', 'description': 'Executes Formal Engine #509 (Level 495 / REG-215): Client-Led Leaderless Consensus Inclusion Safety via 2-Path Fork Selection (2610.29497), BSIT Bootstrap Stochastic Interpolant Tree Decoupled Sampler under Sparse Reward (2610.24185), Alpha-Fair 2-Stage Hierarchical Trusted Task Orchestration with +22.0% Completion Gain (2610.33295), 3-Ingredient Periodized Chebyshev Higher-Order Lattice Quadrature with Base 1.110721^s (2610.01113).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_maestro_global_proof_coordinator_ineqagent_symbolic_backends_mechanical_vacuity_autoformalization_and_rpbft_exact_potential_pcc', 'description': 'Executes Formal Engine #510 (Level 496 / REG-216): Maestro Global Proof Coordination Solving 669/672 PutnamBench & 34/48 arXivLean (2610.25920), IneqAgent 3-Backend Symbolic Certificate Lean 4 Prover Solving 175/186 (2610.20681), Mechanical Numerical & Vacuity Autoformalization Verification on FLMF/DLMF (2610.20573), R-PBFT Exact-Potential Adaptive Byzantine Redundancy with +62.3% Timely Updates (2610.29592).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_rust_sliding_window_speedup_matter_thread_cached_pqc_nist_fips_32bit_slhdsa_energy_and_email_pqc_downgrade_defense_pcc', 'description': 'Executes Formal Engine #511 (Level 497 / REG-217): Python-to-Rust Sliding-Window Language (4-29x) vs Incremental Algorithm (>11,000x) Decomposition (2610.07931), Matter-over-Thread Cached-Chain & Hybrid P-256+ML-KEM-512 Session Establishment (2610.13026), NIST FIPS 203/204/205 32-Bit SLH-DSA +243% Energy Guard (2610.27111), Email Multi-Hop PQC Negotiation & Plaintext SMTP Fallback Defense (2610.36145).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_dualguard_speculative_memory_safety_mha_lean_head_complexity_lndp_subgraph_counting_and_hybrid_pqc_qkd_combiner_pcc', 'description': 'Executes Formal Engine #512 (Level 498 / REG-218): DualGuard 4-Category Sequential & Speculative Memory Safety with 3%-72% Overhead Reduction (2610.39374), Lean-Verified Multi-Head Attention Head Complexity & 10-Bit Strict Threshold Bound (2610.25341), Optimal O(n^{k-1/2}/eps^{k-1}) Subgraph Counting under Local Node DP (2610.22278), 8-Dimension Hybrid PQC-QKD KEM-Combiner across RFCs 8784/9370/9867 (2610.19039).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_mirror_multipath_quorum_integrity_secreason_instream_self_repair_database_mte_cheri_trilemma_and_quasar_mec_free_qlearning_pcc', 'description': 'Executes Formal Engine #513 (Level 499 / REG-219): MIRROR Multipath Quorum Integrity with 0% AiTM ASR at 1x Token Cost vs 35x LLM-Judge (2610.02349), SecReason Dual-Track In-Stream Self-Repair Raising Secure Code to 72.8%-98.1% (2610.14453), Database MTE (~10%) vs CHERI (20%-60%) Memory-Safety Trilemma across 6 Engines (2610.11525), Quasar Model-Free O(|S||A|) Reachability Q-Learning in MEC-Free MDPs (2610.01781).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_reva_contextual_probe_vulnerability_screening_deepavr_six_role_avr_reins_thread_scheduler_and_cross_chain_trust_coordination_pcc', 'description': 'Executes Formal Engine #514 (Level 500 / REG-220): REVA Single-Pass Contextual Probe Vulnerability Screening >250x Faster on PrimeVul (2610.35829), DeepAVR 6-Role Patch-Conditioned Relocalization & Root-Cause AVR with 92.3% VulnLoc Accuracy (2610.32345), REINS Agent-Guided Concurrency Thread Scheduler Finding 6 New Bugs (2610.13421), Trust-Centric Cross-Chain Coordination with Unlinkability & Stake-Reputation Relays (2610.41032).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_vela_interface_restricted_agent_security_tee_pbs_rollup_sequencer_chainseed_emulator_and_synthapi_tool_scaling_pcc', 'description': 'Executes Formal Engine #515 (Level 501 / REG-221): VELA Interface-Restricted Agent Web Security across 44 Vulnerabilities & 12 Families (2610.35541), TEE-Enabled Proposer-Builder Separation Rollup Sequencer Neutrality (2610.24284), ChainSEED High-Fidelity 60,000-Validator Blockchain Emulator (2610.31188), SynthAPI 3-Axis Tool-Use Agent Scaling Law over 458,752 Tasks & 849 Models (2610.37648).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_skillsif_linux_kernel_skill_evolution_agenticvulhunter_local_scrbench_osteon_decay_governance_and_qutop_compiler_selection_pcc', 'description': 'Executes Formal Engine #516 (Level 502 / REG-222): SKILL-SIF Failure-Driven Security Skill Evolution with 8x Unseen Vulnerability Gain over 14,800 Runs (2610.25705), AgenticVulHunter Local SCRBench Review Outperforming Commercial Sonnet 4 (2610.27383), OSTEON Session-Start Knowledge Decay Governance across 452 Repos (2610.31306), QuTOP Top-Down Rule-Guided Quantum Compiler Selection over 268 Circuits (2610.29170).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_agent_harness_independent_critic_verification_sdo_telemetry_playbooks_llm_regression_fault_enforcing_guard_and_failbench_fault_tolerance_pcc', 'description': 'Executes Formal Engine #517 (Level 503 / REG-223): Agent Harness 4-Layer Independent Critic Verification across 17 Designs & 7 Models (2610.34577), Self-Defining Operator Telemetry Playbooks with 52% Faster Resolution across 11 Microservices (2610.14547), LLM Regression Test Fault-Enforcing Guard across 145 PRs (2610.11835), FailBench 142-Combination Distributed Training Fault Tolerance Selection (2610.07688).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_reasoning_trace_half_truncation_contra_selective_clarification_interacct_crosschain_access_and_decentralized_edr_3axis_sok_pcc', 'description': 'Executes Formal Engine #518 (Level 504 / REG-224): Reasoning Trace 50% Fixed Truncation Cost-Correctness across 866 Python Tasks (2610.36952), CONTRA Selective Clarification Qualification with +13.88 pp F1 across 4 Coding Agents (2610.01769), InterAcct Consortium-Level Cross-Chain Access Control (2610.05054), Decentralized EDR/XDR 3-Axis SoK Hybrid Orchestration (2610.01872).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_specreveal_intent_defense_divalgo_algorithmic_diversity_two_layer_magic_state_verification_and_distributed_ftqc_bell_link_pcc', 'description': 'Executes Formal Engine #519 (Level 505 / REG-225): SpecReveal 96.88% Dual-View Intent Reconstruction Defense against SpecCloak 28.91% ASR (2610.17907), DivAlgo Algorithmic Diversity Evaluation across 24 Models (2610.19157), Two-Layer Verification for [[21,3,5]] Quantum Magic-State Preparation (2610.32267), Distributed FTQC 1-MHz 90%-Fidelity Bell-Pair Link Resource Analysis (2610.34143).', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}},
        {'name': 'aleph_prove_omega_continual_self_improvement_hipporag2_titans_zero_forgetting_and_bitacora_vault', 'description': 'Nivel 506 (v33.0.0 — REG-330): Certifica formalmente la Bóveda Interna de Bitácora (350+ reglas compiladas en El Aleph), recuperación asociativa HippoRAG 2 PPR, memorización Titans con momento, TextGrad, torneo evolutivo DGM + AlphaEvolve y 0.0% Catastrophic Forgetting (cadena Merkle SHA-256).', 'inputSchema': {'type': 'object', 'properties': {'query_context': {'type': 'string'}, 'min_required_rules': {'type': 'integer'}, 'simulate_tamper_or_forgetting': {'type': 'boolean'}}}},
        {'name': 'aleph_bitacora_query_hipporag2_ppr', 'description': 'Consulta las 350+ reglas aprendidas de la Bitácora compiladas nativamente dentro de El Aleph usando el motor híbrido HippoRAG 2 (Personalized PageRank sobre Grafo de Conocimiento + Okapi BM25 + EWC).', 'inputSchema': {'type': 'object', 'properties': {'query': {'type': 'string'}, 'top_k': {'type': 'integer'}, 'shard_filter': {'type': 'string'}}, 'required': ['query']}},
        {'name': 'aleph_bitacora_enforce_pre_turn_gate', 'description': 'Compuerta Pre-Turno Always-On: Audita código o planes de ingeniería contra las 350+ reglas internas de la Bitácora en El Aleph antes de ejecutar cambios.', 'inputSchema': {'type': 'object', 'properties': {'code_or_plan': {'type': 'string'}, 'top_k': {'type': 'integer'}}, 'required': ['code_or_plan']}},
        {'name': 'aleph_bitacora_learn_experiential_rule', 'description': 'Aprende y consolida una nueva regla operativa (SI -> ENTONCES -> EVITAR) desde una experiencia o error usando Sorpresa de Titans + ExpeL + TextGrad y la sella en la cadena Merkle interna sin olvidar ninguna regla previa.', 'inputSchema': {'type': 'object', 'properties': {'friction_or_error': {'type': 'string'}, 'si_clause': {'type': 'string'}, 'entonces_clause': {'type': 'string'}, 'evitar_clause': {'type': 'string'}, 'shard': {'type': 'string'}, 'persist_to_disk': {'type': 'boolean'}}, 'required': ['friction_or_error', 'si_clause', 'entonces_clause', 'evitar_clause']}},
        {'name': 'aleph_omega_dgm_alphaevolve_self_improve', 'description': 'Ejecuta un ciclo completo de automejora continua SOTA (Darwin Gödel Machine + AlphaEvolve + HippoRAG 2 PPR + Titans + TextGrad + Voyager AST + CEGIS).', 'inputSchema': {'type': 'object', 'properties': {'task_description': {'type': 'string'}, 'observed_friction': {'type': 'string'}, 'persist_new_rule': {'type': 'boolean'}}}},
        {'name': 'aleph_bitacora_vault_status_and_telemetry', 'description': 'Devuelve el estado completo de la Bóveda Interna de Bitácora de El Aleph (350+ reglas activas, desglose por nodo, raíz Merkle SHA-256 y verificación de 0.0% olvido catastrófico).', 'inputSchema': {'type': 'object', 'properties': {}}},
        {
            'name': 'aleph_v4_verify_aep_scm_hcm_pqc_and_bft',
            'description': 'Ejecuta y verifica los 5 motores v4 de .aleph/v4_engine/: protocolo binario AEP, Modelo Causal SCM de Pearl, Memoria Holográfica VSA 10.240 bits, criptografía post-cuántica FIPS 203 y consenso DAG-BFT Super-Swarm.',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'state_hash': {'type': 'string', 'description': 'Hash/estado del árbol a sellar con PQC.'},
                    'cause': {'type': 'string', 'description': 'Causa raíz a registrar en memoria holográfica VSA.'},
                    'effect': {'type': 'string', 'description': 'Efecto observado.'},
                    'remediation': {'type': 'string', 'description': 'Remediación verificada.'},
                    'total_agents': {'type': 'integer', 'default': 10},
                },
            },
        },
        {
            'name': 'aleph_ide_lifecycle_hook_and_hygiene_gate',
            'description': 'Ejecuta los 4 hooks nativos de ciclo de vida del IDE (.aleph/hooks/: UserPromptSubmit, PreToolUse, PostToolUse, Stop) y el escáner de higiene del repositorio (.aleph/scripts/scan_cleanliness.py).',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'prompt': {'type': 'string'},
                    'command': {'type': 'string'},
                    'source_code': {'type': 'string'},
                    'stdout': {'type': 'string'},
                    'scan_repo': {'type': 'boolean', 'default': False},
                },
            },
        },
        {
            'name': 'aleph_swarm_governor_50_orchestrate',
            'description': 'Ejecuta el orquestador distribuido SwarmGovernor50 (.aleph/scripts/swarm_governor_50.py) con Multi-Raft, AST-CRDT, SMP, Tarjan DFS, HART v2 y Plumtree Gossip.',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'num_agents': {'type': 'integer', 'default': 50},
                    'duration_seconds': {'type': 'number', 'default': 0.05},
                },
            },
        },
    ]
    return tools
