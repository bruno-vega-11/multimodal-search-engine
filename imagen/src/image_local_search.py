import os
import json
import math
from collections import defaultdict

# Rutas por defecto de los artefactos del índice invertido (mismo esquema que
# texto y audio: un lexicon de offsets + postings en JSONL leídos por seek()).
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROCESSED_DIR = os.path.join(SCRIPT_DIR, "..", "data", "processed")
LEXICON_FILE_PATH = os.path.join(PROCESSED_DIR, "lexicon.json")
INDEX_FILE_PATH = os.path.join(PROCESSED_DIR, "inverted_index.jsonl")
DOCS_FILE_PATH = os.path.join(PROCESSED_DIR, "docs.json")


class ImageLocalSearch:
    """Motor de búsqueda de imágenes 100% local y SIN cargar todo a RAM.

    Igual que el motor de audio: en memoria sólo viven el lexicon (word_id ->
    offset de byte), el mapa de documentos (id -> nombre/ruta) y las magnitudes
    TF-IDF precomputadas. Las listas de postings se leen bajo demanda desde el
    disco con seek(), sólo para las palabras visuales presentes en la consulta.

    El id de cada imagen es su índice de línea en el JSONL de vectores original.
    """

    def __init__(self, base_dir, lexicon_path=LEXICON_FILE_PATH,
                 index_path=INDEX_FILE_PATH, docs_path=DOCS_FILE_PATH):
        # base_dir: raíz del proyecto a la que se concatena la ruta relativa
        # del JSONL para llegar al archivo físico en disco (endpoint de render).
        self.base_dir = base_dir

        # 1. Lexicon (punteros) en RAM.
        with open(lexicon_path, "r", encoding="utf-8") as f:
            self.lexicon = json.load(f)

        # 2. Mapa de documentos (id -> {nombre_archivo, ruta_original}) en RAM.
        #    Sólo strings, mucho más liviano que los 44k histogramas densos.
        with open(docs_path, "r", encoding="utf-8") as f:
            self.docs = json.load(f)
        self.total_docs = len(self.docs)

        # 3. Archivo de postings abierto para lectura por offset.
        self.index_file = open(index_path, "rb")

        # 4. Precomputar IDF y magnitudes vectoriales TF-IDF recorriendo el
        #    índice una sola vez (no se guardan los histogramas, sólo escalares).
        self.idf = {}
        self.doc_magnitudes = defaultdict(float)
        N = self.total_docs
        for word_id_str in self.lexicon.keys():
            posting_list = self._get_posting_list(word_id_str)
            df = len(posting_list)
            self.idf[word_id_str] = math.log((N + 1) / (df + 1)) + 1.0
            idf_weight = self.idf[word_id_str]
            for doc_id, tf in posting_list:
                self.doc_magnitudes[doc_id] += (tf * idf_weight) ** 2

        for doc_id in self.doc_magnitudes:
            self.doc_magnitudes[doc_id] = math.sqrt(self.doc_magnitudes[doc_id])

    def __len__(self):
        return self.total_docs

    def _get_posting_list(self, word_id_str):
        """Salta al byte exacto en disco y recupera la lista de postings."""
        if word_id_str not in self.lexicon:
            return []
        offset = self.lexicon[word_id_str]
        self.index_file.seek(offset)
        line_bytes = self.index_file.readline()
        return json.loads(line_bytes.decode("utf-8"))

    def search(self, query_histogram, top_k=5):
        """Recibe el histograma denso (lista de 1000 conteos) de la imagen
        consulta y devuelve los top_k por similitud coseno TF-IDF. Cada
        resultado es un dict con id, nombre_archivo, ruta_original y score."""
        # Histograma denso -> {word_id: tf} sólo para palabras presentes.
        query_tf = {i: int(c) for i, c in enumerate(query_histogram) if c}
        if not query_tf:
            return []

        query_tfidf = {}
        for word_id, tf in query_tf.items():
            word_id_str = str(word_id)
            if word_id_str in self.idf:
                query_tfidf[word_id_str] = tf * self.idf[word_id_str]

        query_magnitude = math.sqrt(sum(s ** 2 for s in query_tfidf.values()))
        if query_magnitude == 0:
            return []

        dot_products = defaultdict(float)
        for word_id_str, q_tfidf in query_tfidf.items():
            idf_weight = self.idf[word_id_str]
            # Lista leída SOLO bajo demanda desde el disco.
            for doc_id, doc_tf in self._get_posting_list(word_id_str):
                dot_products[doc_id] += q_tfidf * (doc_tf * idf_weight)

        scores = []
        for doc_id, dot in dot_products.items():
            doc_magnitude = self.doc_magnitudes.get(doc_id, 1.0)
            similarity = dot / (query_magnitude * doc_magnitude)
            scores.append((doc_id, similarity))

        scores.sort(key=lambda x: x[1], reverse=True)

        resultados = []
        for doc_id, score in scores[:top_k]:
            meta = self.docs.get(str(doc_id), {})
            resultados.append({
                "id": int(doc_id),
                "nombre_archivo": meta.get("nombre_archivo"),
                "ruta_original": meta.get("ruta_original"),
                "score": round(float(score), 4),
            })
        return resultados

    def resolver_ruta(self, imagen_id):
        """Traduce un id a la ruta absoluta en la máquina: base_dir + ruta
        relativa del JSONL. Devuelve None si el id no existe en el mapa."""
        meta = self.docs.get(str(imagen_id))
        if not meta:
            return None
        ruta_relativa = os.path.normpath(meta["ruta_original"])
        return os.path.join(self.base_dir, ruta_relativa)

    def close(self):
        if hasattr(self, "index_file") and not self.index_file.closed:
            self.index_file.close()

    def __del__(self):
        self.close()
