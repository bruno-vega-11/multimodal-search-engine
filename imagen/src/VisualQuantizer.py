import cv2
import numpy as np
import faiss
from metrics import MetricsTracker 

class VisualQuantizer:
    def __init__(self, codebook_npy_path, k_clusters=1000):
        self.centroids = np.load(codebook_npy_path, mmap_mode='r').astype(np.float32)
        self.k = k_clusters
        self.index = faiss.IndexFlatL2(128) 
        self.index.add(self.centroids)
        self.sift = cv2.SIFT_create()

    def image_to_histogram(self, image_path):
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return np.zeros(self.k).tolist()

        keypoints, descriptors = self.sift.detectAndCompute(img, None)
        del img
        
        if descriptors is None:
            return np.zeros(self.k).tolist()

        descriptors = descriptors.astype(np.float32)
        _, indices = self.index.search(descriptors, 1)
        
        visual_words = indices.flatten()
        histogram, _ = np.histogram(visual_words, bins=np.arange(self.k + 1), density=False)

        return histogram.tolist()

if __name__ == "__main__":
    quantizer = VisualQuantizer("./codebook_kmeans.npy", k_clusters=1000)
    imagen_prueba = "test_image.jpg" 
    
    # Uso de MetricsTracker igual que en el motor de búsqueda de texto
    with MetricsTracker() as m:
        try:
            vector = quantizer.image_to_histogram(imagen_prueba)
            print("\n¡Imagen cuantizada exitosamente!")
        except Exception as e:
            print(f"Error al probar: {e}")
            
    print("Metricas de procesamiento:", m.result)