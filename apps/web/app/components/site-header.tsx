import Link from "next/link";

import { ThemeToggle } from "./theme-toggle";

export function SiteHeader() {
  return (
    <>
      <Link aria-label="ScamSigurado home" className="brand" href="/">
        <span aria-hidden="true" className="brand-mark">✓</span>
        <span>ScamSigurado</span>
      </Link>
      <ThemeToggle />
    </>
  );
}
