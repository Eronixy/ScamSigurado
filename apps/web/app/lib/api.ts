export type AnalysisStatus = "processing" | "completed" | "failed";

export type FeatureImportance = {
  word: string;
  importance: number;
};

export type AnalysisResult = {
  id: string;
  status: AnalysisStatus;
  prediction: "scam" | "legitimate" | null;
  scam_risk: number | null;
  text_confidence: number | null;
  image_confidence: number | null;
  extracted_text: string | null;
  feature_importance: FeatureImportance[];
  detected_urls: string[];
  high_risk_keywords: string[];
  model_version: string | null;
  created_at: string;
  completed_at: string | null;
  expires_at: string;
};

const apiBaseUrl = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(/\/$/, "");

export function apiUrl(path: string) {
  return `${apiBaseUrl}${path}`;
}

export async function getErrorMessage(response: Response) {
  const payload = await response.json().catch(() => null);
  return typeof payload?.detail === "string" ? payload.detail : "Something went wrong. Please try again.";
}
