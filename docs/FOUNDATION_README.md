Here’s a single, self-contained Markdown doc you can drop into GitHub (e.g., docs/FOUNDATION_README.md). It consolidates the full plan, artifacts, decisions, and step-by-step setup for your team.
 
Commerce Factory — Foundation README
Status: v1.0 • Owner: Orchestrator (you) • Scope: End-to-end local setup, architecture, files, decisions, and operating model
This document captures the relevant parts of our design discussion and the initial scaffolding for a local-first, Git-auditable Commerce Factory that can run many parallel projects (“bets”) with agentic workflows, budget guardrails, and human-in-the-loop approvals. The first concrete project is GLP-1 Companion; the foundation is reusable for future projects.
 
Table of Contents
1.	Vision & Operating Model
2.	Architecture at a Glance
3.	Repo & Folder Layout
4.	Prerequisites
5.	Shared Services (Docker)
6.	Control Room (Next.js)
7.	Orchestrator (Python + Pydantic)
8.	Mail Bus (Git-backed threads + leases)
9.	Per-Project Template (GLP-1 example)
10.	Budgets, Pacing & Approvals
11.	Security & Compliance
12.	Runbook: First End-to-End Run
13.	Roadmap & Backlog
14.	Key Decisions & Rationale
15.	Incident Handling
16.	Glossary
 
Vision & Operating Model
•	Why now: Modern model gateways, agent protocols, and eval tooling make it possible for a single human orchestrator to coordinate a portfolio of small, instrumented bets—validating cheaply and scaling only winners.
•	What we’re building: A Validation & Scaling Factory. Agents (Architect, Research, Builder, QA, Growth) operate inside isolated project repos using a mail-style, Git-backed bus. The Control Room surfaces actions (deploy?, budget override?, merge?), while the Orchestrator enforces pacing and budgets.
•	Maturity model: DISCOVER → VALIDATE → BUILD → LAUNCH → SCALE → MAINTAIN/ARCHIVE. Promotion requires evidence + human approval.
•	Principles:
o	Trust-by-audit: All actions leave artifacts in Git (threads, leases, PRs, ADRs).
o	Speed with brakes: Loop pacing + gates make automation comprehensible.
o	Fiscal discipline: Hard caps per project; burn visible per agent/project.
o	Modularity: Per-project repos; shared skills/tools; swappable models.
 
Architecture at a Glance
•	Control Room (Next.js, read-only by default): Lists projects, renders shared docs (COMMERCE_FACTORY.md, DIVISION.md), shows budgets & loop pace, links to traces; later adds approvals & CRUD.
•	Orchestrator (Python): Pydantic-typed config loader, async tick loop, routes model calls via a LiteLLM proxy (budget & routing), interacts with the mail bus for agent threads, and opens PRs (no direct pushes).
•	Mail Bus (MCP mail server): Agents communicate via Markdown threads stored in the project repo; file leases prevent overwrite conflicts; full-text search.
•	Model Gateway (LiteLLM proxy): One API fronting multiple vendors; supports per-project and per-agent budget policies and tagging.
•	Observability (Langfuse): Centralized traces, tokens, costs per project/agent.
•	QA (Playwright container): Browser E2E, screenshots, logs → attached to mail threads / PRs.
 
Repo & Folder Layout
Use a parent folder with separate repos (isolation is intentional):
ai-factory/
  control-room/            # Repo A: Next.js dashboard
  orchestrator/            # Repo B: Python orchestrator + proxy config
  projects/
    glp1-companion/        # Repo C: first project (pattern for future)
  docs/                    # Shared documents rendered in Control Room
  docker-compose.yml       # Shared services (proxy, Langfuse, Playwright)
  .env                     # Provider keys for Docker services (not committed)
Separation policy: Control Room (read-only), Orchestrator (read-only across projects; PR-only writes), and per-project repos for all code/content/artifacts.
 
Prerequisites
•	Windows with Docker Desktop (WSL2 backend recommended)
•	Git
•	Node 20+ and pnpm (npm i -g pnpm)
•	Python 3.11+
•	(Optional but helpful) WSL2 Ubuntu for Node/Playwright ergonomics
 
Shared Services (Docker)
Create in ai-factory/:
.env
GEMINI_API_KEY=...
OPENAI_API_KEY=...
TOGETHER_API_KEY=...
IMAGE_API_KEY=...
docker-compose.yml
version: "3.9"
services:
  litellm:
    image: ghcr.io/berriai/litellm:latest
    ports: ["4000:4000"]
    volumes: ["./orchestrator/config/litellm.config.yaml:/app/config.yaml:ro"]
    environment:
      - LITELLM_CONFIG=/app/config.yaml
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - TOGETHER_API_KEY=${TOGETHER_API_KEY}
      - IMAGE_API_KEY=${IMAGE_API_KEY}
    command: ["--config", "/app/config.yaml"]

  langfuse-db:
    image: postgres:15
    environment:
      POSTGRES_USER: langfuse
      POSTGRES_PASSWORD: langfuse
      POSTGRES_DB: langfuse
    volumes: ["langfuse_db:/var/lib/postgresql/data"]

  langfuse:
    image: ghcr.io/langfuse/langfuse:latest
    depends_on: [langfuse-db]
    ports: ["3001:3000"]
    environment:
      - DATABASE_URL=postgresql://langfuse:langfuse@langfuse-db:5432/langfuse
      - NEXTAUTH_URL=http://localhost:3001
      - NEXTAUTH_SECRET=devsecret
      - SALT=devsalt

  pw:
    image: mcr.microsoft.com/playwright:v1.48.0-jammy
    tty: true
    shm_size: 2gb
    working_dir: /workspace
    volumes:
      - ./orchestrator/pw-runner:/workspace
      - /workspace/node_modules
    command: ["bash","-lc","npm ci && npx playwright install --with-deps && tail -f /dev/null"]

volumes:
  langfuse_db:
Bring up services:
docker compose up -d
# Proxy:   http://localhost:4000
# Langfuse: http://localhost:3001
 
Control Room (Next.js)
Purpose: Read-only dashboard for now; renders Factory docs; lists projects & each IDEAS.md.
Key files (repo control-room/):
control-room/
  app/
    layout.tsx           # Nav: Dashboard | Factory
    page.tsx             # Lists projects & their IDEAS.md
    factory/page.tsx     # Renders ../docs/COMMERCE_FACTORY.md + DIVISION.md
  components/Markdown.tsx
  lib/md.ts              # Markdown loader using remark/remark-html
  package.json
We added a Factory tab to render the two division docs read-only.
 
Orchestrator (Python + Pydantic)
Purpose: Load per-project configs, enforce loop pacing, route model calls via proxy (with tags for budgets), interact with mail threads, open PRs (never write to main directly).
Key files (repo orchestrator/):
orchestrator/
  pyproject.toml
  orchestrator.py              # Pydantic configs + async tick loop (skeleton)
  config/
    litellm.config.yaml        # Proxy routing & budgets
  pw-runner/
    package.json               # (future QA CLI wrapper)
config/litellm.config.yaml (excerpt):
general_settings:
  master_key: sk-local
litellm_settings:
  telemetry: False
  max_budget: 100.00 # global safety cap

model_list:
  - model_name: gemini-flash
    litellm_params:
      model: gemini/gemini-2.0-flash
      api_base: https://generativelanguage.googleapis.com
      api_key: ${GEMINI_API_KEY}
  - model_name: frontier-strong
    litellm_params:
      model: openai/gpt-4.1
      api_key: ${OPENAI_API_KEY}
  - model_name: cheap-fast
    litellm_params:
      model: together_ai/Meta-Llama-3.1-8B-Instruct
      api_key: ${TOGETHER_API_KEY}
orchestrator.py (high level):
•	Pydantic models for ProjectCfg, AgentCfg, GateCfg
•	load_projects() reads ../projects/*/project.yaml
•	litellm_chat() posts to http://localhost:4000/v1/chat/completions with tags (project, agent, phase) for budget accounting
•	process_mail() scans .mail/inbox/ and writes replies to .mail/outbox/ (skeleton)
•	tick_loop() runs per loop_interval_sec; later: budget tripwires, PR bot, Playwright job runner
Run:
cd orchestrator
python -m venv .venv && . .venv/Scripts/activate
pip install -e .
python orchestrator.py
 
Mail Bus (Git-backed threads + leases)
•	Use the MCP Agent Mail server from the referenced repo (run as a separate local process).
•	Functions:
o	Inbox/Outbox threads as Markdown files inside each project’s .mail/
o	File leases/claims to prevent simultaneous conflicting edits
o	Searchable history
•	We keep it pinned and run from source for supply-chain hygiene.
 
Per-Project Template (GLP-1 example)
Each project is its own repo under projects/. The GLP-1 repo serves as the template.
projects/glp1-companion/
  project.yaml
  AGENTS.md
  skills/
    brand_voice.md
    nutrition_styleguide.md
    web_research.md
    nextjs_conventions.md
    email_copy.md
    social_hooks.md
  docs/
    LLM_STACK.md
    PRD.md
    ARCH.md
    TESTPLAN.md
  ADRs/
    0001-adopt-mail-bus.md
  artifacts/
  .mail/
    inbox/
    outbox/
    qa/
  IDEAS.md
  web/
    app/page.tsx       # placeholder
  e2e/
    smoke.spec.ts      # placeholder
project.yaml (policy & routing per project):
project: glp1-companion
budget_usd: 25
loop_interval_sec: 10           # Control Room can bump to 120 during builds/tests
models:
  default: proxy://gemini-flash
  codegen: proxy://frontier-strong
  summarize: proxy://cheap-fast
  image: proxy://image-gen
agents:
  - name: architect
    skills: [product_prd, brand_voice]
  - name: researcher
    skills: [web_research, nutrition_styleguide]
  - name: frontend
    skills: [nextjs_conventions]
  - name: qa_browser
    mcp_tools: [playwright.run_e2e, playwright.screenshot]
  - name: growth
    skills: [email_copy, social_hooks]
gates:
  - on: deploy
    requires: human_approval
  - on: budget_90_percent
    requires: human_approval
mail:
  repo_subdir: .mail
  leases: enabled
outputs:
  artifacts_dir: ./artifacts
  email_provider: resend
AGENTS.md (roles & protocol):
•	Roles: Architect, Researcher, Frontend, QA Browser, Growth
•	Protocols:
o	All cross-agent comms via .mail/threads/*.md
o	Claim a file (lease) before edits
o	PR-only; no direct pushes to main
o	Major decisions recorded as ADRs
o	CI gates: Playwright green; <90% budget; Architect approval required for deploy
docs/LLM_STACK.md (replicated per project):
•	Declares which models are used for which tasks
•	Notes free-tier/key limits
•	Budget policy and tags
•	Allowed MCP servers & outbound domain allowlist
•	Change control rules (switching models requires ADR + approval)
 
Budgets, Pacing & Approvals
•	Budgets:
o	Hard per-project cap in LiteLLM proxy (global)
o	Per-agent soft caps by tagging requests (project, agent, phase)
o	At 90%, the Orchestrator pauses and opens an approval thread; resuming requires explicit human approval
•	Pacing:
o	Default loop interval 10s (idle & research)
o	120s during build/test phases (configurable via Control Room later)
•	Approvals (gates):
o	Deploys
o	Merges to main
o	Budget overrides
 
Security & Compliance
•	Per-project repos (isolation, easy archive/sale)
•	PR-only writes to main (bot account opens PRs)
•	Pin versions of the mail server & any MCP servers (run from source where feasible)
•	Key management: .env for Docker; project secrets for ESP/payments; least-privilege tokens
•	Outbound allowlist for network access from agents/tools
•	Privacy: double opt-in email flows; GDPR templates; cookie/consent for web
 
Runbook: First End-to-End Run
1.	Install prerequisites (Docker, Git, Node 20+, pnpm, Python 3.11+).
2.	Create folder layout and repos as shown above.
3.	Add provider keys to ai-factory/.env.
4.	Start shared services: docker compose up -d.
5.	Run Mail Bus: clone the MCP mail server and pnpm start (follow its README).
6.	Run Orchestrator: create venv, pip install -e ., python orchestrator.py.
7.	Run Control Room: pnpm install, pnpm dev (http://localhost:3099).
8.	Sanity checks:
o	Control Room Factory tab shows COMMERCE_FACTORY.md and DIVISION.md.
o	Dashboard lists glp1-companion.
o	Drop .mail/inbox/hello.md → orchestrator writes .mail/outbox/reply_hello.md.
o	See traces in Langfuse (http://localhost:3001).
o	(Optional) Open the Playwright container and verify npx playwright --version.
 
Roadmap & Backlog
Chapters
•	A — Foundation: Services, docs, skills, first PR loop (you are here)
•	B — Operate & Observe: Thread viewer, budget manager, QA pack, deploy via gates
•	C — Monetize: ESP flows, payments (Stripe/Lemon Squeezy), downloads, tax/receipts
•	D — Parallelize: Multiple project repos discovered automatically; portfolio view
•	E — Scale & Specialize: Off-peak scheduling, caching, model/skill packs, optional A2A adapter
Backlog Epics
•	Control Room UX (approvals, budgets, thread search, Ideas CRUD)
•	Orchestrator Core (state machine, PR bot, Playwright jobs, artifact ingester)
•	Content/Web (scaffolder, SEO, static export, responsive images)
•	Commerce (payments, fulfillment, VAT, affiliates, campaign analytics)
•	Research & Trends (MCP fetch/browser, citations, trend miner to IDEAS.md)
•	Security & Compliance (SBOM, key vault, allowlists, rotation cadence)
•	Reliability (health checks, circuit breakers, autoslow on failures)
 
Key Decisions & Rationale
1.	Per-project repos (not mono-repo):
o	Why: Isolation, easy archiving/transfer, lower cross-project risk.
2.	Mail bus + Git (vs in-memory):
o	Why: Auditable, searchable history; file leases prevent conflicts.
3.	Orchestrator runtime: Pydantic + asyncio (vs LangGraph):
o	Why: Thin, explicit, stable; typed configs; fewer moving parts.
4.	Model routing via LiteLLM proxy:
o	Why: Multi-vendor, budgets, tagging; task-aware escalation to stronger models.
5.	Approvals & pacing baked in:
o	Why: Human comprehension, cost control, safer deploys.
6.	Control Room read-only to start:
o	Why: Reduce foot-guns; add write actions (CRUD, approvals) incrementally.
7.	QA via Playwright container:
o	Why: Cross-browser, reliable CI semantics; artifacts fed back to threads/PRs.
 
Incident Handling
•	Triggers: Budget spike, failing tests, suspicious outbound requests, anomalous model latency/cost.
•	Immediate actions: Orchestrator pauses the project; opens INCIDENT.md thread in .mail/; posts summary + last actions + spend since last gate.
•	Human steps: Triage, decide resume/rollback, create ADR if policy or routing changes.
•	Follow-ups: Add test coverage, adjust budgets/loop interval, rotate keys if needed.
 
Glossary
•	Bet / Project: Self-contained repo with its own budget, skills, agents, and outputs.
•	Skill: Reusable specialization bundle (instructions/assets/scripts) loaded by an agent.
•	Gate: Human approval requirement (deploy, main merge, budget override).
•	Loop interval: Tick frequency for orchestrator task dispatch (e.g., 10s, 120s).
•	Mail bus: Git-backed messaging with file leases (inbox/outbox threads).
•	Proxy: LiteLLM gateway in front of multiple model providers.
•	Traces: Token/cost/latency events in Langfuse.
 
Quick Commands (Reference)
# From ai-factory/
docker compose up -d

# Mail bus (separate terminal, in its repo)
pnpm install && pnpm start

# Orchestrator
cd orchestrator
python -m venv .venv && . .venv/Scripts/activate
pip install -e .
python orchestrator.py

# Control Room
cd ../control-room
pnpm install && pnpm dev

# Sanity check
# 1) http://localhost:3099 (Dashboard & Factory tabs)
# 2) http://localhost:3001 (Langfuse)
# 3) ./projects/glp1-companion/.mail/inbox/hello.md → outbox reply
 
Add this file to docs/FOUNDATION_README.md. It stands as the single source of truth for setup, architecture, policies, and run procedures.

<img width="451" height="692" alt="image" src="https://github.com/user-attachments/assets/b21eb7f4-f0c0-47b7-a4a6-8c09ef5011bb" />
