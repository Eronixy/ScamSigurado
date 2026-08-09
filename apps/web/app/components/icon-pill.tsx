import type { LucideIcon } from "lucide-react";

type Tone = "yellow" | "lavender" | "paper" | "coral";

const tones: Record<Tone, string> = {
  yellow: "bg-[#FFD23F] text-black",
  lavender: "bg-[#B8A9FA] text-black",
  paper: "bg-[#FFFDF5] text-black",
  coral: "bg-[#FF6B6B] text-black",
};

export function IconPill({
  icon: Icon,
  label,
  tone = "yellow",
}: {
  icon: LucideIcon;
  label: string;
  tone?: Tone;
}) {
  return (
    <span
      aria-label={label}
      className={`inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-full border-[3px] border-black ${tones[tone]}`}
    >
      <Icon aria-hidden="true" size={19} strokeWidth={3} />
    </span>
  );
}
