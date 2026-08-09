"use client";

/* Local object URLs cannot be handled by next/image's optimizer. */
/* eslint-disable @next/next/no-img-element */

import { AnimatePresence, motion } from "framer-motion";
import { ArrowUpRight, Crop, FileImage, ShieldAlert, X } from "lucide-react";
import { ChangeEvent, FormEvent, useRef, useState } from "react";
import { useRouter } from "next/navigation";

import { apiUrl, getErrorMessage } from "../lib/api";
import {
  analysisStatuses,
  useAnalysisModal,
} from "../hooks/use-analysis-modal";
import { useAnalysisSettings } from "./analysis-settings";
import { CropModal } from "./crop-modal";
import { IconPill } from "./icon-pill";
import { LoadingModal } from "./loading-modal";

const maxFileSize = 10 * 1024 * 1024;

export function UploadPanel() {
  const fileInput = useRef<HTMLInputElement>(null);
  const previewUrlRef = useRef<string | null>(null);
  const router = useRouter();
  const { settings } = useAnalysisSettings();
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isCropping, setIsCropping] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { isLoading, status, showLoading, hideLoading, updateLoadingStatus } =
    useAnalysisModal();

  function setPreview(nextFile: File) {
    if (previewUrlRef.current) URL.revokeObjectURL(previewUrlRef.current);
    const nextUrl = URL.createObjectURL(nextFile);
    previewUrlRef.current = nextUrl;
    setPreviewUrl(nextUrl);
  }

  function selectFile(nextFile: File | null) {
    setError(null);
    if (!nextFile) return;
    if (!["image/jpeg", "image/png"].includes(nextFile.type)) {
      setFile(null);
      setError("DROP A PNG OR JPEG ONLY.");
      return;
    }
    if (nextFile.size > maxFileSize) {
      setFile(null);
      setError("THAT FILE IS OVER THE 10 MB LIMIT.");
      return;
    }
    setFile(nextFile);
    setPreview(nextFile);
  }

  function onFileChange(event: ChangeEvent<HTMLInputElement>) {
    selectFile(event.target.files?.[0] ?? null);
  }
  function removeFile() {
    if (previewUrlRef.current) URL.revokeObjectURL(previewUrlRef.current);
    previewUrlRef.current = null;
    setFile(null);
    setPreviewUrl(null);
    setError(null);
    setIsCropping(false);
    if (fileInput.current) fileInput.current.value = "";
  }
  function applyCrop(croppedFile: File) {
    setFile(croppedFile);
    setPreview(croppedFile);
    setIsCropping(false);
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file) {
      setError("PICK A SCREENSHOT FIRST.");
      return;
    }
    setError(null);
    showLoading();
    updateLoadingStatus(analysisStatuses[0]);
    const timers = [
      window.setTimeout(() => updateLoadingStatus(analysisStatuses[1]), 450),
      window.setTimeout(() => updateLoadingStatus(analysisStatuses[2]), 1200),
      window.setTimeout(() => updateLoadingStatus(analysisStatuses[3]), 2400),
    ];
    const formData = new FormData();
    formData.append("file", file);
    formData.append("text_model", settings.textModel);
    formData.append("image_model", settings.imageModel);
    formData.append("text_weight", String(settings.textWeight));
    formData.append("image_weight", String(settings.imageWeight));
    try {
      const response = await fetch(apiUrl("/v1/analyses"), {
        method: "POST",
        body: formData,
      });
      if (!response.ok) throw new Error(await getErrorMessage(response));
      const analysis = (await response.json()) as { id: string };
      router.push(`/results/${analysis.id}`);
    } catch (submissionError) {
      setError(
        submissionError instanceof Error
          ? submissionError.message.toUpperCase()
          : "THE CHECK DID NOT RUN. TRY AGAIN.",
      );
    } finally {
      timers.forEach(window.clearTimeout);
      hideLoading();
    }
  }

  return (
    <>
      <motion.form
        animate={{ opacity: 1, y: 0 }}
        className="relative border-[4px] border-black bg-[#FFFDF5] p-4 text-black shadow-[8px_8px_0px_0px_#000] sm:p-6"
        initial={{ opacity: 0, y: 20 }}
        onSubmit={submit}
        transition={{ type: "spring", stiffness: 260, damping: 22 }}
      >
        <div className="mb-5 flex items-start justify-between gap-4">
          <div>
            <p className="font-black text-xs tracking-[0.16em] uppercase">
              YOUR TURN
            </p>
            <h2 className="mt-1 font-black text-3xl leading-none tracking-[-0.07em]">
              DROP THE RECEIPTS.
            </h2>
          </div>
          <span className="rotate-3 border-[3px] border-black bg-[#B8A9FA] px-2 py-1 font-mono text-xs font-black shadow-[3px_3px_0px_0px_#000]">
            PRIVATE
          </span>
        </div>
        <label className="group grid min-h-62 cursor-pointer place-items-center border-[4px] border-dashed border-black bg-[#FFD23F] p-5 text-center text-black transition-transform hover:-translate-x-0.5 hover:-translate-y-0.5">
          <input
            accept="image/jpeg,image/png"
            className="sr-only"
            onChange={onFileChange}
            ref={fileInput}
            type="file"
          />
          {previewUrl ? (
            <img
              alt="Selected screenshot preview"
              className="max-h-60 w-full object-contain"
              src={previewUrl}
            />
          ) : (
            <span className="grid justify-items-center gap-3">
              <IconPill
                icon={FileImage}
                label="Upload screenshot"
                tone="paper"
              />
              <strong className="font-black text-xl tracking-[-0.04em]">
                TAP TO PICK A SCREENSHOT
              </strong>
              <span className="max-w-xs font-bold text-sm">
                PNG OR JPEG — UP TO 10 MB
              </span>
            </span>
          )}
        </label>
        <AnimatePresence initial={false}>
          {file && previewUrl ? (
            <motion.div
              animate={{ opacity: 1, y: 0 }}
              className="mt-4 border-[3px] border-black bg-[#B8A9FA] p-3"
              exit={{ opacity: 0, y: -8 }}
              initial={{ opacity: 0, y: -8 }}
            >
              <div className="flex items-center gap-3">
                <IconPill
                  icon={FileImage}
                  label="Selected file"
                  tone="yellow"
                />
                <div className="min-w-0 flex-1">
                  <p className="truncate font-black text-sm">{file.name}</p>
                  <p className="font-mono text-xs font-bold">
                    {formatFileSize(file.size)} — READY TO CHECK
                  </p>
                </div>
                <button
                  aria-label="Remove selected screenshot"
                  className="grid h-9 w-9 place-items-center border-[3px] border-black bg-[#FFFDF5] shadow-[2px_2px_0px_0px_#000] active:translate-x-0.5 active:translate-y-0.5 active:shadow-none"
                  onClick={removeFile}
                  type="button"
                >
                  <X size={18} strokeWidth={3} />
                </button>
              </div>
              <button
                className="mt-3 inline-flex items-center gap-2 border-[3px] border-black bg-[#FFFDF5] px-3 py-2 font-black text-sm shadow-[3px_3px_0px_0px_#000] active:translate-x-1 active:translate-y-1 active:shadow-none"
                onClick={() => setIsCropping(true)}
                type="button"
              >
                <Crop size={18} strokeWidth={3} /> CROP PREVIEW
              </button>
            </motion.div>
          ) : null}
        </AnimatePresence>
        <AnimatePresence initial={false}>
          {error ? (
            <motion.p
              animate={{ opacity: 1, x: 0 }}
              className="mt-4 border-[3px] border-black bg-[#FF6B6B] p-3 font-black text-sm text-black"
              exit={{ opacity: 0, x: -8 }}
              initial={{ opacity: 0, x: -8 }}
              role="alert"
            >
              {error}
            </motion.p>
          ) : null}
        </AnimatePresence>
        <button
          className="mt-5 flex w-full items-center justify-between border-[4px] border-black bg-[#B8A9FA] p-3.5 font-black text-base tracking-wider text-black shadow-[6px_6px_0px_0px_#000] transition-transform hover:-translate-x-0.5 hover:-translate-y-0.5 active:translate-x-1 active:translate-y-1 active:shadow-none disabled:cursor-not-allowed disabled:bg-[#FFFDF5] disabled:opacity-70"
          disabled={isLoading || !file}
          type="submit"
        >
          <span>CHECK THIS SCREENSHOT</span>
          <IconPill
            icon={ArrowUpRight}
            label="Start screenshot check"
            tone="yellow"
          />
        </button>
        <p className="mt-5 flex items-center gap-2 border-t-[3px] border-black pt-4 font-mono text-[0.68rem] font-bold uppercase">
          <IconPill icon={ShieldAlert} label="Privacy note" tone="lavender" />{" "}
          YOUR IMAGE IS TEMPORARY. WE DO NOT SAVE IT.
        </p>
      </motion.form>
      <LoadingModal isOpen={isLoading} status={status} />
      {isCropping && file && previewUrl ? (
        <CropModal
          file={file}
          onApply={applyCrop}
          onClose={() => setIsCropping(false)}
          previewUrl={previewUrl}
        />
      ) : null}
    </>
  );
}

function formatFileSize(bytes: number) {
  return `${(bytes / 1024 / 1024).toFixed(bytes < 1024 * 1024 ? 1 : 0)} MB`;
}
