# src/build_final_index.py
import os
from indexing.merger import (ExternalMerger)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # → texto/

merger = ExternalMerger(
    blocks_dir=os.path.join(BASE_DIR, "data", "index"),
    output_file=os.path.join(BASE_DIR, "data", "index", "final_index.idx")
)
merger.merge()