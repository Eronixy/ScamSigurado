"use client";

import { LoaderCircle } from "lucide-react";

export function LoadingModal({ isOpen, status }: { isOpen: boolean; status: string }) {
  if (!isOpen) return null;

  return (
    <div aria-busy="true" aria-live="assertive" className="fixed inset-0 z-50 grid place-items-center bg-black/65 p-4" role="status">
      <div className="pointer-events-auto w-full max-w-lg border-4 border-black bg-[#FFFDF5] p-6 text-black shadow-[6px_6px_0px_0px_#000] sm:p-8">
        <div className="flex items-start gap-4">
          <div aria-hidden="true" className="analysis-block-spinner grid h-16 w-16 shrink-0 place-items-center border-4 border-black shadow-[4px_4px_0px_0px_#000]">
            <LoaderCircle size={29} strokeWidth={3} />
          </div>
          <div>
            <p className="font-mono text-xs font-black tracking-widest uppercase">Please keep this tab open</p>
            <h2 className="mt-1 font-black text-3xl leading-none tracking-[-0.07em] sm:text-4xl">ANALYZING SCREENSHOT...</h2>
          </div>
        </div>
        <p className="mt-6 border-l-4 border-black pl-3 font-bold">Running ScamSigurado Multimodal Pipeline...</p>
        <p className="mt-5 border-[3px] border-black bg-[#B8A9FA] p-3 font-mono text-sm font-black leading-relaxed">{status}</p>
      </div>
    </div>
  );
}
