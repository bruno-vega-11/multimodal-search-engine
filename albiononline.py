import os
from collections import defaultdict
from tqdm import tqdm
from db import get_connection
from imagen.src.image_local_search import ImageLocalSearch

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def actualizar_a_tfidf():
    print("Cargando ImageLocalSearch (lexicon + docs + idf)...")
    motor = ImageLocalSearch(base_dir=SCRIPT_DIR)

    print(f"Total de imagenes: {motor.total_docs}")
    print("Reconstruyendo vectores TF-IDF por doc_id (una sola pasada por el indice invertido)...")

    K = 1000  # numero de clusters del codebook, ajusta si es distinto
    vectores = defaultdict(lambda: [0.0] * K)

    # Una sola pasada por todas las posting lists, acumulando tfidf en la
    # posicion word_id de cada doc_id. Mucho mas rapido que buscar doc por doc.
    for word_id_str in tqdm(motor.lexicon.keys(), desc="Procesando clusters"):
        word_id = int(word_id_str)
        idf_weight = motor.idf[word_id_str]
        posting_list = motor._get_posting_list(word_id_str)
        for doc_id, tf in posting_list:
            vectores[doc_id][word_id] = tf * idf_weight

    print(f"Vectores reconstruidos: {len(vectores)}")
    conn = get_connection()
    cursor = conn.cursor()

    update_query = """
        UPDATE fashion_images
        SET histograma_visual = %s::vector
        WHERE id = %s;
    """

    procesados = 0
    errores = 0

    for doc_id, vec in tqdm(vectores.items(), desc="Actualizando en Postgres"):
        try:
            vector_str = "[" + ",".join(f"{x:.6f}" for x in vec) + "]"
            cursor.execute(update_query, (vector_str, doc_id))
            procesados += 1
            if procesados % 1000 == 0:
                conn.commit()
        except Exception as e:
            errores += 1
            tqdm.write(f"Error en doc_id {doc_id}: {e}")
            continue

    conn.commit()
    cursor.close()
    conn.close()
    motor.close()

    print("\n=== RESUMEN ===")
    print(f"Actualizados: {procesados}")
    print(f"Errores:      {errores}")


if __name__ == "__main__":
    actualizar_a_tfidf()

