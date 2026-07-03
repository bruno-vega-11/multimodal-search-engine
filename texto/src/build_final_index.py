from indexing.merger import (ExternalMerger)

merger = ExternalMerger(blocks_dir="data/index", output_songs_file="data/index/final_index.idx", output_chunks_file="data/index/final_index_chunks.idx")
merger.merge()