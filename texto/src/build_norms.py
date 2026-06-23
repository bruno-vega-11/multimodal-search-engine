# src/build_norms.py
import os
import json
import math
from collections import defaultdict

def build_doc_norms(index_file, idf_file, output_file):

    print("Loading IDF...")

    with open(idf_file, "r", encoding="utf-8") as f:
        idf = json.load(f)

    print(f"Terms loaded: {len(idf)}")
    print("Computing norms...")
    # acumula suma de cuadrados
    norm_squares = defaultdict(float)

    processed_terms = 0

    with open(index_file, "r", encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            term = record["term"]
            postings = record["postings"]

            term_idf = idf.get(term, 0.0)

            for chunk_id, tf in postings:
                # TF-IDF
                weight = (1 + math.log10(tf)) * term_idf
                norm_squares[str(chunk_id)] += (weight * weight)

            processed_terms += 1

            if (processed_terms% 10000 == 0):
                print(f"Processed terms: " f"{processed_terms}")

    print("Finalizing norms...")

    doc_norms = {}

    for chunk_id, value in (norm_squares.items()):
        doc_norms[chunk_id] = math.sqrt(value)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(doc_norms, f)

    print()

    print(f"Chunks indexed: " f"{len(doc_norms)}")

    print(f"Saved: " f"{output_file}")


if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # -> texto
    build_doc_norms(
        index_file=os.path.join(BASE_DIR,"data","index","final_index.idx"), 
        idf_file=os.path.join(BASE_DIR,"data","processed","idf.json"), 
        output_file=os.path.join(BASE_DIR,"data","index","doc_norms.json")
    )