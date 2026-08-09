import Link from "next/link";
import Image from "next/image";

import { AboutModal } from "./about-modal";
import { AdvancedModal } from "./advanced-modal";

export function SiteHeader() {
  return (
    <header className="border-b-4 border-black bg-[#FFFDF5] text-black">
      <div className="mx-auto flex min-h-22 w-full max-w-[92rem] items-center justify-between gap-4 px-4 py-3 sm:px-6 lg:px-8">
        <Link
          aria-label="ScamSigurado home"
          className="flex items-center gap-3"
          href="/"
        >
          <Image
            alt=""
            aria-hidden="true"
            className="size-12 shrink-0 sm:size-14"
            height={56}
            src="/icon.svg"
            unoptimized
            width={56}
          />
          <span className="leading-none">
            <span className="block font-black text-lg tracking-[-0.08em] sm:text-2xl">
              SCAM
            </span>
            <span className="block bg-black px-1.5 py-0.5 font-black text-sm tracking-[0.18em] text-[#FFD23F] sm:text-base">
              SIGURADO
            </span>
          </span>
        </Link>
        <div className="flex items-center gap-2 sm:gap-3">
          <AdvancedModal />
          <AboutModal />
        </div>
      </div>
    </header>
  );
}
