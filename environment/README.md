# Reproducible environment

`environment-lock.research.yaml` and `requirements-core.lock.txt` lock the exact
core/tooling versions for the Day 26 blueprint.

A real resolver-generated `uv.lock` is intentionally **not fabricated** in this
package. Before Day 29 training, run in the approved connected environment:

```bash
uv lock
uv lock --check
uv sync --frozen
```

Commit `uv.lock`, record its SHA-256 in the experiment manifest, and make the
training preflight fail closed when the lock is missing or inconsistent.
