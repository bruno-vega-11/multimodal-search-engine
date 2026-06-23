# src/load_to_postgres.py
#
# Migra la persistencia de texto (Fase 2) de archivos locales
# (JSON/JSONL + indice SPIMI en disco) a tablas Postgres.
#
# Corre esto UNA VEZ despues de haber generado:
#   data/processed/codebook.json
#   data/processed/idf.json
#   data/processed/metadata.json
#   data/index/final_index.idx
#   data/index/dictionary.json
#   data/index/doc_norms.json
#
# (es decir, despues de correr main.py, build_index.py,
#  build_final_index.py, build_dictionary.py y build_norms.py)
#
# Usa psycopg v3 (no psycopg2). executemany() reemplaza a
# psycopg2.extras.execute_values(); en psycopg v3, executemany
# ya hace batching eficiente internamente.
#
# Uso:
#   python src/load_to_postgres.py
import os
import json
from db import get_connection

BATCH_SIZE = 5000

def load_schema(conn, schema_path=None):

    if schema_path is None:
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # -> texto
        schema_path = os.path.join(BASE_DIR,"src","sql","schema.sql")

    print("Aplicando schema...")

    with open(schema_path, encoding="utf-8") as f:
        schema_sql = f.read()
    with conn.cursor() as cur:
        cur.execute(schema_sql)
    conn.commit()

def _batched(rows, batch_size):
    for i in range(0, len(rows), batch_size):
        yield rows[i:i + batch_size]

def load_codebook(conn, codebook_file):
    print("Cargando codebook...")

    with open(codebook_file, encoding="utf-8") as f:
        codebook = json.load(f)

    rows = [(term, rank) for term, rank in codebook.items()]

    with conn.cursor() as cur:
        cur.execute("TRUNCATE codebook CASCADE")
        for batch in _batched(rows, BATCH_SIZE):
            cur.executemany(
                "INSERT INTO codebook (term, rank) VALUES (%s, %s)",
                batch
            )
    conn.commit()

    print(f"  {len(rows)} terminos cargados.")


def load_metadata(conn, metadata_file):
    print("Cargando metadata...")
    rows = []
    with open(metadata_file, encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            rows.append((record["chunk_id"], record["document_id"], record["title"], record["artist"], record["text"],))

    with conn.cursor() as cur:
        cur.execute("TRUNCATE metadata CASCADE")
        for batch in _batched(rows, BATCH_SIZE):
            cur.executemany(
                """
                INSERT INTO metadata
                    (chunk_id, document_id, title, artist, text)
                VALUES (%s, %s, %s, %s, %s)
                """,
                batch
            )
    conn.commit()
    print(f"  {len(rows)} chunks cargados.")


def load_doc_norms(conn, doc_norms_file):
    print("Cargando doc_norms...")

    with open(doc_norms_file, encoding="utf-8") as f:
        doc_norms = json.load(f)

    rows = [(int(chunk_id), norm) for chunk_id, norm in doc_norms.items()]

    with conn.cursor() as cur:
        for batch in _batched(rows, BATCH_SIZE):
            cur.executemany(
                "INSERT INTO doc_norms (chunk_id, norm_value) VALUES (%s, %s)",
                batch
            )

    conn.commit()

    print(f"  {len(rows)} normas cargadas.")


def load_term_index(conn, idf_file, index_file):
    """
    Fusiona idf.json y final_index.idx en la tabla term_index:
    una fila por termino, con su idf_value y su posting list
    completa empacada como JSONB.

    final_index.idx ya trae cada termino con su posting list en
    el formato exacto que necesitamos como JSONB:
        {"term": "aa", "postings": [[chunk_id, tf], ...]}
    asi que la carga es casi directa, solo agregamos el idf_value
    correspondiente a cada termino antes de insertar.

    Se usa COPY (no INSERT/executemany): aunque ahora son solo
    ~5,000 filas (una por termino, no por chunk_id), cada valor
    de "postings" es un array JSON que puede tener miles de
    elementos (ej. "love" con ~57,809 pares chunk_id/tf), asi
    que el volumen total de datos a transferir sigue siendo
    grande. COPY evita el overhead de armar una sentencia SQL
    por fila para esos blobs.
    """

    print("Cargando term_index (idf + postings combinados)...")

    with open(idf_file, encoding="utf-8") as f:
        idf = json.load(f)

    with conn.cursor() as cur:
        cur.execute("TRUNCATE term_index")

    conn.commit()
    total = 0

    with conn.cursor() as cur:
        with open(index_file, encoding="utf-8") as f:
            with cur.copy("COPY term_index (term, idf_value, postings) FROM STDIN") as copy:
                for line in f:
                    record = json.loads(line)
                    term = record["term"]

                    if term not in idf:
                        continue

                    idf_value = idf[term]
                    postings_json = json.dumps(record["postings"])
                    copy.write_row((term, idf_value, postings_json))
                    total += 1
    conn.commit()
    print(f"  {total} terminos cargados (idf + postings).")


def main():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # -> texto
    DATA = os.path.join(BASE_DIR,"data")

    conn = get_connection()
    try:
        load_schema(conn)
        # Orden importa por las foreign keys:
        # codebook -> term_index
        # metadata -> doc_norms
        load_codebook(conn, os.path.join(DATA,"processed","codebook.json"))
        load_metadata(conn, os.path.join(DATA,"processed","metadata.json"))
        load_doc_norms(conn, os.path.join(DATA,"index","doc_norms.json"))
        load_term_index(conn, os.path.join(DATA, "processed", "idf.json"),
                              os.path.join(DATA, "index",     "final_index.idx"))
        print("\nCarga completa.")

    finally:
        conn.close()


if __name__ == "__main__":
    main()