import { Navigate } from "react-router-dom";
import ResultsHeader from "../components/results/ResultsHeader";
import ResultsGrid from "../components/results/ResultsGrid";
import { useSearch } from "../context/SearchContext";
import { ROUTES } from "../lib/constants";

export default function Results() {
  const { state } = useSearch();

  if (!state.results || !state.lastSearch) {
    return <Navigate to={ROUTES.SEARCH} replace />;
  }

  return (
    <div className="mx-auto max-w-6xl px-6 py-12">
      <ResultsHeader
        modality={state.lastSearch.modality}
        label={state.lastSearch.label}
        metrics={state.metrics}
      />
      <ResultsGrid modality={state.lastSearch.modality} results={state.results} />
    </div>
  );
}
