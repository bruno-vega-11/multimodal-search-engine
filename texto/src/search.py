# src/search.py
#
# Motor de busqueda de texto (backend del proyecto). Ya no lee
# codebook.json, idf.json, metadata.json, doc_norms.json ni
# dictionary.json: todo eso vive en Postgres (ver
# src/sql/schema.sql y src/load_to_postgres.py).
#
# idf y postings estan fusionados en una sola tabla, term_index,
# donde cada fila es un termino con su idf_value y su posting
# list completa empacada como JSONB. Esto es valido porque el
# patron de uso de este proyecto es carga unica + solo lecturas
# (nunca se actualiza un posting individual despues de cargar),
# asi que no se paga el costo tipico de JSONB en escritura
# incremental, y se gana en lectura: una sola query por termino
# trae idf + posting list completa (antes eran 2 tablas).
#
# dictionary.json (el mapa termino->offset que usabamos para
# hacer f.seek() en final_index.idx) ya no es necesario: el
# indice (primary key) de Postgres sobre term_index.term resuelve
# ese mismo problema de acceso directo sin manejar offsets a mano.
#
# IMPORTANTE: esto es el motor de busqueda real del proyecto
# (Fase 2). Para el experimento comparativo de Fase 3 (tu indice
# invertido vs. GIN/GiST), se usa un script aparte que sigue
# leyendo final_index.idx directamente, sin pasar por Postgres,
# para poder medir tu implementacion propia de forma aislada.

import math
from collections import Counter, defaultdict

from texto.src.preprocess import preprocess_text
from db import get_connection, get_dict_cursor


class SearchEngine:

    def __init__(self):
        self.conn = get_connection()
        print("Ready (Postgres backend).")

    def close(self):
        self.conn.close()

    # ------------------------------------------------------------
    # Batch fetch: idf_value + postings (JSONB) de varios terminos
    # en una sola query. Antes eran 2 queries a 2 tablas distintas
    # (idf y postings); ahora term_index las trae juntas.
    # ------------------------------------------------------------
    def _fetch_term_index(self, terms):
        if not terms:
            return {}

        with get_dict_cursor(self.conn) as cur:
            cur.execute(
                """
                SELECT term, idf_value, postings
                FROM term_index
                WHERE term = ANY(%s)
                """,
                (list(terms),)
            )

            result = {}

            for row in cur.fetchall():
                # row["postings"] ya viene deserializado como
                # lista de [chunk_id, tf] por el driver (JSONB).
                result[row["term"]] = {
                    "idf_value": row["idf_value"],
                    "postings": row["postings"],
                }

            return result

    # ------------------------------------------------------------
    # Batch fetch: SOLO document_id de varios chunk_id (liviano,
    # sin texto). Se usa para poder agrupar por cancion ANTES de
    # cortar a top_k, sin pagar el costo de traer title/artist/
    # text de candidatos que van a ser descartados.
    # ------------------------------------------------------------
    def _fetch_document_ids(self, chunk_ids):

        if not chunk_ids:
            return {}

        with get_dict_cursor(self.conn) as cur:
            cur.execute(
                """
                SELECT chunk_id, document_id
                FROM metadata
                WHERE chunk_id = ANY(%s)
                """,
                (list(chunk_ids),)
            )
            return {
                row["chunk_id"]: row["document_id"]
                for row in cur.fetchall()
            }

    # ------------------------------------------------------------
    # Batch fetch: normas de varios chunk_id en una sola query
    # ------------------------------------------------------------
    def _fetch_doc_norms(self, chunk_ids):

        if not chunk_ids:
            return {}

        with get_dict_cursor(self.conn) as cur:
            cur.execute(
                """
                SELECT chunk_id, norm_value
                FROM doc_norms
                WHERE chunk_id = ANY(%s)
                """,
                (list(chunk_ids),)
            )
            return {
                row["chunk_id"]: row["norm_value"]
                for row in cur.fetchall()
            }
        
    # ------------------------------------------------------------
    # Batch fetch: metadata SOLO de los chunk_id finales (top-k)
    # ------------------------------------------------------------
    def _fetch_metadata(self, chunk_ids):

        if not chunk_ids:
            return {}

        with get_dict_cursor(self.conn) as cur:
            cur.execute(
                """
                SELECT chunk_id, document_id, title, artist, text
                FROM metadata
                WHERE chunk_id = ANY(%s)
                """,
                (list(chunk_ids),)
            )
            return {
                row["chunk_id"]: row
                for row in cur.fetchall()
            }

    def search(self, query, top_k=10):
        terms = preprocess_text(query)
        print("TOKENS:", terms)
        if not terms:
            return []

        query_tf = Counter(terms)
        # --------------------------------------------------
        # 1) idf + postings de los terminos de la query, en
        #    una sola query batch contra term_index
        # --------------------------------------------------
        term_data = self._fetch_term_index(set(query_tf.keys()))
        query_vector = {}

        for term, tf in query_tf.items():
            if term not in term_data:
                continue
            idf_value = term_data[term]["idf_value"]
            query_vector[term] = ((1 + math.log10(tf)) * idf_value)

        if not query_vector:
            return []

        query_norm = math.sqrt(sum(w * w for w in query_vector.values()))

        # --------------------------------------------------
        # 2) Calcular dot products usando la posting list
        #    (ya la trajimos en el paso 1, no hay query nueva)
        # --------------------------------------------------
        dot_products = defaultdict(float)
        matched_terms = defaultdict(set)

        for term, q_weight in query_vector.items():
            term_idf = term_data[term]["idf_value"]
            postings = term_data[term]["postings"]
            for chunk_id, tf in postings:
                d_weight = (1 + math.log10(tf)) * term_idf
                dot_products[chunk_id] += q_weight * d_weight
                matched_terms[chunk_id].add(term)
        if not dot_products:
            return []

        # --------------------------------------------------
        # 3) Normas de los chunks candidatos (1 query batch)
        # --------------------------------------------------
        doc_norms = self._fetch_doc_norms(list(dot_products.keys()))

        n_query_terms = len(query_vector)
        chunk_scores = []

        for chunk_id, dot in dot_products.items():
            doc_norm = doc_norms.get(chunk_id, 0)
            if doc_norm == 0 or query_norm == 0:
                continue
            cosine = dot/(query_norm * doc_norm)
            coverage = (len(matched_terms[chunk_id]) / n_query_terms)

            # Score final: coseno ponderado por cobertura de
            # terminos de la query. Esto evita dos problemas:
            # 1) coseno puro: un chunk corto y mono-tematico
            #    (ej. "Dance Dance") puede tener norma muy baja
            #    y por tanto coseno artificialmente alto, aunque
            #    le falten terminos de la query.
            # 2) coverage como filtro escalonado (ordenar primero
            #    por coverage, coseno solo como desempate): genera
            #    saltos duros donde un coseno muy alto con
            #    cobertura parcial queda siempre por debajo de
            #    un coseno bajo con cobertura completa, sin
            #    importar la magnitud de la diferencia.
            # Multiplicar es continuo: penaliza cobertura parcial
            # proporcionalmente, sin escalones, dejando que un
            # coseno suficientemente alto compense una cobertura
            # algo menor.
            final_score = cosine * coverage

            chunk_scores.append((chunk_id, final_score, cosine, coverage))

        # Ordenar por el score final (coseno * coverage).
        chunk_scores.sort(key=lambda x: x[1],reverse=True)

        # --------------------------------------------------
        # SONG RANKING (agrupar por document_id, quedarse con
        # el mejor chunk de cada cancion). Usamos document_id
        # "liviano" (sin text) para poder agrupar y cortar a
        # top_k ANTES de pagar el costo de traer title/artist/
        # text completos.
        # --------------------------------------------------
        doc_id_map = self._fetch_document_ids([cid for cid, _, _, _ in chunk_scores])

        best_per_song = {}

        for chunk_id, final_score, cosine, coverage in chunk_scores:
            doc_id = doc_id_map.get(chunk_id)

            if doc_id is None:
                continue

            if (doc_id not in best_per_song or final_score > best_per_song[doc_id]["rank_key"]):
                best_per_song[doc_id] = {
                    "score": cosine,
                    "coverage": coverage,
                    "rank_key": final_score,
                    "chunk_id": chunk_id,
                }

        # Cortamos a top_k ANTES de pedir texto completo.
        top_songs = sorted(best_per_song.values(), key=lambda x: x["rank_key"], reverse=True)[:top_k]

        # Solo aqui pagamos el costo de traer title/artist/text,
        # y solo para los top_k chunk_id ganadores.
        winning_chunk_ids = [song["chunk_id"] for song in top_songs]

        metadata_map = self._fetch_metadata(winning_chunk_ids)

        results = []

        for song in top_songs:
            meta = metadata_map.get(song["chunk_id"])
            if meta is None:
                continue

            results.append({
                "score": song["score"],
                "coverage": song["coverage"],
                "rank_key": song["rank_key"],
                "chunk_id": song["chunk_id"],
                "title": meta["title"],
                "artist": meta["artist"],
                "text": meta["text"],
            })
        return results


if __name__ == "__main__":
    engine = SearchEngine()
    try:
        while True:
            query = input("\nQuery: ")
            if query.lower() == "exit":
                break
            results = engine.search(query)
            print()
            for i, result in enumerate(results, start=1):
                print("=" * 60)
                print(f"#{i}")
                print(f"Title: {result['title']}")
                print(f"Artist: {result['artist']}")
                print(f"Similarity: {result['rank_key']:.4f}")
                print()
                print(result["text"])
                print()
    finally:
        engine.close()