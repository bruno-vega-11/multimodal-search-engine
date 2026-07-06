import time
from audio_search_engine import AudioSearchEngine

def test_engine():
    print("--- INICIANDO PRUEBA DEL SISTEMA MULTIMODAL (100% LOCAL) ---")
    
    try:
        engine = AudioSearchEngine()
    except Exception as e:
        print(f"Fallo al levantar el motor: {e}")
        return

    # 1. Buscamos la canción de prueba directamente en la RAM (No SQL)
    target_id = "492" # Prueba con el número que gustes
    if target_id not in engine.metadata:
        print(f"No se encontró la canción con ID {target_id} en la metadata local.")
        return
        
    record = engine.metadata[target_id]
    audio_id = target_id
    title = record['title']
    filepath = record['filepath']
    
    print(f"\n[QUERY] Buscando canciones similares a: ID {audio_id} - '{title}'")
    print(f"Ruta: {filepath}")
    
    # 2. Ejecutamos la búsqueda
    print("\nCalculando similitudes (TF-IDF + Coseno)...")
    start_time = time.perf_counter()
    
    resultados = engine.search(query_filepath=filepath, top_k=5)
    
    latency = (time.perf_counter() - start_time) * 1000 
    print(f"Búsqueda resuelta en {latency:.2f} ms")
    
    # 3. Mostramos Ranking
    print("\n--- TOP 5 RESULTADOS ---")
    for i, res in enumerate(resultados, start=1):
        match_id = str(res['audio_id'])
        score = res['similarity_score']
        
        # Recuperamos la información de nuestra caché local
        if match_id in engine.metadata:
            match_title = engine.metadata[match_id]['title']
            match_artist = engine.metadata[match_id]['collaborators']
            print(f"#{i} | Score: {score:.4f} | ID: {match_id} | {match_title} - {match_artist}")
        else:
            print(f"#{i} | Score: {score:.4f} | ID: {match_id} | (Sin metadatos)")

if __name__ == "__main__":
    test_engine()