import type { ReactNode } from "react";
import "./globals.css";

export const metadata = {
  title: "N-ATLAS Chat Starter",
  description: "Multilingual chat in English, Hausa, Igbo and Yoruba, powered by N-ATLAS",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
