"use client";

import { Info, X } from "lucide-react";
import { useEffect, useRef, useState } from "react";

const authors = ["Irron Jovic Jun V. Brosoto", "Jezrielle Anne G. Padlan", "Julia Kyla C. Rustia", "Catherine C. Tabigne"];

export function AboutModal() {
  const [isOpen, setIsOpen] = useState(false);
  const closeButton = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!isOpen) return;
    closeButton.current?.focus();
    const closeOnEscape = (event: KeyboardEvent) => { if (event.key === "Escape") setIsOpen(false); };
    window.addEventListener("keydown", closeOnEscape);
    return () => window.removeEventListener("keydown", closeOnEscape);
  }, [isOpen]);

  return (
    <>
      <button className="inline-flex items-center gap-2 border-[3px] border-black bg-[#B8A9FA] px-3 py-2 font-black text-xs tracking-wider text-black shadow-[3px_3px_0px_0px_#000] transition-transform hover:-translate-x-0.5 hover:-translate-y-0.5 active:translate-x-1 active:translate-y-1 active:shadow-none uppercase" onClick={() => setIsOpen(true)} type="button">
        <Info aria-hidden="true" size={16} strokeWidth={3} /> About
      </button>
      {isOpen ? (
        <div className="fixed inset-0 z-50 grid place-items-center bg-black/65 p-4" onMouseDown={(event) => { if (event.target === event.currentTarget) setIsOpen(false); }}>
          <section aria-labelledby="about-title" aria-modal="true" className="w-full max-w-2xl border-4 border-black bg-[#FFFDF5] p-6 text-black shadow-[6px_6px_0px_0px_#000] sm:p-8" role="dialog">
            <div className="flex items-start justify-between gap-4">
              <div><p className="font-mono text-xs font-black tracking-widest uppercase">About the project</p><h2 className="mt-1 font-black text-3xl tracking-[-0.06em]" id="about-title">SCAMSIGURADO</h2></div>
              <button aria-label="Close about dialog" className="grid h-10 w-10 shrink-0 place-items-center rounded-full border-[3px] border-black bg-[#FF6B6B] text-black shadow-[3px_3px_0px_0px_#000] transition-transform active:translate-x-1 active:translate-y-1 active:shadow-none" onClick={() => setIsOpen(false)} ref={closeButton} type="button"><X size={21} strokeWidth={3} /></button>
            </div>
            <p className="mt-6 border-l-4 border-black pl-4 font-bold leading-relaxed">ScamSigurado is a multimodal scam detection web application featuring a Next.js product UI, a public FastAPI gateway, and a private FastAPI ML runtime. It combines optical text extraction and CNN vision models to detect Filipino-targeted online scams from uploaded screenshots.</p>
            <div className="mt-6 border-[3px] border-black bg-[#B8A9FA] p-4"><h3 className="font-black tracking-wider uppercase">Authors</h3><ul className="mt-3 space-y-1 font-bold">{authors.map((author) => <li key={author}>{author}</li>)}</ul></div>
            <p className="mt-6 border-[3px] border-black bg-[#FFD23F] p-4 text-sm font-bold leading-relaxed">This project is for academic and research purposes only. Commercial use is not permitted without prior consent.</p>
          </section>
        </div>
      ) : null}
    </>
  );
}
