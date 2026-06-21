# src/build_final_index.py

from indexing.merger import (
    ExternalMerger
)


merger = ExternalMerger(

    blocks_dir=
    "data/index",

    output_file=
    "data/index/final_index.idx"

)

merger.merge()