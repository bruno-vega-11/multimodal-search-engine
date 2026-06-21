# src/search.py

import json
import math
from collections import Counter, defaultdict

from preprocess import preprocess_text


class SearchEngine:

    def __init__(self):

        print("Loading dictionary...")

        with open(
            "data/index/dictionary.json",
            encoding="utf-8"
        ) as f:

            self.dictionary = json.load(f)

        print("Loading idf...")

        with open(
            "data/processed/idf.json",
            encoding="utf-8"
        ) as f:

            self.idf = json.load(f)

        print("Loading norms...")

        with open(
            "data/index/doc_norms.json",
            encoding="utf-8"
        ) as f:

            self.doc_norms = json.load(f)

        print("Loading metadata...")

        self.metadata = {}

        with open(
            "data/processed/metadata.json",
            encoding="utf-8"
        ) as f:

            for line in f:

                record = json.loads(line)

                self.metadata[
                    record["chunk_id"]
                ] = record

        print("Ready.")

    def get_postings(
        self,
        term
    ):

        if term not in self.dictionary:

            return []

        offset = self.dictionary[
            term
        ]

        with open(
            "data/index/final_index.idx",
            encoding="utf-8"
        ) as f:

            f.seek(offset)

            line = f.readline()

        record = json.loads(
            line
        )

        return record["postings"]

    def search(
        self,
        query,
        top_k=10
    ):

        terms = preprocess_text(
            query
        )

        print("TOKENS:", terms)

        if not terms:

            return []

        # --------------------
        # QUERY VECTOR
        # --------------------

        query_tf = Counter(
            terms
        )

        query_vector = {}

        for term, tf in query_tf.items():

            if term not in self.idf:
                continue

            query_vector[term] = ((1 + math.log10(tf))*self.idf[term])

        query_norm = math.sqrt(

            sum(
                weight * weight
                for weight in
                query_vector.values()
            )

        )

        # --------------------
        # DOT PRODUCTS
        # --------------------

        dot_products = defaultdict(
            float
        )

        matched_terms = defaultdict(
            set
        )

        for term, q_weight in (
            query_vector.items()
        ):

            postings = self.get_postings(
                term
            )

            term_idf = self.idf[
                term
            ]

            for chunk_id, tf in postings:

                d_weight = (
                    (1 + math.log10(tf))
                    *
                    term_idf
                )

                dot_products[
                    chunk_id
                ] += (
                    q_weight *
                    d_weight
                )

                matched_terms[
                    chunk_id
                ].add(term)

        # --------------------
        # COSINE
        # --------------------

        chunk_scores = []

        n_query_terms = len(
            query_vector
        )

        for chunk_id, dot in (
            dot_products.items()
        ):

            doc_norm = (
                self.doc_norms.get(
                    str(chunk_id),
                    0
                )
            )

            if (
                doc_norm == 0
                or
                query_norm == 0
            ):
                continue

            cosine = (
                dot /
                (
                    query_norm *
                    doc_norm
                )
            )

            coverage = (
                len(matched_terms[chunk_id])
                / n_query_terms
            )

            chunk_scores.append(
                (
                    chunk_id,
                    cosine,
                    coverage
                )
            )

        # Primero por cobertura de terminos de la query
        # (cuantos terminos distintos matchea el chunk),
        # luego por coseno como desempate. Esto evita que
        # un chunk de una sola palabra repetida (norma muy
        # baja => coseno alto) le gane a un chunk que
        # realmente contiene varios terminos de la query.
        chunk_scores.sort(
            key=lambda x: (x[2], x[1]),
            reverse=True
        )

        # --------------------
        # SONG RANKING
        # --------------------

        songs = {}

        for chunk_id, cosine, coverage in (
            chunk_scores
        ):

            meta = self.metadata[
                chunk_id
            ]

            doc_id = meta[
                "document_id"
            ]

            rank_key = (
                coverage,
                cosine
            )

            if (
                doc_id not in songs
                or
                rank_key >
                songs[doc_id]["rank_key"]
            ):

                songs[doc_id] = {

                    "score":
                    cosine,

                    "coverage":
                    coverage,

                    "rank_key":
                    rank_key,

                    "chunk_id":
                    chunk_id,

                    "title":
                    meta["title"],

                    "artist":
                    meta["artist"],

                    "text":
                    meta["text"]
                }

        results = sorted(

            songs.values(),

            key=lambda x:
            x["rank_key"],

            reverse=True

        )

        return results[:top_k]


if __name__ == "__main__":

    engine = SearchEngine()

    while True:

        query = input(
            "\nQuery: "
        )

        if query.lower() == "exit":
            break

        results = engine.search(
            query
        )

        print()

        for i, result in enumerate(
            results,
            start=1
        ):

            print(
                "=" * 60
            )

            print(
                f"#{i}"
            )

            print(
                f"Title: "
                f"{result['title']}"
            )

            print(
                f"Artist: "
                f"{result['artist']}"
            )

            print(
                f"Similarity: "
                f"{result['score']:.4f}"
            )

            print()

            print(
                result["text"]
            )

            print()