import numpy as np
import faiss
import glob
import os
from tqdm import tqdm

def train_kmeans_gpu(chunks_folder, output_file, k_clusters=1000):
    chunk_files = sorted(glob.glob(os.path.join(chunks_folder, "Archivitos/sift_descriptors_parte*.npy")))
    
    if not chunk_files:
        print("No se encontraron archivos .npy")
        return

    print(f"Encontrados {len(chunk_files)} chunks.")

    print("Cargando descriptores...")
    all_data = []
    for f in tqdm(chunk_files, unit="chunk"):
        d = np.load(f).astype(np.float32)
        all_data.append(d)
    
    data = np.vstack(all_data)
    del all_data
    print(f"Total descriptores: {data.shape}")

    print("Entrenando KMeans en GPU...")
    d = data.shape[1]  # 128
    kmeans = faiss.Kmeans(d, k_clusters, niter=20, verbose=True, gpu=True)
    kmeans.train(data)

    output_npy = output_file.replace('.pkl', '.npy')
    np.save(output_npy, kmeans.centroids)
    print(f"Guardado en '{output_npy}'  shape={kmeans.centroids.shape}")

if __name__ == "__main__":
    train_kmeans_gpu(".", "codebook_kmeans.pkl", k_clusters=1000)