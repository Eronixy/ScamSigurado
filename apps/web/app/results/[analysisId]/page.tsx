import { AnalysisResultView } from "../../components/analysis-result";
import { SiteHeader } from "../../components/site-header";

export default async function ResultsPage({ params }: { params: Promise<{ analysisId: string }> }) {
  const { analysisId } = await params;

  return (
    <div className="app-shell">
      <header className="page-container site-header">
        <SiteHeader />
      </header>
      <main className="page-container content">
        <p className="eyebrow">Analysis result</p>
        <AnalysisResultView analysisId={analysisId} />
      </main>
    </div>
  );
}
