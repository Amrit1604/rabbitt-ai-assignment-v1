import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Sales Insight Automator",
  description: "Upload sales data, receive an AI-generated summary in your inbox.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
