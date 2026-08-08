"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { AnalysisResult, apiUrl, getErrorMessage } from "../lib/api";

export function AnalysisResultView({ analysisId }: { analysisId: string }) {
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [feedbackState, setFeedbackState] = useState<"idle" | "sending" | "sent">("idle");

  useEffect(() => {
    let isActive = true;

    async function loadAnalysis() {
      try {
        const response = await fetch(apiUrl(`/v1/analyses/${analysisId}`), { cache: "no-store" });
        if (!response.ok) {
          throw new Error(await getErrorMessage(response));
        }
        const nextAnalysis = (await response.json()) as AnalysisResult;
        if (isActive) {
          setAnalysis(nextAnalysis);
        }
      } catch (loadError) {
        if (isActive) {
          setError(loadError instanceof Error ? loadError.message : "We could not load this result.");
        }
      }
    }

    loadAnalysis();
    return () => {
      isActive = false;
    };
  }, [analysisId]);

  async function submitFeedback(wasResultAccurate: boolean) {
    setFeedbackState("sending");
    try {
      const response = await fetch(apiUrl("/v1/feedback"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ analysis_id: analysisId, was_result_accurate: wasResultAccurate }),
      });
      if (!response.ok) {
        throw new Error(await getErrorMessage(response));
      }
      setFeedbackState("sent");
    } catch {
      setFeedbackState("idle");
    }
  }

  if (error) {
    return <ErrorState message={error} />;
  }

  if (!analysis || analysis.status === "processing") {
    return (
      <section className="panel status-card" aria-live="polite">
        <div className="spinner" />
        <h1 className="result-heading">Checking your screenshot</h1>
        <p className="result-meta">This can take a moment while we read and evaluate the image.</p>
      </section>
    );
  }

  if (analysis.status === "failed" || !analysis.prediction) {
    return <ErrorState message="We could not complete this screenshot check. Please try another image." />;
  }

  const isScam = analysis.prediction === "scam";
  const signalWords = unique([...analysis.high_risk_keywords, ...analysis.feature_importance.slice(0, 5).map(({ word }) => word)]);

  return (
    <>
      <section className={`panel result-card ${isScam ? "is-scam" : "is-legitimate"}`}>
        <div className="result-header">
          <div>
            <p className="result-label">{isScam ? "Use caution" : "No strong scam signal"}</p>
            <h1 className="result-heading">{isScam ? "Potential scam detected" : "Appears legitimate"}</h1>
          </div>
          <div className="confidence">
            <strong>{Math.round((analysis.confidence ?? 0) * 100)}%</strong>
            <span className="result-meta">confidence</span>
          </div>
        </div>
        <p className="result-summary">
          {isScam
            ? "This screenshot contains signals commonly used in scam attempts. Do not share codes, passwords, or money until you verify the sender independently."
            : "We did not find strong scam signals in this screenshot. Still verify unexpected requests through an official channel."}
        </p>
      </section>

      <section className="details-grid" aria-label="Analysis details">
        <article className="panel signal-card">
          <h2>Signals found</h2>
          {signalWords.length ? (
            <div className="chip-list">
              {signalWords.map((signal) => <span className="chip" key={signal}>{signal}</span>)}
            </div>
          ) : <p className="result-meta">No readable high-risk phrases were found.</p>}
        </article>
        <article className="panel signal-card">
          <h2>Links found</h2>
          {analysis.detected_urls.length ? (
            <div className="chip-list">
              {analysis.detected_urls.map((url) => <span className="chip" key={url}>{url}</span>)}
            </div>
          ) : <p className="result-meta">No links were detected in the readable text.</p>}
        </article>
      </section>

      {analysis.extracted_text ? (
        <section className="panel signal-card" style={{ marginTop: "1rem" }}>
          <h2>Text read from the screenshot</h2>
          <pre className="extracted-text">{analysis.extracted_text}</pre>
        </section>
      ) : null}

      <section className="panel feedback">
        {feedbackState === "sent" ? (
          <p>Thank you. Your feedback helps us improve the service.</p>
        ) : (
          <>
            <p>Was this result helpful?</p>
            <div className="feedback-actions">
              <button className="button button-secondary" disabled={feedbackState === "sending"} onClick={() => submitFeedback(true)} type="button">Yes</button>
              <button className="button button-secondary" disabled={feedbackState === "sending"} onClick={() => submitFeedback(false)} type="button">Not really</button>
            </div>
          </>
        )}
      </section>

      <div className="button-row">
        <Link className="button button-primary" href="/">Check another screenshot</Link>
      </div>
    </>
  );
}

function ErrorState({ message }: { message: string }) {
  return (
    <section className="panel status-card">
      <p className="eyebrow">Unable to load result</p>
      <h1 className="result-heading">Let&apos;s try that again.</h1>
      <p className="result-meta">{message}</p>
      <div className="button-row">
        <Link className="button button-primary" href="/">Return to upload</Link>
      </div>
    </section>
  );
}

function unique(items: string[]) {
  return [...new Set(items.filter(Boolean))];
}
