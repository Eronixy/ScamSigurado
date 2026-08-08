import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ScamSigurado",
  description: "Check a screenshot for potential scam signals.",
};

const themeScript = `
  try {
    const savedTheme = localStorage.getItem("scamsigurado-theme");
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    document.documentElement.classList.toggle("dark", savedTheme ? savedTheme === "dark" : prefersDark);
  } catch (_) {}
`;

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
      </head>
      <body>{children}</body>
    </html>
  );
}
