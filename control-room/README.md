# Control Room

Next.js dashboard that surfaces Commerce Factory documents, projects, and health information.

## Prerequisites

* Node.js 20+
* pnpm (recommended) or npm

## Getting Started

```bash
pnpm install
pnpm dev
```

The development server runs on http://localhost:3099. Update `package.json` if you need to change the port.

Project metadata lives in `data/projects.ts`. The `/factory` page renders shared documents from the repository root with Markdown support, mirroring the setup guide in `docs/`. Individual project pages surface live inbox threads from the Git-backed mail bus so you can track incoming work without leaving the dashboard.
