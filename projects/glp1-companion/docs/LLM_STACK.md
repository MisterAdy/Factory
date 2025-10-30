# GLP-1 Companion LLM Stack

## Models

| Task        | Model              | Provider | Notes                       |
| ----------- | ------------------ | -------- | --------------------------- |
| Research    | google/gemini-pro  | LiteLLM  | Cost-effective discovery    |
| Build/Test  | openai/gpt-4o-mini | LiteLLM  | Strong coding performance   |
| Images      | openai/dall-e-3    | LiteLLM  | Marketing mockups           |

## Budget Policy

* Project cap: $500 per validation cycle
* Research agent soft cap: $200
* Builder agent soft cap: $200
* QA agent soft cap: $100

## Governance

* Model changes require ADR approval.
* External MCP servers must be declared in `docs/MCP_ALLOWLIST.md`.
* Cost overruns above 90% trigger an approval thread via the orchestrator.
