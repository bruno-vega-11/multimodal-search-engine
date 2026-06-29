import gc
from audio_utils import AudioDatabaseManager, AcousticFeatureExtractor
from audio_quantizer import AudioQuantizer
from inverted_index import InvertedIndex
from audio_utils import INDEX_FILE_PATH
def run_indexing_pipeline():
    print("Iniciando Generación de Histogramas e Índice Invertido...")
     
    db_manager = AudioDatabaseManager()
    extractor = AcousticFeatureExtractor(window_ms=100)
    quantizer = AudioQuantizer()
    inverted_index = InvertedIndex()
    
    batch_size = 10
    offset = 0
    total_indexed = 0
    
    try:
        while True:
            # Recuperar lote desde PostgreSQL
            records = db_manager.get_audio_batch(batch_size=batch_size, offset=offset)
            if not records:
                break 
                
            for audio_id, audio_bytea in records:
                print(f"Indexando pista ID: {audio_id}")
                 
                mfcc_vectors = extractor.extract_from_bytea(audio_bytea)
                
                if mfcc_vectors is not None: 
                    histogram = quantizer.quantize_to_histogram(mfcc_vectors) 
                    if histogram:
                        inverted_index.add_document(audio_id, histogram)
                        
            total_indexed += len(records)
            offset += batch_size
            gc.collect() # Prevenir desbordamiento de RAM
            
        print(f"\nProceso completado. Total de audios indexados: {total_indexed}")
         
        inverted_index.save_to_disk()
        
    except Exception as e:
        print(f"Error en el pipeline de indexación: {e}")
        # Guardar progreso parcial en caso de caída
        inverted_index.save_to_disk(INDEX_FILE_PATH.replace(".json", "_PARCIAL.json"))
    finally:
        db_manager.close()

if __name__ == "__main__":
    run_indexing_pipeline()