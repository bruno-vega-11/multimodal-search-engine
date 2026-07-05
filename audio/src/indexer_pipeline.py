import gc
from audio_utils import AudioDatabaseManager, AcousticFeatureExtractor,LEXICON_FILE_PATH, INDEX_FILE_PATH
from audio_quantizer import AudioQuantizer
from inverted_index import InvertedIndex

def run_indexing_pipeline():
    print("Iniciando Generación de Histogramas e Índice Invertido...")
     
    db_manager = AudioDatabaseManager()
    extractor = AcousticFeatureExtractor(window_ms=500)
    quantizer = AudioQuantizer()
    inverted_index = InvertedIndex()
    
    batch_size = 10
    offset = 0
    total_indexed = 0
    
    try:
        while True:
            records = db_manager.get_audio_batch(batch_size=batch_size, offset=offset)
            if not records:
                break 
                
            for audio_id, filepath in records:
                print(f"Indexando pista ID: {audio_id}")
                 
                mfcc_vectors = extractor.extract_from_path(filepath) # Llamada local
                
                if mfcc_vectors is not None: 
                    histogram = quantizer.quantize_to_histogram(mfcc_vectors) 
                    if histogram:
                        inverted_index.add_document(audio_id, histogram)
                        
            total_indexed += len(records)
            offset += batch_size
            gc.collect() 
            
        print(f"\nProceso completado. Total de audios indexados: {total_indexed}")
         
        # GUARDAMOS USANDO LA ARQUITECTURA DE OFFSETS
        inverted_index.save_with_offsets()
        
    except Exception as e:
        print(f"Error en el pipeline de indexación: {e}")
        inverted_index.save_with_offsets(
            LEXICON_FILE_PATH.replace(".json", "_PARCIAL.json"), 
            INDEX_FILE_PATH.replace(".jsonl", "_PARCIAL.jsonl")
        )
    finally:
        db_manager.close()

if __name__ == "__main__":
    run_indexing_pipeline()