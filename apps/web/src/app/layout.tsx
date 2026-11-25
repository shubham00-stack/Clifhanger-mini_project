import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Cliffhanger Strength Analyzer — Narrative Suspense & Continuity Workspace",
  description: "Enterprise-grade explainable AI workspace evaluating narrative tension, stakes, and cliffhanger cutoffs across 9 calibrated dimensions.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-[#0d0d0f] text-[#ececee] min-h-screen antialiased select-auto">
        {children}
      </body>
    </html>
  );
}
