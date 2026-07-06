import { createContext, useContext, useEffect, useMemo, useReducer } from "react";
import { MODALITIES, SEARCH_SESSION_KEY } from "../lib/constants";

const SearchContext = createContext(null);

const initialState = {
  modality: MODALITIES.TEXTO,
  query: { text: "", file: null },
  topK: 5,
  status: "idle", // idle | loading | success | error
  error: null,
  results: null,
  metrics: null,
  lastSearch: null, // { modality, label, topK }
};

function reducer(state, action) {
  switch (action.type) {
    case "SET_MODALITY":
      return {
        ...state,
        modality: action.modality,
        query: { text: "", file: null },
      };
    case "SET_QUERY_TEXT":
      return { ...state, query: { ...state.query, text: action.text } };
    case "SET_QUERY_FILE":
      return { ...state, query: { ...state.query, file: action.file } };
    case "SET_TOPK":
      return { ...state, topK: action.topK };
    case "SEARCH_START":
      return { ...state, status: "loading", error: null };
    case "SEARCH_SUCCESS":
      return {
        ...state,
        status: "success",
        results: action.results,
        metrics: action.metrics,
        lastSearch: { modality: action.modality, label: action.label, topK: state.topK },
      };
    case "SEARCH_ERROR":
      return { ...state, status: "error", error: action.error };
    case "HYDRATE":
      return { ...state, ...action.payload };
    default:
      return state;
  }
}

function init() {
  try {
    const raw = sessionStorage.getItem(SEARCH_SESSION_KEY);
    if (!raw) return initialState;
    const persisted = JSON.parse(raw);
    return {
      ...initialState,
      ...persisted,
      query: { text: persisted.lastSearch?.label ?? "", file: null },
      status: persisted.results ? "success" : "idle",
    };
  } catch {
    return initialState;
  }
}

export function SearchProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, undefined, init);

  useEffect(() => {
    if (state.status !== "success") return;
    const toPersist = {
      modality: state.modality,
      topK: state.topK,
      results: state.results,
      metrics: state.metrics,
      lastSearch: state.lastSearch,
    };
    sessionStorage.setItem(SEARCH_SESSION_KEY, JSON.stringify(toPersist));
  }, [state.status, state.modality, state.topK, state.results, state.metrics, state.lastSearch]);

  const findResultById = useMemo(() => {
    return (modality, id) => {
      if (!state.results) return null;
      if (modality === "text-song") return state.results.by_song?.find((r) => r.id === id) ?? null;
      if (modality === "text-chunk") return state.results.by_chunk?.find((r) => r.id === id) ?? null;
      if (Array.isArray(state.results)) return state.results.find((r) => r.id === id) ?? null;
      return null;
    };
  }, [state.results]);

  const value = useMemo(
    () => ({ state, dispatch, findResultById }),
    [state, findResultById]
  );

  return <SearchContext.Provider value={value}>{children}</SearchContext.Provider>;
}

export function useSearch() {
  const ctx = useContext(SearchContext);
  if (!ctx) throw new Error("useSearch must be used within SearchProvider");
  return ctx;
}
