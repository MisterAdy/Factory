# Commerce Factory Orchestrator

The orchestrator coordinates agent loops, enforces budgets, and mediates between the mail bus and shared services.

## Getting Started

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
orchestrator  # or python -m orchestrator.main
```

The `orchestrator.main` module loads configuration from `config/` and starts an asynchronous tick loop that:

1. Scans project repositories for *new or updated* mail threads.
2. Dispatches work to the LiteLLM proxy respecting per-agent budgets.
3. Writes replies back to the `.mail/outbox` for human review.

## Configuration

* `config/litellm.config.yaml` — shared model routing and budgets for the LiteLLM proxy.
* `config/settings.example.toml` — sample runtime configuration (copy to `settings.toml`).
