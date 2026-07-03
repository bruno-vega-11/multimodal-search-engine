import nltk

from builder import (build_collection)

nltk.download("stopwords")

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