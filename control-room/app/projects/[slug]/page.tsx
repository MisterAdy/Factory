import Link from "next/link";

import projects from "../../../data/projects";
import { readInboxThreads } from "../../../lib/workspace";

export default function ProjectPage({ params }: { params: { slug: string } }) {
  const project = projects.find((item) => item.slug === params.slug);

  if (!project) {
    return (
      <section>
        <h2>Project not found</h2>
        <p>The requested project does not exist. Return to the dashboard.</p>
        <Link href="/">Back to dashboard</Link>
      </section>
    );
  }

  const threads = readInboxThreads(project.inboxPath);
  const formatter = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  });
  const burnPercent =
    project.budget.cap > 0
      ? Math.round((project.budget.burned / project.budget.cap) * 100)
      : 0;

  return (
    <section className="card">
      <h2>{project.name}</h2>
      <p>{project.summary}</p>
      <dl className="project-meta">
        <div>
          <dt>Status</dt>
          <dd>{project.status}</dd>
        </div>
        <div>
          <dt>Phase</dt>
          <dd>{project.phase}</dd>
        </div>
        <div>
          <dt>Budget</dt>
          <dd>
            {formatter.format(project.budget.burned)} / {formatter.format(project.budget.cap)} ({
              burnPercent
            }
            %)
          </dd>
        </div>
      </dl>
      <section>
        <h3>Active Threads</h3>
        {threads.length === 0 ? (
          <p>No inbound threads yet.</p>
        ) : (
          <ul className="thread-list">
            {threads.map((thread) => (
              <li key={thread.relativePath}>
                <strong>{thread.name}</strong>
                <span>{new Date(thread.updatedAt).toLocaleString()}</span>
                <p>{thread.preview}</p>
              </li>
            ))}
          </ul>
        )}
      </section>
      <section>
        <h3>Docs</h3>
        <ul>
          {project.docs.map((doc) => (
            <li key={doc}>
              <Link href={`/docs/${doc}`} prefetch={false}>
                {doc}
              </Link>
            </li>
          ))}
        </ul>
      </section>
    </section>
  );
}
