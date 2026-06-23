# src/indexing/spimi.py

import json
import os
import psutil
from collections import defaultdict

class SPIMI:
    def __init__(self, output_dir, max_memory_mb=30):
        self.output_dir = output_dir
        self.max_memory_mb = max_memory_mb
        self.block_count = 0
        self.process = psutil.Process(os.getpid())

        os.makedirs(output_dir, exist_ok=True)

    def current_memory_mb(self):
        return (self.process.memory_info().rss/1024/1024)

    def write_block(self, dictionary):
        block_path = os.path.join(self.output_dir, f"block_{self.block_count}.idx")

        with open(block_path,"w", encoding="utf-8") as f:

            for term in sorted(dictionary.keys()):
                postings = sorted(dictionary[term], key=lambda x: x[0])

                record = {"term": term, "postings": postings}

                f.write(json.dumps(record) + "\n")

        print(f"Bloque {self.block_count} escrito")

        self.block_count += 1

    def invert(self, token_generator):

        dictionary = defaultdict(list)

        processed_terms = 0

        for term, chunk_id, tf in token_generator:
            dictionary[term].append((chunk_id, tf))

            processed_terms += 1

            if (processed_terms% 100000 == 0):

                current_mb = (self.current_memory_mb())

                print(f"RAM: " f"{current_mb:.2f} MB")

                if (current_mb >= self.max_memory_mb):

                    print(f"Limite alcanzado " f"({current_mb:.2f} MB)")

                    self.write_block(dictionary)

                    dictionary = defaultdict(list)

        if dictionary:
            self.write_block(dictionary)

        print()

        print(f"Total bloques: " f"{self.block_count}")