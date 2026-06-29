import os
import io
import librosa
import numpy as np
import psycopg2
import soundfile as sf
from sklearn.cluster import MiniBatchKMeans
from psycopg2 import sql
from dotenv import load_dotenv
import gc

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SRC_DIR)

CODEBOOK_DIR = os.path.join(PROJECT_ROOT, "data", "codebook")
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")

CODEBOOK_FILE_PATH = os.path.join(CODEBOOK_DIR, "acoustic_codebook.npy")
INDEX_FILE_PATH = os.path.join(PROCESSED_DIR, "acoustic_inverted_index.json")
 
load_dotenv()

class AudioDatabaseManager:
    """Maneja la conexión a PostgreSQL y la recuperación de datos binarios (BYTEA)."""
    
    def __init__(self):
        self.host = os.getenv("DB_HOST", "localhost")
        self.database = os.getenv("DB_NAME", "sistema_multimodal")
        self.user = os.getenv("DB_USER", "postgres")
        self.password = os.getenv("DB_PASSWORD", "123456")
        self.port = os.getenv("DB_PORT", "5433")
        self.conn = None

    def connect(self):
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port
            )
            print("Conexión a PostgreSQL establecida.")
        except psycopg2.Error as e:
            print(f"Error al conectar a la base de datos: {e}")
            raise

    def get_audio_batch(self, batch_size=100, offset=0):
        """Recupera un lote de archivos de audio (BYTEA) adaptado al esquema actual."""
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        query = sql.SQL("SELECT audio_id, audio_data FROM audio_dataset ORDER BY audio_id LIMIT %s OFFSET %s")
        
        try:
            cursor.execute(query, (batch_size, offset))
            records = cursor.fetchall()
            return records
        except Exception as e:
            print(f"Error al recuperar datos: {e}")
            return []
        finally:
            cursor.close()

    def close(self):
        if self.conn:
            self.conn.close()
            print("Conexión a PostgreSQL cerrada.")


class AcousticFeatureExtractor:
    "ventanas deslizantes y extracción MFCC."
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
            print(f"Error procesando bytea de audio: {e}")
            return None


class AcousticCodebookBuilder:
    def __init__(self, n_clusters=500):
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

