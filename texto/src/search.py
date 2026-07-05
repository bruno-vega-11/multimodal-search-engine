import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import json
import math
from collections import Counter, defaultdict

from preprocess import preprocess_text
from metrics import MetricsTracker

class SearchEngine:
    def __init__(
        self,
        dictionary_file="data/index/dictionary.json",
        index_file="data/index/final_index.idx",
        idf_file="data/processed/idf.json",
        doc_norms_file="data/index/doc_norms.json",
        documents_file="data/processed/documents.json",
        dictionary_chunks_file="data/index/dictionary_chunks.json",
        index_chunks_file="data/index/final_index_chunks.idx",
        idf_chunks_file="data/processed/idf_chunks.json",
        doc_norms_chunks_file="data/index/doc_norms_chunks.json",
        metadata_file="data/processed/metadata.json",
    ):
        with open(dictionary_file, "r", encoding="utf-8") as f:
            self.dictionary = json.load(f)

        with open(idf_file, "r", encoding="utf-8") as f:
            self.idf = json.load(f)

        with open(doc_norms_file, "r", encoding="utf-8") as f:
            self.doc_norms = json.load(f)

        self.documents = {}
        with open(documents_file, "r", encoding="utf-8") as f:
            for line in f:
                record = json.loads(line)
                self.documents[record["document_id"]] = record

        self._index_handle = open(index_file, "r", encoding="utf-8")

        with open(dictionary_chunks_file, "r", encoding="utf-8") as f:
            self.dictionary_chunks = json.load(f)

        with open(idf_chunks_file, "r", encoding="utf-8") as f:
            self.idf_chunks = json.load(f)

        with open(doc_norms_chunks_file, "r", encoding="utf-8") as f:
            self.doc_norms_chunks = json.load(f)

        self.metadata = {}
        with open(metadata_file, "r", encoding="utf-8") as f:
            for line in f:
                record = json.loads(line)
                self.metadata[record["chunk_id"]] = record

        self._index_chunks_handle = open(index_chunks_file, "r", encoding="utf-8")

        print(
            f"Ready (song index: {len(self.dictionary)} terminos, "
            f"{len(self.documents)} canciones | chunk index: "
            f"{len(self.dictionary_chunks)} terminos, {len(self.metadata)} chunks)."
        )

    def close(self):
        self._index_handle.close()
        self._index_chunks_handle.close()

    def _fetch_postings(self, term, dictionary, index_handle):
        offset = dictionary.get(term)

        if offset is None:
            return None

        index_handle.seek(offset)
        line = index_handle.readline()
        record = json.loads(line)

        return record["postings"]

    def _rank(self, query_tf, idf_map, dictionary, index_handle, doc_norms, top_k, dedupe_key=None):
        query_vector = {}
        term_postings = {}

        for term, tf in query_tf.items():
            idf_value = idf_map.get(term)

            if idf_value is None:
                continue

            postings = self._fetch_postings(term, dictionary, index_handle)

            if postings is None:
                continue

            query_vector[term] = (1 + math.log10(tf)) * idf_value
            term_postings[term] = postings

        if not query_vector:
            return []

        query_norm = math.sqrt(sum(w * w for w in query_vector.values()))

        dot_products = defaultdict(float)

        for term, q_weight in query_vector.items():
            term_idf = idf_map[term]
            for doc_id, tf in term_postings[term]:
                d_weight = (1 + math.log10(tf)) * term_idf
                dot_products[doc_id] += q_weight * d_weight

        if not dot_products:
            return []

        scores = []

        for doc_id, dot in dot_products.items():
            doc_norm = doc_norms.get(str(doc_id), 0)
            if doc_norm == 0 or query_norm == 0:
                continue
            cosine = dot / (query_norm * doc_norm)
            scores.append((doc_id, cosine))

        scores.sort(key=lambda x: x[1], reverse=True)

        if dedupe_key is not None:
            seen = set()
            deduped = []
            for doc_id, score in scores:
                key = dedupe_key(doc_id)
                if key in seen:
                    continue
                seen.add(key)
                deduped.append((doc_id, score))
            scores = deduped

        return scores[:top_k]

    def search(self, query, top_k=10):
        terms = preprocess_text(query)
        print("TOKENS:", terms)
        if not terms:
            return {"by_song": [], "by_chunk": []}

        query_tf = Counter(terms)

        top_songs = self._rank(query_tf, self.idf, self.dictionary, self._index_handle, self.doc_norms, top_k)

        top_chunks = self._rank(
            query_tf, self.idf_chunks, self.dictionary_chunks, self._index_chunks_handle, self.doc_norms_chunks, top_k,
            dedupe_key=lambda chunk_id: self.metadata[chunk_id]["document_id"],
        )

        by_song = []

        for document_id, score in top_songs:
            doc = self.documents.get(document_id)
            if doc is None:
                continue

            by_song.append({
                "document_id": document_id,
                "score": score,
                "title": doc["title"],
                "artist": doc["artist"],
            })

        by_chunk = []

        for chunk_id, score in top_chunks:
            chunk = self.metadata.get(chunk_id)
            if chunk is None:
                continue

            by_chunk.append({
                "chunk_id": chunk_id,
                "document_id": chunk["document_id"],
                "score": score,
                "title": chunk["title"],
                "artist": chunk["artist"],
                "text": chunk["text"],
            })

        return {"by_song": by_song, "by_chunk": by_chunk}


if __name__ == "__main__":
    engine = SearchEngine()
    try:
        while True:
            query = input("\nQuery: ")
            if query.lower() == "exit":
                break
            with MetricsTracker() as m:
                results = engine.search(query)

            print()
            print("Metricas:", m.result)
            print("### Ranking por cancion ###")
            for i, result in enumerate(results["by_song"], start=1):
                print("=" * 60)
                print(f"#{i}")
                print(f"Title: {result['title']}")
                print(f"Artist: {result['artist']}")
                print(f"Similarity: {result['score']:.4f}")
                print()

            print("### Ranking por chunk ###")
            for i, result in enumerate(results["by_chunk"], start=1):
                print("=" * 60)
                print(f"#{i}")
                print(f"Title: {result['title']}")
                print(f"Artist: {result['artist']}")
                print(f"Similarity: {result['score']:.4f}")
                print(f"Text: {result['text']}")
                print()
    finally:
        engine.close()
