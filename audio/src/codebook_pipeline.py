import gc
import glob
import os
import numpy as np
from audio_utils import AcousticFeatureExtractor, AcousticCodebookBuilder, CODEBOOK_FILE_PATH, RAW_AUDIO_DIR

def run_pipeline():
    print("Iniciando Fase 2: Entrenamiento del Codebook (100% Local)...")
    
    extractor = AcousticFeatureExtractor(window_ms=500) 
    codebook_builder = AcousticCodebookBuilder(n_clusters=1000) 
    
    # 1. Buscamos todos los MP3 de manera local y determinista
    audio_files = sorted(glob.glob(os.path.join(RAW_AUDIO_DIR, "**", "*.mp3"), recursive=True))
    print(f"Audios encontrados: {len(audio_files)}")
    
    batch_size = 50 
    total_processed = 0 
    
    try:
        # Iteramos los archivos en lotes
        for i in range(0, len(audio_files), batch_size):
            batch_files = audio_files[i:i + batch_size]
            batch_mfcc_list = []
            
            for filepath in batch_files:
                record_id = audio_files.index(filepath) + 1 # ID simulado localmente
                print(f"Procesando pista ID: {record_id}")
                mfcc_vectors = extractor.extract_from_path(filepath)
                
                if mfcc_vectors is not None and len(mfcc_vectors) > 0:
                    batch_mfcc_list.append(mfcc_vectors)
                    
            if batch_mfcc_list:
                combined_mfcc = np.vstack(batch_mfcc_list)
                print(f"-> Entrenando K-Means con {combined_mfcc.shape[0]} vectores...")
                codebook_builder.partial_fit(combined_mfcc)
                
            total_processed += len(batch_files)
            gc.collect() 
            
        print(f"\nProcesamiento completado. Audios analizados: {total_processed}")
        codebook_builder.export_codebook()
        
    except Exception as e:
        print(f"\nError en el pipeline: {e}") 
        if hasattr(codebook_builder.kmeans, 'cluster_centers_'):
            codebook_builder.export_codebook(CODEBOOK_FILE_PATH.replace(".npy", "_parcial.npy"))
            
if __name__ == "__main__":
    run_pipeline()