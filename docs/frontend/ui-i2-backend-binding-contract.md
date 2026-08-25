# UI-I2 Backend Binding Contract

`services/api-server/src/ui_i2/` is an adapter boundary, not a second ingestion/QC engine.

Bind:

- `list_sessions` -> canonical session registry/read model
- `get_session` -> canonical session detail/read model
- `create_import` / `upload_import` -> immutable source registration + ingestion orchestration
- `get_preflight` -> canonical validation/preflight evidence
- `get_mapping` / `resolve_mapping` -> versioned channel ontology mapping
- `get_quality` -> canonical QC service/read model

## Required scientific behavior

- raw source receives immutable identity/hash;
- Noraxon single CSV supported;
- Noraxon separated export may use a workspace/directory ingestion adapter if browser
  multi-file upload is not yet supported;
- signal sampling rates are per-signal, not assumed globally;
- missing values are not silently imputed at raw layer;
- V/uV conversion requires provenance;
- preflight FAIL cannot proceed;
- mapping uncertainty must surface as exception;
- QC works at session/channel/window;
- QC FAIL blocks unsupported downstream metrics;
- WARNING/UNKNOWN remain reviewable, not silently PASS.

## Fail closed

If the live core cannot satisfy the adapter contract, leave routes unbound and return
`BACKEND_BINDING_NOT_CONFIGURED` / `BLOCKED_BACKEND_BINDING`.

Do not bind demo fixtures to real mode.
