import numpy as np
from scipy.spatial.distance import cdist
from collections import Counter

class AudioQuantizer:
    def __init__(self, codebook_path="acoustic_codebook.npy"):
        try:
            self.codebook = np.load(codebook_path)
            self.num_words = self.codebook.shape[0]
            print(f"Cuantizador inicializado con {self.num_words} palabras acústicas.")
        except Exception as e:
            print(f"Error crítico al cargar el Codebook: {e}")
            raise

    def quantize_to_histogram(self, mfcc_features):
         
        if mfcc_features is None or len(mfcc_features) == 0:
            return {}
        distances = cdist(mfcc_features, self.codebook, metric='euclidean')
        nearest_words = np.argmin(distances, axis=1)
    
        histogram = dict(Counter(nearest_words))
        
        return histogram