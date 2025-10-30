import fs from "node:fs";
import path from "node:path";

const ROOT = path.join(process.cwd(), "..");

export function resolveWorkspacePath(relativePath: string): string {
  return path.join(ROOT, relativePath);
}

export function readWorkspaceFile(relativePath: string): string | null {
  const fullPath = resolveWorkspacePath(relativePath);
  if (!fs.existsSync(fullPath)) {
    return null;
  }
  return fs.readFileSync(fullPath, "utf-8");
}

export type InboxThread = {
  name: string;
  relativePath: string;
  updatedAt: string;
  preview: string;
};

export function readInboxThreads(relativeInboxPath: string): InboxThread[] {
  const inboxPath = resolveWorkspacePath(relativeInboxPath);
  if (!fs.existsSync(inboxPath)) {
    return [];
  }

  const entries = fs
    .readdirSync(inboxPath, { withFileTypes: true })
    .filter((dirent) => dirent.isFile() && dirent.name.endsWith(".md"));

  return entries
    .map((entry) => {
      const filePath = path.join(inboxPath, entry.name);
      const content = fs.readFileSync(filePath, "utf-8");
      const stats = fs.statSync(filePath);
      const lines = content
        .split("\n")
        .map((line) => line.trim())
        .filter(Boolean);
      const previewLines = lines.slice(0, 3);
      if (lines.length > previewLines.length) {
        previewLines.push("…");
      }
      return {
        name: entry.name,
        relativePath: path.join(relativeInboxPath, entry.name),
        updatedAt: new Date(stats.mtime).toISOString(),
        preview: previewLines.join("\n"),
      } satisfies InboxThread;
    })
    .sort((a, b) => (a.updatedAt < b.updatedAt ? 1 : -1));
}
