import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { FileText, Image as ImageIcon, AudioLines, ArrowRight } from "lucide-react";
import SegmentedControl from "../ui/SegmentedControl";
import Button from "../ui/Button";
import ErrorState from "../ui/ErrorState";
import TextSearchInput from "./TextSearchInput";
import ImageSearchInput from "./ImageSearchInput";
import AudioSearchInput from "./AudioSearchInput";
import TopKSelect from "./TopKSelect";
import { useSearch } from "../../context/SearchContext";
import { searchText, searchAudio, searchImage } from "../../api";
import { MODALITIES, ROUTES } from "../../lib/constants";

const MODE_OPTIONS = [
  { value: MODALITIES.TEXTO, label: "Texto", icon: <FileText className="size-4" /> },
  { value: MODALITIES.IMAGEN, label: "Imagen", icon: <ImageIcon className="size-4" /> },
  { value: MODALITIES.AUDIO, label: "Audio", icon: <AudioLines className="size-4" /> },
];

const SEARCH_FNS = {
  [MODALITIES.TEXTO]: (query, topK) => searchText(query.text, topK),
  [MODALITIES.IMAGEN]: (query, topK) => searchImage(query.file, topK),
  [MODALITIES.AUDIO]: (query, topK) => searchAudio(query.file, topK),
};

export default function SearchBar() {
  const { state, dispatch } = useSearch();
  const [localError, setLocalError] = useState(null);
  const navigate = useNavigate();

  const canSubmit =
    state.modality === MODALITIES.TEXTO ? state.query.text.trim().length > 0 : Boolean(state.query.file);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!canSubmit || state.status === "loading") return;

    setLocalError(null);
    dispatch({ type: "SEARCH_START" });
    try {
      const { data, metrics } = await SEARCH_FNS[state.modality](state.query, state.topK);
      const label = state.modality === MODALITIES.TEXTO ? state.query.text : state.query.file.name;
      dispatch({ type: "SEARCH_SUCCESS", results: data, metrics, modality: state.modality, label });
      navigate(ROUTES.RESULTS);
    } catch (err) {
      dispatch({ type: "SEARCH_ERROR", error: err.message });
      setLocalError(err.message);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="mb-5 flex justify-center">
        <SegmentedControl
          options={MODE_OPTIONS}
          value={state.modality}
          onChange={(modality) => dispatch({ type: "SET_MODALITY", modality })}
        />
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={state.modality}
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -6 }}
          transition={{ duration: 0.2 }}
        >
          {state.modality === MODALITIES.TEXTO && (
            <TextSearchInput
              value={state.query.text}
              onChange={(text) => dispatch({ type: "SET_QUERY_TEXT", text })}
            />
          )}
          {state.modality === MODALITIES.IMAGEN && (
            <ImageSearchInput
              file={state.query.file}
              onFile={(file) => dispatch({ type: "SET_QUERY_FILE", file })}
            />
          )}
          {state.modality === MODALITIES.AUDIO && (
            <AudioSearchInput
              file={state.query.file}
              onFile={(file) => dispatch({ type: "SET_QUERY_FILE", file })}
            />
          )}
        </motion.div>
      </AnimatePresence>

      <div className="mt-4 flex items-center justify-between gap-3">
        <TopKSelect value={state.topK} onChange={(topK) => dispatch({ type: "SET_TOPK", topK })} />
        <Button type="submit" variant="accent" size="lg" loading={state.status === "loading"} disabled={!canSubmit}>
          Buscar
          <ArrowRight className="size-4" />
        </Button>
      </div>

      {localError && (
        <div className="mt-6">
          <ErrorState
            title="No se pudo completar la búsqueda"
            description={localError}
            onRetry={() => setLocalError(null)}
          />
        </div>
      )}
    </form>
  );
}
