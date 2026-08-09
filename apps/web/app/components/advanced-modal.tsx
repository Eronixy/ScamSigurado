"use client";

import { SlidersHorizontal, X } from "lucide-react";
import { useEffect, useRef, useState } from "react";

import {
  AnalysisSettings,
  defaultAnalysisSettings,
  useAnalysisSettings,
} from "./analysis-settings";

const textModels = [
  { value: "rf", label: "Random Forest" },
  { value: "svm", label: "Support Vector Machine" },
  { value: "nb", label: "Naive Bayes" },
] as const;
const imageModels = [
  { value: "vggnet", label: "VGG16" },
  { value: "resnet", label: "ResNet" },
  { value: "mobilenet", label: "MobileNet" },
  { value: "efficientnet", label: "EfficientNet" },
] as const;

export function AdvancedModal() {
  const { settings, setSettings } = useAnalysisSettings();
  const [isOpen, setIsOpen] = useState(false);
  const [draft, setDraft] = useState(settings);
  const closeButton = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!isOpen) return;
    closeButton.current?.focus();
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") setIsOpen(false);
    };
    window.addEventListener("keydown", closeOnEscape);
    return () => window.removeEventListener("keydown", closeOnEscape);
  }, [isOpen, settings]);

  function setTextWeight(value: number) {
    setDraft((current) => ({
      ...current,
      textWeight: value,
      imageWeight: Number((1 - value).toFixed(2)),
    }));
  }
  function save() {
    setSettings(draft);
    setIsOpen(false);
  }
  function reset() {
    setDraft({ ...defaultAnalysisSettings });
  }

  function open() {
    setDraft(settings);
    setIsOpen(true);
  }

  return (
    <>
      <button
        className="inline-flex items-center gap-2 border-[3px] border-black bg-[#FFD23F] px-3 py-2 font-black text-xs tracking-wider text-black shadow-[3px_3px_0px_0px_#000] transition-transform hover:-translate-x-0.5 hover:-translate-y-0.5 active:translate-x-1 active:translate-y-1 active:shadow-none uppercase"
        onClick={open}
        type="button"
      >
        <SlidersHorizontal aria-hidden="true" size={16} strokeWidth={3} />{" "}
        Advanced
      </button>
      {isOpen ? (
        <div
          className="fixed inset-0 z-50 grid place-items-center bg-black/65 p-4"
          onMouseDown={(event) => {
            if (event.target === event.currentTarget) setIsOpen(false);
          }}
        >
          <section
            aria-labelledby="advanced-title"
            aria-modal="true"
            className="w-full max-w-xl border-4 border-black bg-[#FFFDF5] p-6 text-black shadow-[6px_6px_0px_0px_#000] sm:p-8"
            role="dialog"
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="font-mono text-xs font-black tracking-widest uppercase">
                  Analysis setup
                </p>
                <h2
                  className="mt-1 font-black text-3xl tracking-[-0.06em]"
                  id="advanced-title"
                >
                  ADVANCED OPTIONS
                </h2>
              </div>
              <button
                aria-label="Close advanced options"
                className="grid h-10 w-10 shrink-0 place-items-center rounded-full border-[3px] border-black bg-[#FF6B6B] text-black shadow-[3px_3px_0px_0px_#000] active:translate-x-1 active:translate-y-1 active:shadow-none"
                onClick={() => setIsOpen(false)}
                ref={closeButton}
                type="button"
              >
                <X size={21} strokeWidth={3} />
              </button>
            </div>
            <div className="mt-6 grid gap-5 sm:grid-cols-2">
              <Field label="Text model">
                <select
                  className="w-full border-[3px] border-black bg-[#FFFDF5] p-3 font-bold"
                  onChange={(event) =>
                    setDraft((current) => ({
                      ...current,
                      textModel: event.target
                        .value as AnalysisSettings["textModel"],
                    }))
                  }
                  value={draft.textModel}
                >
                  {textModels.map((model) => (
                    <option key={model.value} value={model.value}>
                      {model.label}
                    </option>
                  ))}
                </select>
              </Field>
              <Field label="Image model">
                <select
                  className="w-full border-[3px] border-black bg-[#FFFDF5] p-3 font-bold"
                  onChange={(event) =>
                    setDraft((current) => ({
                      ...current,
                      imageModel: event.target
                        .value as AnalysisSettings["imageModel"],
                    }))
                  }
                  value={draft.imageModel}
                >
                  {imageModels.map((model) => (
                    <option key={model.value} value={model.value}>
                      {model.label}
                    </option>
                  ))}
                </select>
              </Field>
            </div>
            <div className="mt-6 border-[3px] border-black bg-[#B8A9FA] p-4">
              <div className="flex items-center justify-between">
                <h3 className="font-black uppercase">Model weight</h3>
                <span className="font-mono text-sm font-black">
                  {Math.round(draft.textWeight * 100)}% text /{" "}
                  {Math.round(draft.imageWeight * 100)}% image
                </span>
              </div>
              <label className="mt-4 block font-bold" htmlFor="text-weight">
                Text analysis priority
              </label>
              <input
                className="mt-2 w-full accent-black"
                id="text-weight"
                max="100"
                min="0"
                onChange={(event) =>
                  setTextWeight(Number(event.target.value) / 100)
                }
                type="range"
                value={Math.round(draft.textWeight * 100)}
              />
            </div>
            <div className="mt-6 flex flex-wrap justify-end gap-3">
              <button
                className="border-[3px] border-black bg-[#FFFDF5] px-4 py-3 font-black shadow-[3px_3px_0px_0px_#000] active:translate-x-1 active:translate-y-1 active:shadow-none"
                onClick={reset}
                type="button"
              >
                RESET TO DEFAULTS
              </button>
              <button
                className="border-[4px] border-black bg-[#B8A9FA] px-4 py-3 font-black tracking-wider text-black shadow-[5px_5px_0px_0px_#000] transition-transform hover:-translate-x-0.5 hover:-translate-y-0.5 active:translate-x-1 active:translate-y-1 active:shadow-none"
                onClick={save}
                type="button"
              >
                SAVE SETTINGS
              </button>
            </div>
          </section>
        </div>
      ) : null}
    </>
  );
}

function Field({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <label className="block font-black">
      <span className="mb-2 block text-sm uppercase">{label}</span>
      {children}
    </label>
  );
}
