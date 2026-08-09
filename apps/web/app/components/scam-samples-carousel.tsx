"use client";

import Image from "next/image";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { useEffect, useState } from "react";

import scam0004 from "../assets/scam0004.jpg";
import scam0013 from "../assets/scam0013.jpg";
import scam0048 from "../assets/scam0048.jpg";

const samples = [
  {
    image: scam0004,
    label: "SMS phishing link",
    detail: "Urgent wallet alert sending you to an unfamiliar link.",
  },
  {
    image: scam0013,
    label: "SMS phishing link",
    detail: "A bank-style message using a look-alike web address.",
  },
  {
    image: scam0048,
    label: "Fake Viber job offer",
    detail: "Unexpected work offer promising unusually easy daily earnings.",
  },
];

export function ScamSamplesCarousel() {
  const [activeIndex, setActiveIndex] = useState(0);
  const next = () => setActiveIndex((index) => (index + 1) % samples.length);
  const previous = () =>
    setActiveIndex((index) => (index - 1 + samples.length) % samples.length);

  useEffect(() => {
    const timer = window.setInterval(next, 5000);
    return () => window.clearInterval(timer);
  }, []);

  const sample = samples[activeIndex];
  return (
    <section
      aria-label="Example scam screenshots"
      className="border-[4px] border-black bg-[#FFFDF5] p-4 shadow-[6px_6px_0px_0px_#000]"
    >
      <div className="mx-auto w-fit border-[3px] border-black bg-[#FFFDF5]">
        <Image
          alt={`Example of ${sample.label}`}
          className="h-64 w-full object-contain"
          priority={activeIndex === 0}
          src={sample.image}
        />
      </div>
      <div aria-live="polite" className="mt-4">
        <p className="font-black text-xs tracking-wider uppercase">
          Example {activeIndex + 1} of {samples.length}
        </p>
        <h3 className="mt-1 font-black text-2xl uppercase">{sample.label}</h3>
        <p className="mt-1 font-bold leading-snug">{sample.detail}</p>
      </div>
      <div className="mt-4 flex items-center justify-between gap-3">
        <button
          aria-label="Show previous scam example"
          className="grid h-10 w-10 place-items-center border-[3px] border-black bg-[#B8A9FA] shadow-[3px_3px_0px_0px_#000] active:translate-x-1 active:translate-y-1 active:shadow-none"
          onClick={previous}
          type="button"
        >
          <ChevronLeft size={21} strokeWidth={3} />
        </button>
        <div className="flex gap-2">
          {samples.map((item, index) => (
            <button
              aria-label={`Show ${item.label} example ${index + 1}`}
              aria-pressed={activeIndex === index}
              className={`h-4 w-4 rounded-full border-[2px] border-black ${activeIndex === index ? "bg-[#FFD23F]" : "bg-[#FFFDF5]"}`}
              key={item.image.src}
              onClick={() => setActiveIndex(index)}
              type="button"
            />
          ))}
        </div>
        <button
          aria-label="Show next scam example"
          className="grid h-10 w-10 place-items-center border-[3px] border-black bg-[#B8A9FA] shadow-[3px_3px_0px_0px_#000] active:translate-x-1 active:translate-y-1 active:shadow-none"
          onClick={next}
          type="button"
        >
          <ChevronRight size={21} strokeWidth={3} />
        </button>
      </div>
    </section>
  );
}
