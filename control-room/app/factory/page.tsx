import Markdown from "../../components/Markdown";
import { readWorkspaceFile } from "../../lib/workspace";

const DOCS: { title: string; path: string }[] = [
  { title: "Foundation README", path: "docs/FOUNDATION_README.md" },
  { title: "Commerce Factory", path: "docs/COMMERCE_FACTORY.md" },
  { title: "Division Charter", path: "docs/DIVISION.md" },
  { title: "Product Roadmap", path: "docs/ProductRoadmap.md" },
];

export default function FactoryDocsPage() {
  return (
    <section className="card-grid">
      {DOCS.map((doc) => {
        const content = readWorkspaceFile(doc.path);
        return (
          <article className="card" key={doc.path}>
            <h2>{doc.title}</h2>
            {content ? (
              <Markdown>{content}</Markdown>
            ) : (
              <p>Missing document: {doc.path}</p>
            )}
          </article>
        );
      })}
    </section>
  );
}
