import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import nltk

from builder import (build_collection)
from metrics import MetricsTracker

nltk.download("stopwords")

with MetricsTracker() as m:
    build_collection(
        csv_file="data/raw/spotify_millsongdata.csv",

        processed_file="data/processed/processed_chunks.jsonl",

        codebook_file="data/processed/codebook.json",

        idf_file="data/processed/idf.json",

        idf_chunks_file="data/processed/idf_chunks.json",

        metadata_file="data/processed/metadata.json",

        documents_file="data/processed/documents.json",

        top_k=10000
    )

print("\nMetricas build_collection:", m.result)