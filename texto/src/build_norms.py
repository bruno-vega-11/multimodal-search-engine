import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import json
import math
from collections import defaultdict

from metrics import MetricsTracker

def build_doc_norms(index_file, idf_file, output_file):

    print("Loading IDF...")

    with open(idf_file, "r", encoding="utf-8") as f:
        idf = json.load(f)

    print(f"Terms loaded: {len(idf)}")
    print("Computing norms...")
    
    norm_squares = defaultdict(float)

    processed_terms = 0

    with open(index_file, "r", encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            term = record["term"]
            postings = record["postings"]

            term_idf = idf.get(term, 0.0)

            for document_id, tf in postings:
                weight = (1 + math.log10(tf)) * term_idf
                norm_squares[str(document_id)] += (weight * weight)

            processed_terms += 1

            if (processed_terms% 10000 == 0):
                print(f"Processed terms: " f"{processed_terms}")

    print("Finalizing norms...")

    doc_norms = {}

    for document_id, value in (norm_squares.items()):
        doc_norms[document_id] = math.sqrt(value)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(doc_norms, f)

    print()

    print(f"Songs indexed: " f"{len(doc_norms)}")

    print(f"Saved: " f"{output_file}")


if __name__ == "__main__":
    with MetricsTracker() as m:
        build_doc_norms(index_file="data/index/final_index.idx", idf_file="data/processed/idf.json", output_file="data/index/doc_norms.json")
    print("\nMetricas build_doc_norms (songs):", m.result)

    with MetricsTracker() as m:
        build_doc_norms(index_file="data/index/final_index_chunks.idx", idf_file="data/processed/idf_chunks.json", output_file="data/index/doc_norms_chunks.json")
    print("\nMetricas build_doc_norms (chunks):", m.result)