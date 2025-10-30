import Link from "next/link";

import Markdown from "../../../components/Markdown";
import { readWorkspaceFile } from "../../../lib/workspace";

export default function DocPage({ params }: { params: { slug: string[] } }) {
  const relativePath = params.slug.join("/");
  const content = readWorkspaceFile(relativePath);

  return (
    <section className="card">
      <h2>{relativePath}</h2>
      {content ? <Markdown>{content}</Markdown> : <p>Document not found.</p>}
      <Link href="/factory">Back to factory docs</Link>
    </section>
  );
}
