import nltk

from builder import (
    build_collection
)

nltk.download(
    "stopwords"
)

build_collection(

    csv_file=
    "data/raw/spotify_millsongdata.csv",

    processed_file=
    "data/processed/processed_chunks.jsonl",

    codebook_file=
    "data/processed/codebook.json",

    idf_file=
    "data/processed/idf.json",

    metadata_file=
    "data/processed/metadata.json",

    top_k=5000
)