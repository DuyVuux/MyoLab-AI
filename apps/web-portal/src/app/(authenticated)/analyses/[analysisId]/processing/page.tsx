import { Day21AnalysisProcessingPage } from "../../../../analyses/Day21AnalysisProcessingPage";

export default function AnalysisProcessingRoute({ params }: { readonly params: { readonly analysisId: string } }): JSX.Element {
  return <Day21AnalysisProcessingPage analysisId={params.analysisId} />;
}
