"""Construye el índice invertido en disco para la búsqueda de imágenes,
mismo esquema que texto y audio (lexicon.json de offsets + postings JSONL).

Entrada:  imagen/data/processed/vectores_fashion.jsonl  (histogramas densos)
Salidas:  imagen/data/processed/lexicon.json            (word_id -> byte offset)
          imagen/data/processed/inverted_index.jsonl    (una línea por word_id: [[img_id, tf], ...])
          imagen/data/processed/docs.json               (img_id -> {nombre_archivo, ruta_original})

El id de cada imagen es su índice de línea (0-based) dentro del JSONL de vectores.
Así ya no hace falta cargar los 44k histogramas a RAM: en consulta solo se leen,
por seek(), las listas de postings de las palabras visuales presentes en la query.
"""
import os
import json
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROCESSED_DIR = os.path.join(SCRIPT_DIR, "..", "data", "processed")

VECTORES_PATH = os.path.join(PROCESSED_DIR, "vectores_fashion.jsonl")
LEXICON_PATH = os.path.join(PROCESSED_DIR, "lexicon.json")
INDEX_PATH = os.path.join(PROCESSED_DIR, "inverted_index.jsonl")
DOCS_PATH = os.path.join(PROCESSED_DIR, "docs.json")


def construir():
    # word_id -> lista de [img_id, tf]
    postings = defaultdict(list)
    docs = {}

    print(f"[BUILD] Leyendo histogramas de: {VECTORES_PATH}")
    with open(VECTORES_PATH, "r", encoding="utf-8") as f:
        for img_id, linea in enumerate(f):
            linea = linea.strip()
            if not linea:
                continue
            registro = json.loads(linea)
            docs[img_id] = {
                "nombre_archivo": registro["nombre_archivo"],
                "ruta_original": registro["ruta_original"],
            }
            for word_id, tf in enumerate(registro["histograma"]):
                if tf:  # solo palabras visuales presentes (histograma disperso)
                    postings[word_id].append([img_id, int(tf)])

    print(f"[BUILD] {len(docs)} imágenes, {len(postings)} palabras visuales con postings.")

    # Escribe el índice invertido y va registrando el offset de byte de cada línea.
    lexicon = {}
    with open(INDEX_PATH, "wb") as f_idx:
        for word_id, lista in postings.items():
            offset = f_idx.tell()
            lexicon[str(word_id)] = offset
            f_idx.write((json.dumps(lista) + "\n").encode("utf-8"))

    with open(LEXICON_PATH, "w", encoding="utf-8") as f_lex:
        json.dump(lexicon, f_lex)

    with open(DOCS_PATH, "w", encoding="utf-8") as f_docs:
        json.dump(docs, f_docs)

    print(f"[BUILD] Lexicon -> {LEXICON_PATH}")
    print(f"[BUILD] Índice  -> {INDEX_PATH}")
    print(f"[BUILD] Docs    -> {DOCS_PATH}")
    print("[BUILD] Listo.")


if __name__ == "__main__":
    construir()
