from audio_utils import CODEBOOK_FILE_PATH, AudioDatabaseManager, AcousticFeatureExtractor, AcousticCodebookBuilder
import gc
def run_pipeline():
    print("Iniciando Fase 2: Módulos de Extracción y Codebook para Audio...")
    
    db_manager = AudioDatabaseManager()
    extractor = AcousticFeatureExtractor(window_ms=100) 
    codebook_builder = AcousticCodebookBuilder(n_clusters=500) 
    batch_size = 10 
    offset = 0 
    total_processed = 0 
    try:
        while True:
            records = db_manager.get_audio_batch(batch_size=batch_size, offset=offset)
            if not records:
                break
                
            for record_id, audio_bytea in records:
                print(f"Procesando pista ID: {record_id}")
                mfcc_vectors = extractor.extract_from_bytea(audio_bytea)
                
                if mfcc_vectors is not None:
                    codebook_builder.partial_fit(mfcc_vectors)
                    
            total_processed += len(records)
            offset += batch_size
            gc.collect() 
        print(f"\nProcesamiento completado. Total de audios analizados: {total_processed}")
        codebook_builder.export_codebook(CODEBOOK_FILE_PATH)
        
    except Exception as e:
        print(f"Error en el pipeline principal: {e}") 
        print("Exportando el codebook parcial para no perder el progreso...")
        codebook_builder.export_codebook(CODEBOOK_FILE_PATH.replace(".npy", "_parcial.npy"))
    finally:
        db_manager.close()

if __name__ == "__main__":
    run_pipeline()