import { AnalysisResultView } from "../../components/analysis-result";
import { SiteHeader } from "../../components/site-header";

export default async function ResultsPage({
  params,
}: {
  params: Promise<{ analysisId: string }>;
}) {
  const { analysisId } = await params;
  return (
    <div className="min-h-screen bg-[#FFFDF5] text-black">
      <SiteHeader />
      <main className="mx-auto w-full max-w-[92rem] px-4 py-8 sm:px-6 lg:px-8 lg:py-10">
        <div className="mb-7 flex flex-wrap items-end justify-between gap-4 border-b-4 border-black pb-5">
          <div>
            <p className="inline-block -rotate-1 border-[3px] border-black bg-[#FFD23F] px-3 py-1 font-black text-xs tracking-wider text-black shadow-[3px_3px_0px_#000] uppercase">
              ANALYSIS COMPLETE
            </p>
            <h1 className="mt-4 font-black text-4xl tracking-[-0.08em] sm:text-6xl">
              THE VERDICT.
            </h1>
          </div>
          <p className="border-[3px] border-black bg-[#FFFDF5] px-3 py-2 font-mono text-xs font-black text-black">
            ID: {analysisId.slice(0, 8).toUpperCase()}
          </p>
        </div>
        <AnalysisResultView analysisId={analysisId} />
      </main>
    </div>
  );
}
