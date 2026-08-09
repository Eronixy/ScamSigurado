"use client";

import { createContext, useContext, useState } from "react";

export type AnalysisSettings = {
  textModel: "rf" | "svm" | "nb";
  imageModel: "vggnet" | "resnet" | "mobilenet" | "efficientnet";
  textWeight: number;
  imageWeight: number;
};

export const defaultAnalysisSettings: AnalysisSettings = {
  textModel: "rf",
  imageModel: "vggnet",
  textWeight: 0.7,
  imageWeight: 0.3,
};
const AnalysisSettingsContext = createContext<{
  settings: AnalysisSettings;
  setSettings: (settings: AnalysisSettings) => void;
} | null>(null);

export function AnalysisSettingsProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [settings, setSettings] = useState(defaultAnalysisSettings);
  return (
    <AnalysisSettingsContext.Provider value={{ settings, setSettings }}>
      {children}
    </AnalysisSettingsContext.Provider>
  );
}

export function useAnalysisSettings() {
  const context = useContext(AnalysisSettingsContext);
  if (!context)
    throw new Error(
      "useAnalysisSettings must be used within AnalysisSettingsProvider",
    );
  return context;
}
