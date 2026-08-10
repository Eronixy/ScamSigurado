"use client";

import { AnimatePresence, motion } from "framer-motion";
import {
  AlertTriangle,
  ArrowUpRight,
  BadgeCheck,
  CircleHelp,
  FileText,
  Link2,
  LoaderCircle,
  MessageSquareText,
  RotateCcw,
  ShieldAlert,
} from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

import { AnalysisResult, apiUrl, getErrorMessage } from "../lib/api";
import { IconPill } from "./icon-pill";

export function AnalysisResultView({ analysisId }: { analysisId: string }) {
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [feedbackState, setFeedbackState] = useState<
    "idle" | "sending" | "sent"
  >("idle");

  useEffect(() => {
    let isActive = true;
    async function loadAnalysis() {
      try {
        const response = await fetch(apiUrl(`/v1/analyses/${analysisId}`), {
          cache: "no-store",
        });
        if (!response.ok) throw new Error(await getErrorMessage(response));
        if (isActive) setAnalysis((await response.json()) as AnalysisResult);
      } catch (loadError) {
        if (isActive)
          setError(
            loadError instanceof Error
              ? loadError.message
              : "WE COULD NOT LOAD THIS RESULT.",
          );
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
        body: JSON.stringify({
          analysis_id: analysisId,
          was_result_accurate: wasResultAccurate,
        }),
      });
      if (!response.ok) throw new Error(await getErrorMessage(response));
      setFeedbackState("sent");
    } catch {
      setFeedbackState("idle");
    }
  }

  if (error) return <ErrorState message={error} />;
  if (!analysis || analysis.status === "processing") return <LoadingState />;
  if (analysis.status === "failed" || !analysis.prediction)
    return (
      <ErrorState message="THE CHECK COULD NOT FINISH. TRY A DIFFERENT IMAGE." />
    );

  const isScam = analysis.prediction === "scam";
  const signalWords = unique([
    ...analysis.high_risk_keywords,
    ...analysis.feature_importance.slice(0, 5).map(({ word }) => word),
  ]);
  const outcome = isScam
    ? {
        kicker: "PAUSE RIGHT THERE",
        title: "POTENTIAL SCAM.",
        icon: AlertTriangle,
        surface: "bg-[#FF6B6B]",
        sticker: "DO NOT PAY",
      }
    : {
        kicker: "NO BIG RED FLAGS",
        title: "LOOKS CLEAR.",
        icon: BadgeCheck,
        surface: "bg-[#B8A9FA]",
        sticker: "STILL VERIFY",
      };

  return (
    <div className="space-y-6 text-black">
      <motion.section
        animate={{ opacity: 1, y: 0 }}
        className={`relative border-[4px] border-black ${outcome.surface} p-5 shadow-[8px_8px_0px_0px_#000] sm:p-7`}
        initial={{ opacity: 0, y: 22 }}
        transition={{ type: "spring", stiffness: 220, damping: 20 }}
      >
        <span className="absolute -right-2 -top-4 rotate-3 border-[3px] border-black bg-[#FFFDF5] px-3 py-1.5 font-black text-xs tracking-wider shadow-[3px_3px_0px_0px_#000] uppercase">
          {outcome.sticker}
        </span>
        <div className="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <div className="flex items-center gap-3">
              <IconPill
                icon={outcome.icon}
                label={outcome.kicker}
                tone="paper"
              />
              <p className="font-black text-xs tracking-[0.16em] uppercase">
                {outcome.kicker}
              </p>
            </div>
            <h1 className="mt-5 font-black text-5xl leading-[0.86] tracking-[-0.09em] sm:text-7xl">
              {outcome.title}
            </h1>
          </div>
          <div className="w-fit border-[4px] border-black bg-[#FFFDF5] px-4 py-3 text-center shadow-[4px_4px_0px_0px_#000]">
            <strong className="block font-mono text-3xl font-black">
              {Math.round((analysis.scam_risk ?? 0) * 100)}%
            </strong>
            <span className="font-black text-[0.65rem] tracking-widest uppercase">
              scam risk
            </span>
          </div>
        </div>
        <p className="mt-6 max-w-3xl border-l-4 border-black pl-4 font-bold leading-relaxed">
          {isScam
            ? "This screenshot carries signals often used in scam attempts. Do not send money, codes, passwords, or personal details until you independently verify the sender."
            : "We did not find strong scam signals in this screenshot. Treat unexpected money or account requests carefully and verify through an official channel."}
        </p>
      </motion.section>
      <section className="grid gap-5 lg:grid-cols-[1.1fr_0.9fr]">
        <InfoCard
          icon={ShieldAlert}
          kicker="READ THIS"
          title="Signals found"
          tone="paper"
        >
          {signalWords.length ? (
            <div className="mt-5 flex flex-wrap gap-2">
              {signalWords.map((signal) => (
                <span
                  className="rounded-full border-[3px] border-black bg-[#FFD23F] px-3 py-1 font-mono text-xs font-black uppercase"
                  key={signal}
                >
                  {signal}
                </span>
              ))}
            </div>
          ) : (
            <p className="mt-5 border-[3px] border-black bg-[#B8A9FA] p-3 font-bold">
              NO READABLE HIGH-RISK PHRASES WERE FOUND.
            </p>
          )}
        </InfoCard>
        <InfoCard
          icon={Link2}
          kicker="CHECK THE URL"
          title="Links found"
          tone="lavender"
        >
          {analysis.detected_urls.length ? (
            <div className="mt-5 flex flex-wrap gap-2">
              {analysis.detected_urls.map((url) => (
                <span
                  className="max-w-full overflow-wrap-anywhere rounded-full border-[3px] border-black bg-[#FFFDF5] px-3 py-1 font-mono text-xs font-black"
                  key={url}
                >
                  {url}
                </span>
              ))}
            </div>
          ) : (
            <p className="mt-5 border-[3px] border-black bg-[#FFFDF5] p-3 font-bold">
              NO LINKS SHOWED UP IN THE READABLE TEXT.
            </p>
          )}
        </InfoCard>
      </section>
      {analysis.extracted_text ? (
        <InfoCard
          icon={FileText}
          kicker="WHAT WE READ"
          title="Screenshot text"
          tone="paper"
        >
          <pre className="mt-5 max-h-60 overflow-auto border-[3px] border-black bg-[#B8A9FA] p-4 font-mono text-sm font-bold whitespace-pre-wrap">
            {analysis.extracted_text}
          </pre>
        </InfoCard>
      ) : null}
      <section className="border-[4px] border-black bg-[#FFD23F] p-5 shadow-[6px_6px_0px_0px_#000] sm:flex sm:items-center sm:justify-between sm:gap-6">
        <div className="flex items-center gap-3">
          <IconPill icon={MessageSquareText} label="Feedback" tone="paper" />
          <div>
            <p className="font-black text-xs tracking-wider uppercase">
              QUICK CHECK
            </p>
            <h2 className="font-black text-2xl tracking-[-0.06em]">
              WAS THIS USEFUL?
            </h2>
          </div>
        </div>
        <AnimatePresence mode="wait" initial={false}>
          {feedbackState === "sent" ? (
            <motion.p
              animate={{ opacity: 1, rotate: 0 }}
              className="mt-4 border-[3px] border-black bg-[#FFFDF5] px-3 py-2 font-black sm:mt-0"
              initial={{ opacity: 0, rotate: -3 }}
            >
              FEEDBACK LOCKED IN. THANKS.
            </motion.p>
          ) : (
            <motion.div
              animate={{ opacity: 1 }}
              className="mt-4 flex flex-wrap gap-2 sm:mt-0"
              initial={{ opacity: 0 }}
            >
              <button
                className="tactile-button border-[3px] border-black bg-[#FFFDF5] px-3 py-2 font-black shadow-[3px_3px_0px_0px_#000] disabled:opacity-50"
                disabled={feedbackState === "sending"}
                onClick={() => submitFeedback(true)}
                type="button"
              >
                YES
              </button>
              <button
                className="tactile-button border-[3px] border-black bg-[#FF6B6B] px-3 py-2 font-black shadow-[3px_3px_0px_0px_#000] disabled:opacity-50"
                disabled={feedbackState === "sending"}
                onClick={() => submitFeedback(false)}
                type="button"
              >
                NOT REALLY
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </section>
      <Link
        className="inline-flex items-center gap-3 border-[4px] border-black bg-[#B8A9FA] px-4 py-3 font-black tracking-wider text-black shadow-[6px_6px_0px_0px_#000] transition-transform hover:-translate-x-0.5 hover:-translate-y-0.5 active:translate-x-1 active:translate-y-1 active:shadow-none"
        href="/"
      >
        <IconPill
          icon={RotateCcw}
          label="Check another screenshot"
          tone="yellow"
        />{" "}
        CHECK ANOTHER SCREENSHOT <ArrowUpRight size={21} strokeWidth={3} />
      </Link>
    </div>
  );
}

function InfoCard({
  icon,
  kicker,
  title,
  tone,
  children,
}: {
  icon: typeof ShieldAlert;
  kicker: string;
  title: string;
  tone: "paper" | "lavender";
  children: React.ReactNode;
}) {
  const surface = tone === "lavender" ? "bg-[#B8A9FA]" : "bg-[#FFFDF5]";
  return (
    <motion.article
      animate={{ opacity: 1, y: 0 }}
      className={`border-[4px] border-black ${surface} p-5 shadow-[6px_6px_0px_0px_#000]`}
      initial={{ opacity: 0, y: 18 }}
    >
      <div className="flex items-center gap-3">
        <IconPill
          icon={icon}
          label={title}
          tone={tone === "lavender" ? "yellow" : "lavender"}
        />
        <div>
          <p className="font-mono text-xs font-black">{kicker}</p>
          <h2 className="font-black text-xl tracking-[-0.05em] uppercase">
            {title}
          </h2>
        </div>
      </div>
      {children}
    </motion.article>
  );
}
function LoadingState() {
  return (
    <section className="border-[4px] border-black bg-[#FFD23F] p-6 text-black shadow-[8px_8px_0px_0px_#000] sm:p-10">
      <div className="flex items-center gap-4">
        <IconPill
          icon={LoaderCircle}
          label="Analysis in progress"
          tone="paper"
        />
        <div>
          <p className="font-mono text-xs font-black">RUNNING THE CHECK</p>
          <h1 className="font-black text-4xl leading-none tracking-[-0.08em] sm:text-6xl">
            SCANNING...
          </h1>
        </div>
      </div>
      <p className="mt-6 border-l-4 border-black pl-3 font-bold">
        READING TEXT + CHECKING IMAGE SIGNALS. KEEP THIS TAB OPEN.
      </p>
    </section>
  );
}
function ErrorState({ message }: { message: string }) {
  return (
    <section className="border-[4px] border-black bg-[#FF6B6B] p-6 text-black shadow-[8px_8px_0px_0px_#000] sm:p-10">
      <div className="flex items-start gap-4">
        <IconPill
          icon={CircleHelp}
          label="Unable to load result"
          tone="paper"
        />
        <div>
          <p className="font-black text-xs tracking-wider uppercase">
            CHECK INTERRUPTED
          </p>
          <h1 className="mt-2 font-black text-4xl leading-none tracking-[-0.08em] sm:text-6xl">
            TRY THAT AGAIN.
          </h1>
          <p className="mt-4 max-w-xl font-bold">{message}</p>
        </div>
      </div>
      <Link
        className="mt-7 inline-flex items-center gap-3 border-[4px] border-black bg-[#FFFDF5] px-4 py-3 font-black tracking-wider text-black shadow-[5px_5px_0px_0px_#000] transition-transform hover:-translate-x-0.5 hover:-translate-y-0.5 active:translate-x-1 active:translate-y-1 active:shadow-none"
        href="/"
      >
        <IconPill icon={RotateCcw} label="Return to upload" tone="yellow" />{" "}
        RETURN TO UPLOAD
      </Link>
    </section>
  );
}
function unique(items: string[]) {
  return [...new Set(items.filter(Boolean))];
}
