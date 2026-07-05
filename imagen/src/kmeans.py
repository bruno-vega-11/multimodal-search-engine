import numpy as np
import faiss
import glob
import os
from tqdm import tqdm

def train_kmeans_gpu(chunks_folder, output_file, k_clusters=1000, sample_ratio=0.2):
    chunk_files = sorted(glob.glob(os.path.join(chunks_folder, "Archivitos", "sift_descriptors_parte*.npy")))
    
    if not chunk_files:
        print("No se encontraron archivos .npy")
        return

    print("Seleccionando submuestra para entrenamiento...")
    sampled_data = []
    
    for f in tqdm(chunk_files, unit="chunk"):
        # Usamos mmap_mode='r' para no cargar el archivo completo
        d = np.load(f, mmap_mode='r')
        
        # Seleccionamos solo una parte aleatoria de cada chunk
        n_rows = d.shape[0]
        indices = np.random.choice(n_rows, int(n_rows * sample_ratio), replace=False)
        sampled_data.append(d[indices].astype(np.float32))
    
    # Esto es mucho más pequeño que cargar todo
    data = np.vstack(sampled_data)
    del sampled_data
    
    print(f"Entrenando con {data.shape[0]} descriptores de {data.shape[1]} dimensiones.")

    # Entrenamiento
    d = data.shape[1]
    kmeans = faiss.Kmeans(d, k_clusters, niter=20, verbose=True, gpu=True)
    kmeans.train(data)

    np.save(output_file, kmeans.centroids)
    print(f"Guardado en '{output_file}'")