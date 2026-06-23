import cv2
import numpy as np
import faiss

class VisualQuantizer:
    def __init__(self, codebook_npy_path, k_clusters=1000):
        print("Inicializando motor de cuantización visual con FAISS...")
        
        self.centroids = np.load(codebook_npy_path).astype(np.float32)
        self.k = k_clusters
        
        self.index = faiss.IndexFlatL2(128) 
        self.index.add(self.centroids)
        
        self.sift = cv2.SIFT_create()
        print("Motor de inferencia listo.")

    def image_to_histogram(self, image_path):
        """
        Toma la ruta de una imagen y devuelve un vector (lista) de frecuencias.
        """
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return np.zeros(self.k).tolist()

        keypoints, descriptors = self.sift.detectAndCompute(img, None)
        if descriptors is None:
            return np.zeros(self.k).tolist()

        descriptors = descriptors.astype(np.float32)
        _, indices = self.index.search(descriptors, 1)
        
        visual_words = indices.flatten()

        histogram, _ = np.histogram(visual_words, bins=np.arange(self.k + 1), density=False)

        return histogram.tolist()

if __name__ == "__main__":
    quantizer = VisualQuantizer("codebook_kmeans.npy", k_clusters=1000)
    
    imagen_prueba = "test_image.jpg" 
    
    try:
        vector = quantizer.image_to_histogram(imagen_prueba)
        print("\n¡Imagen cuantizada exitosamente!")
        print(f"Longitud del vector: {len(vector)}")
        print(f"Muestra (primeros 15 valores): {vector[:15]}")
    except Exception as e:
        print(f"Error al probar: {e}")
        
        



