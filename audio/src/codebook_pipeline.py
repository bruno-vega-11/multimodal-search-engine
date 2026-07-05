import gc
import numpy as np
from audio_utils import  AcousticFeatureExtractor, AcousticCodebookBuilder, CODEBOOK_FILE_PATH, get_audio_batch, db

def run_pipeline():
    print("Iniciando Fase 2: Módulos de Extracción y Codebook para Audio...")
    
    conn = db.get_connection()
    
    extractor = AcousticFeatureExtractor(window_ms=500) 
    codebook_builder = AcousticCodebookBuilder(n_clusters=1000) 
    
    batch_size = 50 
    offset = 0 
    total_processed = 0 
    
    try:
        while True:
            records = get_audio_batch(conn, batch_size=batch_size, offset=offset)
            if not records:
                break
                
            batch_mfcc_list = [] # Lista para acumular los vectores de las 50 canciones
            
            for record_id, filepath in records:
                print(f"Procesando pista ID: {record_id}")
                mfcc_vectors = extractor.extract_from_path(filepath)
                
                if mfcc_vectors is not None and len(mfcc_vectors) > 0:
                    batch_mfcc_list.append(mfcc_vectors) # Agregamos la matriz a la lista
                    
            # Si logramos extraer vectores en este lote, los unimos y entrenamos
            if batch_mfcc_list:
                # np.vstack une todas las matrices en una sola matriz gigante
                combined_mfcc = np.vstack(batch_mfcc_list)
                print(f"-> Entrenando K-Means con bloque de {combined_mfcc.shape[0]} vectores...")
                codebook_builder.partial_fit(combined_mfcc)
                
            total_processed += len(records)
            offset += batch_size
            gc.collect() 
            
        print(f"\nProcesamiento completado. Total de audios analizados: {total_processed}")
        codebook_builder.export_codebook()
        
    except Exception as e:
        print(f"\nError en el pipeline principal: {e}") 
        
        # Validación para evitar el AttributeError secundario
        if hasattr(codebook_builder.kmeans, 'cluster_centers_'):
            print("Exportando el codebook parcial para no perder el progreso...")
            codebook_builder.export_codebook(CODEBOOK_FILE_PATH.replace(".npy", "_parcial.npy"))
        else:
            print("El modelo falló antes de generar el primer cluster. No hay nada que exportar.")
            
    finally:
        conn.close()

if __name__ == "__main__":
    run_pipeline()