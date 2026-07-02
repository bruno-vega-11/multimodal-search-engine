import json
from collections import Counter

def token_stream(processed_file, codebook=None):
    with open(processed_file, "r", encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            chunk_id = record["chunk_id"]
            tokens = record["tokens"]
            if codebook is not None:
                tokens = [t for t in tokens if t in codebook]
            if not tokens:
                continue
            counter = Counter(tokens)
            for term, tf in counter.items():
                yield (term, chunk_id, tf)
