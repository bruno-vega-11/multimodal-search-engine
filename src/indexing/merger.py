# src/indexing/merger.py

import os
import json
import heapq


class ExternalMerger:

    def __init__(
        self,
        blocks_dir,
        output_file
    ):

        self.blocks_dir = blocks_dir

        self.output_file = output_file

    def merge(self):

        block_files = sorted(

            [
                os.path.join(
                    self.blocks_dir,
                    file
                )

                for file in os.listdir(
                    self.blocks_dir
                )

                if file.startswith(
                    "block_"
                )
            ]

        )

        handles = [

            open(
                file,
                "r",
                encoding="utf-8"
            )

            for file in block_files

        ]

        heap = []

        for block_id, f in enumerate(
            handles
        ):

            line = f.readline()

            if line:

                record = json.loads(
                    line
                )

                heapq.heappush(

                    heap,

                    (
                        record["term"],
                        block_id,
                        record["postings"]
                    )

                )

        with open(
            self.output_file,
            "w",
            encoding="utf-8"
        ) as out:

            current_term = None

            current_postings = []

            while heap:

                term, block_id, postings = (
                    heapq.heappop(
                        heap
                    )
                )

                if current_term == term:

                    current_postings.extend(
                        postings
                    )

                else:

                    if current_term is not None:

                        current_postings.sort(
                            key=lambda x: x[0]
                        )

                        out.write(

                            json.dumps(
                                {
                                    "term":
                                    current_term,

                                    "postings":
                                    current_postings
                                }
                            )

                            + "\n"

                        )

                    current_term = term

                    current_postings = postings

                next_line = handles[
                    block_id
                ].readline()

                if next_line:

                    record = json.loads(
                        next_line
                    )

                    heapq.heappush(

                        heap,

                        (
                            record["term"],
                            block_id,
                            record["postings"]
                        )

                    )

            if current_term is not None:

                current_postings.sort(
                    key=lambda x: x[0]
                )

                out.write(

                    json.dumps(
                        {
                            "term":
                            current_term,

                            "postings":
                            current_postings
                        }
                    )

                    + "\n"

                )

        for f in handles:

            f.close()

        print()

        print(
            "MERGE COMPLETADO"
        )

        print(
            f"Bloques fusionados: "
            f"{len(block_files)}"
        )

        print(
            f"Índice final: "
            f"{self.output_file}"
        )