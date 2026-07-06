export const MODALITIES = {
  TEXTO: "texto",
  IMAGEN: "imagen",
  AUDIO: "audio",
};

export const MODALITY_META = {
  [MODALITIES.TEXTO]: {
    label: "Texto",
    description: "Busca por significado en letras de canciones usando un índice invertido con tf-idf y similitud de coseno.",
    accept: null,
  },
  [MODALITIES.IMAGEN]: {
    label: "Imagen",
    description: "Sube una prenda y encuentra visualmente similares mediante SIFT + bag-of-visual-words.",
    accept: ".png,.jpg,.jpeg,.webp",
  },
  [MODALITIES.AUDIO]: {
    label: "Audio",
    description: "Sube un fragmento de audio y encuentra canciones similares por huella acústica.",
    accept: ".mp3,.wav,.ogg",
  },
};

export const ROUTES = {
  HOME: "/",
  SEARCH: "/search",
  RESULTS: "/results",
  detail: (modality, id) => `/results/${modality}/${id}`,
};

export const TOP_K_OPTIONS = [5, 10, 15, 20];

export const SEARCH_SESSION_KEY = "multimodal:last-search";

export const DATASET_TYPE_LABELS = {
  cancion: "Canción",
  letra: "Fragmento de letra",
  prenda: "Imagen de prenda",
};
