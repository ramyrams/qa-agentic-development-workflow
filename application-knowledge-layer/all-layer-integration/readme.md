The design centers on one decision: your access is mixed (partial backend source, stale spec, DDL-only DB), so every API and trace record carries a `source` and `confidence` field rather than treating all links as equally trustworthy. Three things worth flagging:

1. **Observed network traffic outranks the spec, not the other way around** — since the spec is known stale, what the UI actually calls during capture is treated as closer to ground truth, and the reconciliation step surfaces spec gaps rather than papering over them.
2. **DB and baseline-API import are mechanical and independent** — the DDL parser and OpenAPI importer don't need the UI walkthrough at all, so they can start immediately in parallel with the pilot you're about to run.
3. **`tables_touched` confidence is capped by what you actually have** — code-traced only where backend source is reachable; everywhere else it stays explicitly `inferred`/`unknown` rather than an agent guessing table names from a response shape and that guess quietly becoming "fact" downstream.

Want me to write the new skill files next (`import-db-schema`, `reconcile-api-contract`, `code-trace-api`), or extend `capture-page` itself to add the network-call recording step first?
