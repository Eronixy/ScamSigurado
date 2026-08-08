import { SiteHeader } from "./components/site-header";
import { UploadPanel } from "./components/upload-panel";

export default function HomePage() {
  return (
    <div className="app-shell">
      <header className="page-container site-header">
        <SiteHeader />
      </header>
      <main className="page-container content">
        <p className="eyebrow">Screenshot check</p>
        <h1 className="page-title">Check before you click.</h1>
        <p className="page-intro">
          Upload a suspicious message, post, or website screenshot. ScamSigurado checks
          for signals that deserve a closer look.
        </p>
        <UploadPanel />
      </main>
    </div>
  );
}
