
import os
import json
from db import get_connection

BATCH_SIZE = 5000

def load_schema(conn, schema_path=None):
    if schema_path is None:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        schema_path = os.path.join(BASE_DIR,"init.sql")


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
    BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # -> texto
    DATA = os.path.join(BASE_DIR,"texto","data")

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
