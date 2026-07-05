import os
import librosa
import numpy as np
from sklearn.cluster import MiniBatchKMeans
from dotenv import load_dotenv
import sys
load_dotenv()


# Rutas de archivos y directorios

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SRC_DIR)
CODEBOOK_DIR = os.path.join(PROJECT_ROOT,"data", "codebook")
PROCESSED_DIR = os.path.join(PROJECT_ROOT,"data", "processed")
ROOT_DIR = os.path.dirname(PROJECT_ROOT)             

sys.path.append(ROOT_DIR)
import db

os.makedirs(CODEBOOK_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

CODEBOOK_FILE_PATH = os.path.join(CODEBOOK_DIR, "acoustic_codebook.npy")
LEXICON_FILE_PATH = os.path.join(PROCESSED_DIR, "lexicon.json")
INDEX_FILE_PATH = os.path.join(PROCESSED_DIR, "acoustic_inverted_index.jsonl")
# Sidecar local audio_id -> {ruta, metadata}. Reemplaza la BD para audio.
METADATA_FILE_PATH = os.path.join(PROCESSED_DIR, "audio_metadata.json")
# Carpeta local con los MP3 (fuente de la búsqueda, sin BD)
RAW_AUDIO_DIR = os.path.join(PROJECT_ROOT, "data", "raw", "fma_small")




def get_audio_batch(conn, batch_size=100, offset=0):
    """Extrae un lote de audios usando la conexión centralizada."""
    # Usamos el cursor estándar (tuplas) para no romper el unpacking de los pipelines
    cursor = conn.cursor()
    query = "SELECT audio_id, filepath FROM audio_dataset ORDER BY audio_id LIMIT %s OFFSET %s"
    try:
        cursor.execute(query, (batch_size, offset))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error al recuperar datos: {e}")
        return []
    finally:
        cursor.close()



class AcousticFeatureExtractor:
    def __init__(self, sample_rate=22050, window_ms=500, overlap=0.5, n_mfcc=20):
        self.sr = sample_rate
        self.n_mfcc = n_mfcc
        self.n_fft = int((window_ms / 1000.0) * self.sr)
        self.hop_length = int(self.n_fft * (1.0 - overlap))

    def extract_from_path(self, filepath):
        """Lee el audio directamente desde el disco duro."""
        try:
            # librosa.load maneja automáticamente la conversión a mono y el remuestreo
            y, sr = librosa.load(filepath, sr=self.sr, mono=True)

            mfccs = librosa.feature.mfcc(
                y=y, 
                sr=self.sr, 
                n_mfcc=self.n_mfcc, 
                n_fft=self.n_fft, 
                hop_length=self.hop_length
            )
            return mfccs.T 
        except Exception as e:
            print(f"Error procesando archivo {filepath}: {e}")
            return None

class AcousticCodebookBuilder:
    def __init__(self, n_clusters=1000):
        self.n_clusters = n_clusters
        self.kmeans = MiniBatchKMeans(n_clusters=self.n_clusters, random_state=42, batch_size=1024)

    def partial_fit(self, mfcc_features):
        if mfcc_features is not None and len(mfcc_features) > 0:
            self.kmeans.partial_fit(mfcc_features)

    def export_codebook(self, output_path=CODEBOOK_FILE_PATH):
        centroids = self.kmeans.cluster_centers_
        np.save(output_path, centroids)
        print(f"Codebook exportado exitosamente a {output_path} con forma {centroids.shape}")
        return centroids