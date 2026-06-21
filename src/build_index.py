import json

from indexing.token_stream import (
    token_stream
)

from indexing.spimi import (
    SPIMI
)

with open(
    "data/processed/codebook.json",
    "r",
    encoding="utf-8"
) as f:
    codebook = set(json.load(f).keys())

print(f"Codebook cargado: {len(codebook)} terminos")

generator = token_stream(
    "data/processed/processed_chunks.jsonl",
    codebook=codebook
)

spimi = SPIMI(

    output_dir=
    "data/index",

    # AJUSTA ESTO
    max_memory_mb=30
)

spimi.invert(
    generator
)