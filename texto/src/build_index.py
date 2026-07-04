import os,json
from indexing.token_stream import (token_stream)
from indexing.spimi import (SPIMI)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(BASE_DIR,"data","processed","codebook.json"),"r",encoding="utf-8") as f:
    codebook = set(json.load(f).keys())

print(f"Codebook cargado: {len(codebook)} terminos")

generator = token_stream(
    os.path.join(BASE_DIR,"data","processed","processed_chunks.jsonl"),
    codebook=codebook
)

spimi = SPIMI(
    output_dir=os.path.join(BASE_DIR,"data","index"), 
    max_memory_mb=30
)

spimi.invert(generator)
