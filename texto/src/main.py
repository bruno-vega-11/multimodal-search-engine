import os
import nltk

from builder import (build_collection)

nltk.download("stopwords")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # texto/

CSV_PATH = os.path.join(BASE_DIR, "data", "raw", "spotify_millsongdata.csv")
PROCESSED_PATH = os.path.join(BASE_DIR, "data", "processed", "processed_chunks.jsonl")
CODEBOOK_PATH = os.path.join(BASE_DIR, "data", "processed", "codebook.json")
IDF_PATH = os.path.join(BASE_DIR, "data", "processed", "idf.json")
METADATA_PATH = os.path.join(BASE_DIR, "data", "processed", "metadata.json")

build_collection(
    csv_file=CSV_PATH,
    processed_file=PROCESSED_PATH,
    codebook_file=CODEBOOK_PATH,
    idf_file=IDF_PATH,
    metadata_file=METADATA_PATH,
    top_k=5000
)