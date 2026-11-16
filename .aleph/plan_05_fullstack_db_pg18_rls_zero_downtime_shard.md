# Plan 05 — NODE-03 Full-Stack Database, PostgreSQL 18, Supabase Multi-Tenant RLS & Zero-Downtime DDL Shard (v15.0.0 Unified Master Kernel)

## 1. Misión Arquitectónica y Dominio Pareto sobre Lovable.dev
Este plan activo en `.aleph` gobierna los **39 niveles de verificación formal (`Levels 264..302`)** y **39 herramientas MCP (`#273..#311`)** desarrollados por `NODE-03` e integrados sin pérdida en el **Kernel Maestro Unificado `El Aleph v15.0.0`** junto con `NODE-01`, `NODE-02`, `NODE-04`, `NODE-05`, `NODE-06` y `.aleph`.

## 2. Cobertura Formal de los 39 Provers de NODE-03 (`Levels 264..302`)
1. **PostgreSQL 18 Kernel & I/O Engine**:
   - Async I/O (`io_method = 'worker' | 'io_uring'`, `effective_io_concurrency >= 16`), `UUIDv7` (`uuidv7()`) para localidad B-Tree sin fragmentación de página, `WITHOUT OVERLAPS` temporal constraints y claves foráneas `PERIOD`, `VIRTUAL` generated columns por defecto, `OLD`/`NEW` en `RETURNING`, `NULLS NOT DISTINCT`, Skip Scan en B-Tree, Parallel GIN Index Build, OAuth 2.0 `oauth_validator_libraries`, `pg_stat_io` y `pg_stat_checkpointer` con `checkpoint_completion_target >= 0.8`.
2. **Supabase Multi-Tenant RLS & Isolation**:
   - Aislamiento estricto por `tenant_id` con `(SELECT auth.jwt() ->> 'tenant_id')` envuelto en `InitPlan` (`O(1)` por query), segregación de claims inmutables (`app_metadata` vs `user_metadata`), `WITH CHECK` de vinculación de actor en `INSERT` y de inmutabilidad de `tenant_id` en `UPDATE`, políticas `FOR DELETE` restringidas a roles administrativos, y cadenas de vistas con `WITH (security_invoker = true, security_barrier = true)`.
3. **Migraciones DDL Zero-Downtime (Expand-Contract)**:
   - Prohibición total de `VACUUM FULL`, `CLUSTER`, `TRUNCATE`, `REINDEX` no concurrente y `ALTER TYPE` bloqueante; obligatoriedad de `SET LOCAL lock_timeout` + `statement_timeout`, `CREATE INDEX CONCURRENTLY`, `NOT VALID` + `VALIDATE CONSTRAINT` en transacciones separadas, particionado `ATTACH/DETACH PARTITION CONCURRENTLY`, y renombrado de constraints e índices solo en metadatos (`RENAME CONSTRAINT` / `ALTER INDEX ... RENAME TO`).


## Cycle 40 (Level 303 / Tool #312 / Test #482 / REG-088)
- **Verifier**: `PG18LogicalReplicationConflictStatsSupabaseRlsRestrictivePolicyAndForeignKeyReferencingIndexProver`
- **MCP Tool**: `aleph_audit_pg18_logical_replication_conflicts_restrictive_rls_and_fk_index`
- **Invariants**: PG18 `track_commit_timestamp = on` & `pg_stat_subscription_stats` 7-counter monitoring, Supabase Multi-Tenant RLS `AS RESTRICTIVE` policy composition (`AND` isolation boundary over `PERMISSIVE` policies), and Zero-Downtime Foreign Key referencing B-Tree index prefix + `NOT VALID`/`VALIDATE CONSTRAINT` lock discipline.


## Cycle 41 (Level 304 / Tool #313 / Test #483 / REG-089)
- **Verifier**: `PG18TemporalWithoutOverlapsConstraintSupabaseRlsStorageBucketPathIsolationAndZeroDowntimeColumnTypeChangeProver`
- **MCP Tool**: `aleph_audit_pg18_temporal_without_overlaps_storage_rls_and_column_type_change`
- **Invariants**: PG18 `WITHOUT OVERLAPS` temporal Primary/Unique keys & `PERIOD` Foreign Keys (`btree_gist`), Supabase `storage.objects` multi-tenant bucket & path prefix `(storage.foldername(name))[1]` RLS isolation, and Zero-Downtime Expand-Contract column type migrations.


## Cycle 42 (Level 305 / Tool #314 / Test #484 / REG-090)
- **Verifier**: `PG18GeneratedColumnVirtualStoredDisciplineSupabaseRlsRealtimePublicationFilterAndZeroDowntimeTablePartitioningProver`
- **MCP Tool**: `aleph_audit_pg18_virtual_generated_columns_realtime_rls_and_attach_partition`
- **Invariants**: PG18 `GENERATED ALWAYS AS (...) VIRTUAL` zero-rewrite & immutability discipline, Supabase Realtime `realtime.messages` multi-tenant topic prefix RLS isolation, and Zero-Downtime `ATTACH PARTITION` pre-validated `CHECK (...) NOT VALID` + `VALIDATE CONSTRAINT`.


## Cycle 43 (Level 306 / Tool #315 / Test #485 / REG-091)
- **Verifier**: `PG18ReturningOldNewDeltaAuditSupabaseRlsJwtCustomClaimsHookAndZeroDowntimeDetachPartitionConcurrentlyProver`
- **MCP Tool**: `aleph_audit_pg18_returning_old_new_app_metadata_rls_and_detach_partition_concurrently`
- **Invariants**: PG18 `RETURNING OLD AS old_row, NEW AS new_row` single-roundtrip delta audit & integer-cent conservation, Supabase RLS `app_metadata` vs mutable `user_metadata` isolation + `custom_access_token_hook` privilege lockdown, and Zero-Downtime `DETACH PARTITION ... CONCURRENTLY` archival.


## Cycle 44 (Level 307 / Tool #316 / Test #486 / REG-092)
- **Verifier**: `PG18SkipScanMulticolumnBTreeIndexSupabaseRlsPostgrestEmbeddedResourceGuardAndZeroDowntimeDropColumnProver`
- **MCP Tool**: `aleph_audit_pg18_skip_scan_postgrest_embedded_rls_and_drop_column`
- **Invariants**: PG18 B-Tree Skip Scan composite index cardinality ordering (`tenant_id` lead or `NDV <= 32` prefix), Supabase PostgREST embedded resource join Foreign Key RLS isolation, and Zero-Downtime `DROP COLUMN ... RESTRICT` contract phase.


## Cycle 45 (Level 308 / Tool #317 / Test #487 / REG-093)
- **Verifier**: `PG18AsyncIoMethodWorkerUringTuningSupabaseRlsVaultSecretDecryptionConfinementAndZeroDowntimeEnumEvolutionProver`
- **MCP Tool**: `aleph_audit_pg18_aio_vault_secret_rls_and_zero_downtime_enum_evolution`
- **Invariants**: PG18 Asynchronous I/O (`io_method = worker | io_uring`, `effective_io_concurrency >= 16`), Supabase Vault `vault.decrypted_secrets` multi-tenant confinement (`SET search_path = ''`, `app_metadata.tenant_id`), and Zero-Downtime `ENUM`/domain evolution without table rewrite.


## Cycle 46 (Level 309 / Tool #318 / Test #488 / REG-094)
- **Verifier**: `PG18Uuidv7TemporalLocalityPrimaryKeySupabaseRlsMfaAal2FinancialMutationGuardAndZeroDowntimeTableRenameDualViewProver`
- **MCP Tool**: `aleph_audit_pg18_uuidv7_rls_aal2_mfa_and_zero_downtime_table_rename`
- **Invariants**: PG18 native `uuidv7()` monotonic B-Tree locality with `(tenant_id, id)` composite PK, Supabase RLS `AS RESTRICTIVE` `(SELECT auth.jwt() ->> 'aal') = 'aal2'` step-up MFA on critical mutations, and Zero-Downtime table rename via `security_invoker = true` compatibility view.


## Cycle 47 (Level 310 / Tool #319 / Test #489 / REG-095)
- **Verifier**: `PG18VacuumMaxEagerFreezeFailureRateTuningSupabaseRlsPgNetWebhookTenantSignatureAndZeroDowntimeMaterializedViewRefreshConcurrentlyProver`
- **MCP Tool**: `aleph_audit_pg18_eager_freeze_pg_net_webhook_and_matview_refresh_concurrently`
- **Invariants**: PG18 `vacuum_max_eager_freeze_failure_rate` (`0.01..0.10`) & `vacuum_truncate = false`, Supabase `pg_net` (`net.http_post`) SSRF & HMAC tenant signature confinement, and Zero-Downtime `REFRESH MATERIALIZED VIEW CONCURRENTLY` with `security_invoker = true` RLS wrapper view.


## Cycle 48 (Level 311 / Tool #320 / Test #490 / REG-096)
- **Verifier**: `PG18ParallelGinIndexBuildMaintenanceWorkMemSupabaseRlsPgvectorHnswIterativeScanAndZeroDowntimeReindexConcurrentlyProver`
- **MCP Tool**: `aleph_audit_pg18_parallel_gin_pgvector_iterative_rls_and_reindex_concurrently`
- **Invariants**: PG18 parallel GIN index build (`max_parallel_maintenance_workers >= 2`, `maintenance_work_mem >= 256MB`, `gin_pending_list_limit <= 4096kB`), Supabase `pgvector` HNSW `hnsw.iterative_scan = 'relaxed_order'` under `AS RESTRICTIVE` `app_metadata.tenant_id` RLS, and Zero-Downtime `REINDEX INDEX CONCURRENTLY` with invalid `_ccnew`/`_ccold` cleanup.


## Cycle 49 (Level 312 / Tool #321 / Test #491 / REG-097)
- **Verifier**: `PG18PgStatIoPerBackendWalTrackingSupabaseRlsPgCronJobTenantContextConfinementAndZeroDowntimePrimaryKeySwapProver`
- **MCP Tool**: `aleph_audit_pg18_stat_io_pg_cron_rls_and_zero_downtime_pk_swap`
- **Invariants**: PG18 `pg_stat_io` byte-granular (`read_bytes`/`write_bytes`/`extend_bytes`) & `pg_stat_get_backend_io(pid)` WAL telemetry, Supabase `pg_cron` non-`BYPASSRLS` role switching & `app_metadata.tenant_id` JWT context confinement, and Zero-Downtime `PRIMARY KEY USING INDEX` swap.


## Cycle 50 (Level 313 / Tool #322 / Test #492 / REG-098)
- **Verifier**: `PG18ExplainBuffersDefaultAutoExplainPlanDriftSupabaseRlsGraphqlMaxDepthIntrospectionGuardAndZeroDowntimeSequenceBigintUpgradeProver`
- **MCP Tool**: `aleph_audit_pg18_explain_buffers_pg_graphql_rls_and_bigint_sequence`
- **Invariants**: PG18 `EXPLAIN (ANALYZE)` default `BUFFERS` (`temp_written_blocks == 0`, zero large-table `Seq Scan`), Supabase `pg_graphql` depth ceiling (`max_depth <= 5`) & `AS RESTRICTIVE` edge RLS isolation, and Zero-Downtime `int4` -> `bigint` sequence upgrade via Expand-Contract.


## Cycle 51 (Level 314 / Tool #323 / Test #493 / REG-099)
- **Verifier**: `PG18OAuthBearerValidatorConnectionSecuritySupabaseRlsSupavisorTransactionPoolPreparedStatementAndZeroDowntimeDefaultBackfillProver`
- **MCP Tool**: `aleph_audit_pg18_oauth_supavisor_pool_rls_and_fast_default_column`
- **Invariants**: PG18 `hostssl` + native `oauth` (`oauth_validator_libraries`) / `scram-sha-256` HBA security, Supabase Supavisor transaction-mode pool `SET LOCAL` (`set_config(..., true)`) isolation without session bleed, and Zero-Downtime non-volatile `ADD COLUMN` fast defaults (`attmissingval`).


## Cycle 52 (Level 315 / Tool #324 / Test #494 / REG-100)
- **Verifier**: `PG18PgChecksumsDataIntegrityVerificationSupabaseRlsPostgresFdwUserMappingConfinementAndZeroDowntimeTableSplitVerticalPartitionProver`
- **MCP Tool**: `aleph_audit_pg18_checksums_fdw_confinement_and_vertical_table_split`
- **Invariants**: PG18 default `data_checksums = on` & `pg_stat_database.checksum_failures == 0`, Supabase `postgres_fdw` `FOREIGN TABLE` private schema & `app_metadata.tenant_id` pushdown confinement, and Zero-Downtime vertical table split (hot/cold decomposition).


## Cycle 53 (Level 316 / Tool #325 / Test #495 / REG-101)
- **Verifier**: `PG18PgUpgradeOptimizerStatisticsCarryoverSupabaseRlsEdgeFunctionServiceRoleBypassGuardAndZeroDowntimeCheckConstraintModificationProver`
- **MCP Tool**: `aleph_audit_pg18_upgrade_stats_edge_function_rls_and_check_constraint_replace`
- **Invariants**: PG18 `pg_upgrade` optimizer statistics carryover + extended statistics `ANALYZE`, Supabase Edge Function `SUPABASE_ANON_KEY` + caller `Authorization` header forwarding (forbidding `SUPABASE_SERVICE_ROLE_KEY` `BYPASSRLS` in user endpoints), and Zero-Downtime `CHECK` constraint replacement (`ADD NOT VALID` -> `VALIDATE` -> `DROP old`).


## Cycle 54 (Level 317 / Tool #326 / Test #496 / REG-102)
- **Verifier**: `PG18SubtransactionSlruCacheOverflowGuardSupabaseRlsSsoSamlProviderDomainMappingAndZeroDowntimeUniqueConstraintViaConcurrentIndexProver`
- **MCP Tool**: `aleph_audit_pg18_subtrans_slru_sso_saml_rls_and_unique_using_index`
- **Invariants**: PG18 subtransaction SLRU cache overflow prevention (`max_subxids <= 64`, set-based `ON CONFLICT`/`MERGE`), Supabase Enterprise SSO/SAML `sso_provider_id` -> `app_metadata.tenant_id` binding + `AS RESTRICTIVE` RLS, and Zero-Downtime `ADD CONSTRAINT ... UNIQUE USING INDEX` via `CREATE UNIQUE INDEX CONCURRENTLY`.


## Cycle 55 (Level 318 / Tool #327 / Test #497 / REG-103)
- **Verifier**: `PG18IdleTransactionSessionTimeoutLockQueueDefenseSupabaseRlsPgmqQueueTenantIsolationAndZeroDowntimeForeignKeyCascadeReplacementProver`
- **MCP Tool**: `aleph_audit_pg18_tx_timeout_pgmq_rls_and_fk_cascade_replacement`
- **Invariants**: PG18 `transaction_timeout` (`<= 30s`), `idle_in_transaction_session_timeout` (`<= 10s`) & `lock_timeout` (`<= 5s`) lock-convoy defense, Supabase `pgmq` schema confinement + `app_metadata.tenant_id` message envelope stamping, and Zero-Downtime high-fanout Foreign Key `ON DELETE RESTRICT` + batched deletion transition.
