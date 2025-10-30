"use client";

import type { ComponentProps } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export type MarkdownProps = {
  children: string;
} & Omit<ComponentProps<typeof ReactMarkdown>, "children">;

export default function Markdown({ children, ...props }: MarkdownProps) {
  return (
    <ReactMarkdown
      className="markdown"
      remarkPlugins={[remarkGfm]}
      {...props}
    >
      {children}
    </ReactMarkdown>
  );
}
