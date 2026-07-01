import os
import io
import gc
import librosa
import numpy as np
import soundfile as sf
from tqdm import tqdm
from sklearn.cluster import MiniBatchKMeans

from db import get_connection

class AcousticFeatureExtractor:
    def __init__(self, sample_rate=22050, window_ms=100, overlap=0.5, n_mfcc=20):
        self.sr = sample_rate
        self.n_mfcc = n_mfcc
        self.n_fft = int((window_ms / 1000.0) * self.sr)
        self.hop_length = int(self.n_fft * (1.0 - overlap))

    def extract_from_bytea(self, bytea_data):
        try:
            audio_io = io.BytesIO(bytea_data)
            y, sr = sf.read(audio_io)
            if len(y.shape) > 1:
                y = librosa.to_mono(y.T)
            if sr != self.sr:
                y = librosa.resample(y, orig_sr=sr, target_sr=self.sr)
            mfccs = librosa.feature.mfcc(
                y=y, 
                sr=self.sr, 
                n_mfcc=self.n_mfcc, 
                n_fft=self.n_fft, 
                hop_length=self.hop_length
            )
            return mfccs.T 
            
        except Exception as e:
            # Evitamos romper la barra de tqdm usando write
            tqdm.write(f"❌ Error procesando binario de audio: {e}")
            return None


class AcousticCodebookBuilder:
    def __init__(self, n_clusters=500):
        self.n_clusters = n_clusters
        self.kmeans = MiniBatchKMeans(
            n_clusters=self.n_clusters, 
            random_state=42, 
            batch_size=1024,
            n_init="auto" 
        )

    def partial_fit(self, mfcc_features):
        if mfcc_features is not None and len(mfcc_features) > 0:
            self.kmeans.partial_fit(mfcc_features)

    def export_codebook(self, output_path):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        centroids = self.kmeans.cluster_centers_
        np.save(output_path, centroids)
        print(f"\nCodebook exportado exitosamente a: {output_path} (Shape: {centroids.shape})")
        return centroids


def run_pipeline():
    print("Iniciando Fase 2: Extracción de Características y Entrenamiento del Codebook...")
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    AUDIO_ROOT = os.path.dirname(SCRIPT_DIR) 
    
    RUTA_CODEBOOK = os.path.join(AUDIO_ROOT, "data", "codebook", "acoustic_codebook.npy")
    RUTA_PARCIAL = os.path.join(AUDIO_ROOT, "data", "codebook", "acoustic_codebook_parcial.npy")
    extractor = AcousticFeatureExtractor(window_ms=100) 
    codebook_builder = AcousticCodebookBuilder(n_clusters=500) 
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
    except Exception as e:
        print(f"❌ Error crítico al conectar a la base de datos mediante db.py: {e}")
        return

    query = "SELECT id, audio_data FROM audio_dataset ORDER BY id LIMIT %s OFFSET %s;"
    try:
        cursor.execute("SELECT COUNT(*) FROM audio_dataset;")
        total_audios = cursor.fetchone()[0]
        print(f"Total de pistas encontradas en la BD para analizar: {total_audios}")
    except Exception as e:
        print(f"No se pudo precalcular el total de registros: {e}")
        total_audios = None

    batch_size = 20  # Ajustado a 20 para optimizar el throughput de datos en red
    offset = 0 
    total_processed = 0 

    pbar = tqdm(total=total_audios, desc="Progreso del Pipeline", unit="track")
    
    try:
        while True:
            cursor.execute(query, (batch_size, offset))
            records = cursor.fetchall()
            
            if not records:
                break
                
            for record_id, audio_bytea in records:
                # Extracción matemática en memoria RAM
                mfcc_vectors = extractor.extract_from_bytea(audio_bytea)
                
                if mfcc_vectors is not None:
                    # Ajuste incremental de los centroides de K-Means
                    codebook_builder.partial_fit(mfcc_vectors)
                
                pbar.update(1)
                total_processed += 1
                
            offset += batch_size
            gc.collect() # Limpieza explícita del recolector de basura por los objetos binarios consumidos
            
        pbar.close()
        print(f"\n Procesamiento completado con éxito. Total de audios analizados: {total_processed}")
        codebook_builder.export_codebook(RUTA_CODEBOOK)
        
    except Exception as e:
        pbar.close()
        print(f"\nError fatal en el pipeline principal: {e}") 
        print("Salvando el estado actual... Exportando codebook parcial.")
        codebook_builder.export_codebook(RUTA_PARCIAL)
        
    finally:
        cursor.close()
        conn.close()
        print("Conexión a PostgreSQL liberada limpiamente.")

if __name__ == "__main__":
    run_pipeline()
