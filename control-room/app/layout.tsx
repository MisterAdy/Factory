import "./globals.css";
import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Commerce Factory Control Room",
  description: "Read-only dashboard for monitoring agent projects",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <header className="layout__header">
          <h1>Commerce Factory Control Room</h1>
          <nav>
            <Link href="/">Dashboard</Link>
            <Link href="/factory">Factory Docs</Link>
          </nav>
        </header>
        <main className="layout__main">{children}</main>
      </body>
    </html>
  );
}
