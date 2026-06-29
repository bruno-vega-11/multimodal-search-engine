from audio_search_engine import AudioSearchEngine
from audio_utils import AudioDatabaseManager
from psycopg2 import sql

def run_search_test():
    search_engine = AudioSearchEngine()
    db_manager = AudioDatabaseManager()
    db_manager.connect()
    
    test_audio_id = 24
    print(f"\n--- INICIANDO PRUEBA DE BÚSQUEDA ---")
    print(f"Extrayendo canción de prueba (ID: {test_audio_id}) desde la base de datos...")
    
    try:
        cursor = db_manager.conn.cursor()
        cursor.execute("SELECT title, collaborators, audio_data FROM audio_dataset WHERE audio_id = %s", (test_audio_id,))
        record = cursor.fetchone()
        
        if not record:
            print("No se encontró el audio de prueba en la base de datos.")
            return
            
        test_title, test_artist, query_bytea = record
        print(f"Canción a buscar: '{test_title}' de {test_artist}")
        print("Analizando audio y buscando similitudes en el índice...")
        

        top_k_results = search_engine.search(query_bytea, top_k=5)
        
        print("\n--- RESULTADOS DE LA BÚSQUEDA ---")
        if not top_k_results:
            print("No se encontraron coincidencias.")
        else:
            for rank, result in enumerate(top_k_results, start=1):
                matched_id = result["audio_id"]
                score = result["similarity_score"]
                
                cursor.execute("SELECT title, collaborators,filename FROM audio_dataset WHERE audio_id = %s", (matched_id,))
                match_data = cursor.fetchone()
                
                if match_data:
                    match_title, match_artist, filename = match_data
                    print(f"#{rank} | Score: {score} | ID: {matched_id} | Filename: {filename} | '{match_title}' - {match_artist}")
                else:
                    print(f"#{rank} | Score: {score} | ID: {matched_id} | (Metadatos no encontrados)")

    except Exception as e:
        print(f"Error durante la prueba de búsqueda: {e}")
    finally:
        db_manager.close()

if __name__ == "__main__":
    run_search_test()