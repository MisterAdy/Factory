export type Project = {
  slug: string;
  name: string;
  summary: string;
  status: "active" | "paused" | "archived";
  phase: string;
  budget: {
    cap: number;
    burned: number;
  };
  inboxPath: string;
  docs: string[];
};

const projects: Project[] = [
  {
    slug: "glp1-companion",
    name: "GLP-1 Companion",
    summary: "A validation companion providing research, compliance, and UX flows for GLP-1 seekers.",
    status: "active",
    phase: "VALIDATE",
    budget: { cap: 500, burned: 12 },
    inboxPath: "projects/glp1-companion/.mail/inbox",
    docs: [
      "docs/FOUNDATION_README.md",
      "docs/COMMERCE_FACTORY.md",
      "docs/DIVISION.md",
      "docs/ProductRoadmap.md",
    ],
  },
];

export default projects;
