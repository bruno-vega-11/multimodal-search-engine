# src/indexing/token_stream.py

import json

from collections import Counter


def token_stream(processed_file, codebook=None):
    """
    codebook: set/dict de terminos permitidos (top-k del codebook).
    Si es None, no filtra (comportamiento viejo, NO recomendado).
    """

    with open(processed_file, "r", encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            chunk_id = record["chunk_id"]
            tokens = record["tokens"]

            # Cuantizacion: solo se quedan los tokens que pertenecen
            # al codebook (top-k palabras). Igual que en imagen/audio,
            # donde un descriptor se descarta si no cae en ningun codeword.
            if codebook is not None:
                tokens = [t for t in tokens if t in codebook]

            if not tokens:
                continue

            counter = Counter(tokens)

            for term, tf in counter.items():
                yield (term, chunk_id, tf)