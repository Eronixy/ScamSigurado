import {
  FileSearch,
  Link2,
  LockKeyhole,
  ScanSearch,
  Smartphone,
} from "lucide-react";

import { IconPill } from "./components/icon-pill";
import { ScamSamplesCarousel } from "./components/scam-samples-carousel";
import { SiteHeader } from "./components/site-header";
import { UploadPanel } from "./components/upload-panel";

const steps = [
  {
    icon: FileSearch,
    number: "01",
    label: "DROP IT",
    detail: "Upload a suspicious screenshot.",
  },
  {
    icon: ScanSearch,
    number: "02",
    label: "SCAN IT",
    detail: "We read text and check visual signals.",
  },
  {
    icon: LockKeyhole,
    number: "03",
    label: "DECIDE",
    detail: "Get a clear warning before you act.",
  },
];

export default function HomePage() {
  return (
    <div className="min-h-screen overflow-hidden bg-[#FFFDF5] text-black">
      <SiteHeader />
      <main className="mx-auto w-full max-w-[92rem] px-4 py-7 sm:px-6 lg:px-8 lg:py-10">
        <section className="grid items-start gap-7 lg:grid-cols-[minmax(0,1.05fr)_minmax(26rem,0.95fr)] lg:gap-12">
          <div className="relative pt-3 lg:pt-10">
            <span className="absolute -left-2 -top-1 z-10 rotate-3 border-[3px] border-black bg-[#FFD23F] px-3 py-1.5 font-black text-xs tracking-wider text-black shadow-[4px_4px_0px_0px_#000] uppercase sm:left-8">
              PHISHING CHECKER
            </span>
            <div className="border-[4px] border-black bg-[#B8A9FA] p-5 text-black shadow-[8px_8px_0px_0px_#000] sm:p-8 lg:rotate-[-1deg]">
              <p className="mb-4 inline-block border-[3px] border-black bg-[#FFFDF5] px-3 py-1 font-black text-xs tracking-[0.14em] uppercase">
                Stop. Check. Click.
              </p>
              <h1 className="max-w-4xl font-black text-5xl leading-[0.88] tracking-[-0.04em] sm:text-7xl lg:text-8xl">
                DON&apos;T LET A SCAM CALL THE SHOTS.
              </h1>
              <p className="mt-6 max-w-xl border-l-4 border-black pl-4 font-bold text-base leading-relaxed sm:text-lg">
                Upload the screenshot. Get the warning signs before you reply,
                pay, or hand over a code.
              </p>
            </div>
            <div className="relative z-10 -mt-2 ml-auto mr-2 w-fit -rotate-2 border-[3px] border-black bg-[#FFFDF5] px-4 py-2 font-mono text-sm font-black text-black shadow-[5px_5px_0px_0px_#000] sm:mr-10">
              10 MB MAX · PNG + JPG
            </div>
          </div>
          <div className="relative lg:pt-5">
            <div className="absolute -right-3 -top-3 h-24 w-24 rotate-12 border-[4px] border-black bg-[#FF6B6B] sm:h-32 sm:w-32" />
            <UploadPanel />
          </div>
        </section>
        <section className="relative mt-14 border-y-4 border-black bg-[#FFD23F] py-7 text-black">
          <div className="absolute -top-5 left-4 -rotate-2 border-[3px] border-black bg-[#B8A9FA] px-3 py-1 font-black text-xs tracking-wider shadow-[3px_3px_0px_0px_#000] uppercase sm:left-8">
            HOW THE CHECK WORKS
          </div>
          <div className="mx-auto grid w-full max-w-[92rem] gap-4 px-4 pt-3 sm:grid-cols-3 sm:px-6 lg:px-8">
            {steps.map(({ icon, number, label, detail }) => (
              <article
                className="flex items-center gap-3 border-[3px] border-black bg-[#FFFDF5] p-3 shadow-[4px_4px_0px_0px_#000]"
                key={number}
              >
                <IconPill icon={icon} label={label} tone="lavender" />
                <div>
                  <p className="font-mono text-xs font-black">{number}</p>
                  <h2 className="font-black tracking-wider uppercase">
                    {label}
                  </h2>
                  <p className="text-sm font-bold">{detail}</p>
                </div>
              </article>
            ))}
          </div>
        </section>
        <section className="mt-14 pb-8">
          <div className="flex flex-wrap items-end justify-between gap-4 border-b-4 border-black pb-4">
            <div>
              <p className="inline-block border-[3px] border-black bg-[#FF6B6B] px-3 py-1 font-black text-xs tracking-wider shadow-[3px_3px_0px_0px_#000] uppercase">
                Look for the obvious warning signs
              </p>
              <h2 className="mt-4 font-black text-4xl tracking-[-0.07em] sm:text-5xl">
                WHAT WE&apos;RE BUILT TO CATCH.
              </h2>
            </div>
          </div>
          <div className="mt-6 grid gap-5 lg:grid-cols-[0.9fr_1.1fr]">
            <div className="border-[4px] border-black bg-[#B8A9FA] p-5 shadow-[6px_6px_0px_0px_#000]">
              <div className="flex items-center gap-3">
                <IconPill icon={Link2} label="Link warning" tone="yellow" />
                <h3 className="font-black text-2xl">QUICK FLAGS</h3>
              </div>
              <ul className="mt-5 space-y-4 font-bold">
                <li className="border-l-4 border-black pl-3">
                  <strong>SMS phishing links:</strong> urgent banking, wallet,
                  or delivery notices that direct you to a suspicious URL.
                </li>
                <li className="border-l-4 border-black pl-3">
                  <strong>Gambling spam:</strong> unsolicited betting promos,
                  bonus claims, or cash-out links.
                </li>
                <li className="border-l-4 border-black pl-3">
                  <strong>Fake Viber job offers:</strong> unexpected recruiter
                  messages that promise easy daily earnings.
                </li>
              </ul>
              <div className="mt-6 flex items-center gap-3 border-[3px] border-black bg-[#FFFDF5] p-3">
                <IconPill
                  icon={Smartphone}
                  label="Screenshot tip"
                  tone="yellow"
                />
                <p className="text-sm font-bold">
                  Include any visible link when you take the screenshot.
                </p>
              </div>
            </div>
            <ScamSamplesCarousel />
          </div>
        </section>
      </main>
    </div>
  );
}
