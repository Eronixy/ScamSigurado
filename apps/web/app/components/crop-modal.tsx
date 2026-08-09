"use client";

/* Local object URLs cannot be handled by next/image's optimizer. */
/* eslint-disable @next/next/no-img-element */

import { Check, Crop, RotateCcw, X } from "lucide-react";
import { PointerEvent, useEffect, useRef, useState } from "react";

type Crop = { left: number; top: number; width: number; height: number };
type DragMode = "move" | "n" | "s" | "e" | "w" | "nw" | "ne" | "sw" | "se";
type CropModalProps = {
  file: File;
  previewUrl: string;
  onApply: (file: File) => void;
  onClose: () => void;
};
const initialCrop: Crop = { left: 0, top: 0, width: 100, height: 100 };
const minCropSize = 8;

export function CropModal({
  file,
  previewUrl,
  onApply,
  onClose,
}: CropModalProps) {
  const [crop, setCrop] = useState<Crop>(initialCrop);
  const stage = useRef<HTMLDivElement>(null);
  const drag = useRef<{
    mode: DragMode;
    x: number;
    y: number;
    crop: Crop;
  } | null>(null);

  useEffect(() => {
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };
    window.addEventListener("keydown", closeOnEscape);
    return () => window.removeEventListener("keydown", closeOnEscape);
  }, [onClose]);

  function beginDrag(event: PointerEvent<HTMLDivElement>, mode: DragMode) {
    event.preventDefault();
    event.stopPropagation();
    event.currentTarget.setPointerCapture(event.pointerId);
    drag.current = { mode, x: event.clientX, y: event.clientY, crop };
  }

  function moveCrop(event: PointerEvent<HTMLDivElement>) {
    if (!drag.current || !stage.current) return;
    const bounds = stage.current.getBoundingClientRect();
    const deltaX = ((event.clientX - drag.current.x) / bounds.width) * 100;
    const deltaY = ((event.clientY - drag.current.y) / bounds.height) * 100;
    const { mode, crop: start } = drag.current;
    let { left, top, width, height } = start;
    if (mode === "move") {
      left = clamp(start.left + deltaX, 0, 100 - width);
      top = clamp(start.top + deltaY, 0, 100 - height);
    }
    if (mode.includes("w")) {
      left = clamp(
        start.left + deltaX,
        0,
        start.left + start.width - minCropSize,
      );
      width = start.left + start.width - left;
    }
    if (mode.includes("e"))
      width = clamp(start.width + deltaX, minCropSize, 100 - start.left);
    if (mode.includes("n")) {
      top = clamp(
        start.top + deltaY,
        0,
        start.top + start.height - minCropSize,
      );
      height = start.top + start.height - top;
    }
    if (mode.includes("s"))
      height = clamp(start.height + deltaY, minCropSize, 100 - start.top);
    setCrop({ left, top, width, height });
  }

  async function applyCrop() {
    const image = await loadImage(previewUrl);
    const sourceX = Math.round((crop.left / 100) * image.naturalWidth);
    const sourceY = Math.round((crop.top / 100) * image.naturalHeight);
    const sourceWidth = Math.max(
      1,
      Math.round((crop.width / 100) * image.naturalWidth),
    );
    const sourceHeight = Math.max(
      1,
      Math.round((crop.height / 100) * image.naturalHeight),
    );
    const canvas = document.createElement("canvas");
    canvas.width = sourceWidth;
    canvas.height = sourceHeight;
    canvas
      .getContext("2d")
      ?.drawImage(
        image,
        sourceX,
        sourceY,
        sourceWidth,
        sourceHeight,
        0,
        0,
        sourceWidth,
        sourceHeight,
      );
    canvas.toBlob(
      (blob) => {
        if (blob)
          onApply(
            new File(
              [blob],
              `${file.name.replace(/\.[^/.]+$/, "")}-cropped.jpg`,
              { type: "image/jpeg" },
            ),
          );
      },
      "image/jpeg",
      0.92,
    );
  }

  return (
    <div
      className="fixed inset-0 z-50 grid place-items-center bg-black/65 p-4"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) onClose();
      }}
    >
      <section
        aria-labelledby="crop-title"
        aria-modal="true"
        className="w-full max-w-2xl border-4 border-black bg-[#FFFDF5] p-5 text-black shadow-[6px_6px_0px_0px_#000] sm:p-7"
        role="dialog"
      >
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="font-mono text-xs font-black tracking-widest uppercase">
              Fine tune your image
            </p>
            <h2
              className="mt-1 flex items-center gap-2 font-black text-3xl tracking-[-0.06em]"
              id="crop-title"
            >
              <Crop aria-hidden="true" strokeWidth={3} /> CROP SCREENSHOT
            </h2>
          </div>
          <button
            aria-label="Close crop dialog"
            className="grid h-10 w-10 place-items-center rounded-full border-[3px] border-black bg-[#FF6B6B] shadow-[3px_3px_0px_0px_#000] active:translate-x-1 active:translate-y-1 active:shadow-none"
            onClick={onClose}
            type="button"
          >
            <X size={21} strokeWidth={3} />
          </button>
        </div>
        <p className="mt-4 font-bold">
          Drag the crop box to move it. Drag any handle to resize—just like an
          editor.
        </p>
        <div className="mt-5 flex justify-center overflow-auto border-[3px] border-black bg-black p-1">
          <div
            className="relative inline-block touch-none select-none"
            onPointerMove={moveCrop}
            onPointerUp={() => {
              drag.current = null;
            }}
            ref={stage}
          >
            <img
              alt="Crop preview"
              className="block max-h-[48vh] max-w-full"
              draggable="false"
              src={previewUrl}
            />
            <div
              className="absolute cursor-move border-[3px] border-[#FFD23F] bg-[#FFD23F]/20"
              onPointerDown={(event) => beginDrag(event, "move")}
              style={{
                left: `${crop.left}%`,
                top: `${crop.top}%`,
                width: `${crop.width}%`,
                height: `${crop.height}%`,
              }}
            >
              {(["nw", "n", "ne", "e", "se", "s", "sw", "w"] as DragMode[]).map(
                (handle) => (
                  <CropHandle
                    handle={handle}
                    key={handle}
                    onPointerDown={(event) => beginDrag(event, handle)}
                  />
                ),
              )}
            </div>
          </div>
        </div>
        <div className="mt-6 flex flex-wrap justify-end gap-3">
          <button
            className="inline-flex items-center gap-2 border-[3px] border-black bg-[#FFFDF5] px-4 py-2 font-black shadow-[3px_3px_0px_0px_#000] active:translate-x-1 active:translate-y-1 active:shadow-none"
            onClick={() => setCrop(initialCrop)}
            type="button"
          >
            <RotateCcw size={18} strokeWidth={3} /> RESET CROP
          </button>
          <button
            className="border-[3px] border-black bg-[#FFFDF5] px-4 py-2 font-black shadow-[3px_3px_0px_0px_#000] active:translate-x-1 active:translate-y-1 active:shadow-none"
            onClick={onClose}
            type="button"
          >
            CANCEL
          </button>
          <button
            className="inline-flex items-center gap-2 border-[3px] border-black bg-[#FFD23F] px-4 py-2 font-black shadow-[3px_3px_0px_0px_#000] active:translate-x-1 active:translate-y-1 active:shadow-none"
            onClick={applyCrop}
            type="button"
          >
            <Check size={19} strokeWidth={3} /> APPLY CROP
          </button>
        </div>
      </section>
    </div>
  );
}

function CropHandle({
  handle,
  onPointerDown,
}: {
  handle: DragMode;
  onPointerDown: (event: PointerEvent<HTMLDivElement>) => void;
}) {
  const positions: Record<DragMode, string> = {
    move: "",
    nw: "-left-2 -top-2 cursor-nwse-resize",
    n: "left-1/2 -top-2 -translate-x-1/2 cursor-ns-resize",
    ne: "-right-2 -top-2 cursor-nesw-resize",
    e: "-right-2 top-1/2 -translate-y-1/2 cursor-ew-resize",
    se: "-bottom-2 -right-2 cursor-nwse-resize",
    s: "-bottom-2 left-1/2 -translate-x-1/2 cursor-ns-resize",
    sw: "-bottom-2 -left-2 cursor-nesw-resize",
    w: "-left-2 top-1/2 -translate-y-1/2 cursor-ew-resize",
  };
  return (
    <div
      aria-label={`Resize crop ${handle}`}
      className={`absolute h-4 w-4 border-[3px] border-black bg-[#FFFDF5] ${positions[handle]}`}
      onPointerDown={onPointerDown}
      role="button"
    />
  );
}

function clamp(value: number, min: number, max: number) {
  return Math.min(Math.max(value, min), max);
}
function loadImage(src: string) {
  return new Promise<HTMLImageElement>((resolve, reject) => {
    const image = new Image();
    image.onload = () => resolve(image);
    image.onerror = reject;
    image.src = src;
  });
}
