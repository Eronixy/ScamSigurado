"use client";

import { useCallback, useEffect, useState } from "react";

export const analysisStatuses = [
  "Dispatching payload to Public API Gateway...",
  "Extracting text content from screenshot...",
  "Routing request to private ML runtime...",
  "Computing multimodal scam risk score...",
] as const;

export function useAnalysisModal() {
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState<string>(analysisStatuses[0]);

  useEffect(() => {
    if (!isLoading) return;
    const originalOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => { document.body.style.overflow = originalOverflow; };
  }, [isLoading]);

  const showLoading = useCallback(() => {
    setStatus(analysisStatuses[0]);
    setIsLoading(true);
  }, []);
  const hideLoading = useCallback(() => setIsLoading(false), []);
  const updateLoadingStatus = useCallback((message: string) => setStatus(message), []);

  return { isLoading, status, showLoading, hideLoading, updateLoadingStatus };
}
