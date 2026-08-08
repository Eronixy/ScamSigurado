"use client";

import { ChangeEvent, FormEvent, useRef, useState } from "react";
import { useRouter } from "next/navigation";

import { apiUrl, getErrorMessage } from "../lib/api";

const maxFileSize = 10 * 1024 * 1024;

export function UploadPanel() {
  const fileInput = useRef<HTMLInputElement>(null);
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  function selectFile(nextFile: File | null) {
    setError(null);
    if (!nextFile) {
      return;
    }
    if (!['image/jpeg', 'image/png'].includes(nextFile.type)) {
      setFile(null);
      setError("Please choose a PNG or JPEG screenshot.");
      return;
    }
    if (nextFile.size > maxFileSize) {
      setFile(null);
      setError("Please choose a screenshot smaller than 10 MB.");
      return;
    }
    setFile(nextFile);
  }

  function onFileChange(event: ChangeEvent<HTMLInputElement>) {
    selectFile(event.target.files?.[0] ?? null);
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file) {
      setError("Choose a screenshot before starting the check.");
      return;
    }

    setIsSubmitting(true);
    setError(null);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(apiUrl("/v1/analyses"), { method: "POST", body: formData });
      if (!response.ok) {
        throw new Error(await getErrorMessage(response));
      }
      const analysis = (await response.json()) as { id: string };
      router.push(`/results/${analysis.id}`);
    } catch (submissionError) {
      setError(
        submissionError instanceof Error
          ? submissionError.message
          : "We could not analyze that screenshot. Please try again.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form className="panel upload-panel" onSubmit={submit}>
      <label className="drop-zone" data-file={Boolean(file)}>
        <input accept="image/jpeg,image/png" className="sr-only" onChange={onFileChange} ref={fileInput} type="file" />
        <span className="drop-zone-content">
          <span aria-hidden="true" className="upload-icon">↑</span>
          <strong>{file ? "Screenshot selected" : "Choose a screenshot"}</strong>
          <span>PNG or JPEG, up to 10 MB</span>
        </span>
      </label>

      {file ? (
        <div className="file-summary">
          <span className="file-name">{file.name}</span>
          <span className="helper-text">{formatFileSize(file.size)}</span>
        </div>
      ) : null}

      {error ? <p className="error-message" role="alert">{error}</p> : null}

      <div className="button-row">
        <button className="button button-primary" disabled={isSubmitting || !file} type="submit">
          {isSubmitting ? "Checking screenshot…" : "Check screenshot"}
        </button>
      </div>
      <p className="privacy-note">Your screenshot is processed temporarily and is not saved.</p>
    </form>
  );
}

function formatFileSize(bytes: number) {
  return `${(bytes / 1024 / 1024).toFixed(bytes < 1024 * 1024 ? 1 : 0)} MB`;
}
