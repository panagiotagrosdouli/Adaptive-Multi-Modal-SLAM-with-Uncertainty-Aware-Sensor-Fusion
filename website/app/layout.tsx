import "./globals.css";
import type { Metadata } from "next";
import type { ReactNode } from "react";

export const metadata: Metadata = {
  title: "Adaptive Multi-Modal SLAM",
  description:
    "Research website for adaptive multi-modal SLAM with uncertainty-aware sensor fusion.",
  openGraph: {
    title: "Adaptive Multi-Modal SLAM",
    description:
      "Online sensor reliability estimation, adaptive fusion, and benchmark discipline for SLAM research.",
    type: "website",
  },
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
