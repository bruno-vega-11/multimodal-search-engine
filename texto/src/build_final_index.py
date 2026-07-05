import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from indexing.merger import (ExternalMerger)
from metrics import MetricsTracker

merger = ExternalMerger(blocks_dir="data/index", output_songs_file="data/index/final_index.idx", output_chunks_file="data/index/final_index_chunks.idx")

with MetricsTracker() as m:
    merger.merge()

print("\nMetricas merger.merge:", m.result)