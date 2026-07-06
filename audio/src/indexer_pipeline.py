import gc
import os
import glob
import json
from mutagen.easyid3 import EasyID3
from audio_utils import AcousticFeatureExtractor, LEXICON_FILE_PATH, INDEX_FILE_PATH, METADATA_FILE_PATH, RAW_AUDIO_DIR
from audio_quantizer import AudioQuantizer
from inverted_index import InvertedIndex

def extraer_metadata(filepath):
    """Extrae las etiquetas del MP3 localmente."""
    filename = os.path.basename(filepath)
    title = collaborators = album = "Desconocido"
    try:
        tags = EasyID3(filepath)
        title = tags.get("title", [title])[0]
        collaborators = tags.get("artist", [collaborators])[0]
        album = tags.get("album", [album])[0]
    except Exception:
        pass
    return {"filename": filename, "filepath": filepath, "title": title, "collaborators": collaborators, "album": album}

def run_indexing_pipeline():
    print("Iniciando Generación de Índices y Metadata (100% Local)...")
     
    extractor = AcousticFeatureExtractor(window_ms=500)
    quantizer = AudioQuantizer() 
    inverted_index = InvertedIndex()
    
    audio_files = sorted(glob.glob(os.path.join(RAW_AUDIO_DIR, "**", "*.mp3"), recursive=True))
    if not audio_files:
        print(f"Error: No se encontraron audios en {RAW_AUDIO_DIR}")
        return

    metadata_dict = {}
    total_indexed = 0
    
    try:
        for audio_id, filepath in enumerate(audio_files, start=1):
            print(f"Indexando pista ID: {audio_id}")
            mfcc_vectors = extractor.extract_from_path(filepath) 
            
            if mfcc_vectors is not None: 
                histogram = quantizer.quantize_to_histogram(mfcc_vectors) 
                if histogram:
                    # Prevenimos el error de tipos de NumPy al guardar JSONL
                    histogram = {int(word): int(freq) for word, freq in histogram.items()}
                    inverted_index.add_document(audio_id, histogram)
                    
                    # Generamos el diccionario de metadata
                    metadata_dict[str(audio_id)] = extraer_metadata(filepath)
                    total_indexed += 1
                    
            if audio_id % 50 == 0:
                gc.collect() 
            
        print(f"\nProceso completado. Total de audios indexados: {total_indexed}")
        
        # Guardamos índice masivo
        inverted_index.save_with_offsets()
        
        # Guardamos metadata JSON
        with open(METADATA_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(metadata_dict, f, ensure_ascii=False, indent=2)
        print(f"Metadata local guardada exitosamente en {METADATA_FILE_PATH}")
        
    except Exception as e:
        print(f"Error en el pipeline de indexación: {e}")
        inverted_index.save_with_offsets(
            LEXICON_FILE_PATH.replace(".json", "_PARCIAL.json"), 
            INDEX_FILE_PATH.replace(".jsonl", "_PARCIAL.jsonl")
        )

if __name__ == "__main__":
    run_indexing_pipeline()