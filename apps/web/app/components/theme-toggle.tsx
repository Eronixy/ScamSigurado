"use client";

import { useEffect, useState } from "react";

const storageKey = "scamsigurado-theme";

export function ThemeToggle() {
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    setIsDark(document.documentElement.classList.contains("dark"));
  }, []);

  function toggleTheme() {
    const nextTheme = !isDark;
    document.documentElement.classList.toggle("dark", nextTheme);
    localStorage.setItem(storageKey, nextTheme ? "dark" : "light");
    setIsDark(nextTheme);
  }

  return (
    <button
      aria-label={isDark ? "Switch to light mode" : "Switch to dark mode"}
      aria-pressed={isDark}
      className="theme-toggle"
      onClick={toggleTheme}
      type="button"
    >
      <span aria-hidden="true">{isDark ? "☀" : "◐"}</span>
    </button>
  );
}
