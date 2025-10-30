import Link from "next/link";
import projects from "../data/projects";

export default function DashboardPage() {
  const formatter = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  });
  return (
    <section className="card-grid">
      {projects.map((project) => (
        <article className="card" key={project.slug}>
          <h2>{project.name}</h2>
          <p>{project.summary}</p>
          <ul>
            <li>Status: {project.status}</li>
            <li>Phase: {project.phase}</li>
            <li>
              Budget Burn: {formatter.format(project.budget.burned)} /{" "}
              {formatter.format(project.budget.cap)} (
              {project.budget.cap > 0
                ? Math.round((project.budget.burned / project.budget.cap) * 100)
                : 0}
              %)
            </li>
          </ul>
          <Link href={`/projects/${project.slug}`}>View project</Link>
        </article>
      ))}
    </section>
  );
}
