"use client";

import { AnalysisSettingsProvider } from "./components/analysis-settings";

export function Providers({ children }: { children: React.ReactNode }) {
  return <AnalysisSettingsProvider>{children}</AnalysisSettingsProvider>;
}
