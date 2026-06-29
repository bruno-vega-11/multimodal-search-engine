import json
import math
from collections import defaultdict
from audio_utils import AcousticFeatureExtractor
from audio_quantizer import AudioQuantizer
from audio_utils import CODEBOOK_FILE_PATH, INDEX_FILE_PATH

class AudioSearchEngine:
    def __init__(self, index_path=INDEX_FILE_PATH, codebook_path=CODEBOOK_FILE_PATH):
        print("Inicializando Motor de Alta Precisión (TF-IDF + Cosine Similarity)...")
        
        try:
            with open(index_path, 'r') as f:
                self.inverted_index = json.load(f)
            print(f"Índice Invertido cargado con {len(self.inverted_index)} palabras acústicas.")
        except Exception as e:
            print(f"Error al cargar el índice invertido: {e}")
            raise

        unique_docs = set()
        for posting_list in self.inverted_index.values():
            for doc_id, _ in posting_list:
                unique_docs.add(doc_id)
        self.total_docs = len(unique_docs)

        print("Calculando pesos IDF para discriminar ruido de fondo...")
        self.idf = {}
        for word_id, posting_list in self.inverted_index.items():
            df = len(posting_list)
            self.idf[word_id] = math.log((self.total_docs + 1) / (df + 1)) + 1.0

        print("Precomputando magnitudes vectoriales TF-IDF de la base de datos...")
        self.doc_magnitudes = defaultdict(float)
        
        for word_id, posting_list in self.inverted_index.items():
            idf_weight = self.idf[word_id]
            for doc_id, tf in posting_list:
                tfidf_score = tf * idf_weight
                self.doc_magnitudes[doc_id] += (tfidf_score ** 2)
                
        for doc_id in self.doc_magnitudes:
            self.doc_magnitudes[doc_id] = math.sqrt(self.doc_magnitudes[doc_id])

        self.extractor = AcousticFeatureExtractor(window_ms=100)
        self.quantizer = AudioQuantizer(codebook_path=codebook_path)
        print("Motor de Búsqueda listo.")

    def search(self, query_bytea, top_k=5):

        mfcc_vectors = self.extractor.extract_from_bytea(query_bytea)
        if mfcc_vectors is None:
            return []
            
        raw_query_histogram = self.quantizer.quantize_to_histogram(mfcc_vectors)
        if not raw_query_histogram:
            return []

        query_tfidf = {}
        for word_id, tf in raw_query_histogram.items():
            word_id_str = str(word_id)
            if word_id_str in self.idf:
                query_tfidf[word_id_str] = tf * self.idf[word_id_str]

        query_magnitude = math.sqrt(sum(score ** 2 for score in query_tfidf.values()))
        if query_magnitude == 0:
            return []
        dot_products = defaultdict(float)

        for word_id_str, q_tfidf in query_tfidf.items():
            if word_id_str in self.inverted_index:
                idf_weight = self.idf[word_id_str]
                posting_list = self.inverted_index[word_id_str]
                
                for doc_id, doc_tf in posting_list:
                    d_tfidf = doc_tf * idf_weight
                    dot_products[doc_id] += (q_tfidf * d_tfidf)

        cosine_scores = {}
        for doc_id, dot_product in dot_products.items():
            doc_magnitude = self.doc_magnitudes.get(doc_id, 1.0)
            similarity = dot_product / (query_magnitude * doc_magnitude)
            cosine_scores[doc_id] = similarity
        sorted_results = sorted(cosine_scores.items(), key=lambda x: x[1], reverse=True)

        top_results = []
        for doc_id, score in sorted_results[:top_k]:
            top_results.append({
                "audio_id": int(doc_id),
                "similarity_score": float(score)
            })

        return top_results