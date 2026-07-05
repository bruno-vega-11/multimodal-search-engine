import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import json
from indexing.token_stream import (token_stream)
from indexing.spimi import (SPIMI)
from metrics import MetricsTracker

with open("data/processed/codebook.json", "r", encoding="utf-8") as f:
    codebook = set(json.load(f).keys())

print(f"Codebook cargado: {len(codebook)} terminos")

generator = token_stream("data/processed/processed_chunks.jsonl", codebook=codebook)

spimi = SPIMI(output_dir="data/index", max_memory_mb=30)

with MetricsTracker() as m:
    spimi.invert(generator)

print("\nMetricas spimi.invert:", m.result)
