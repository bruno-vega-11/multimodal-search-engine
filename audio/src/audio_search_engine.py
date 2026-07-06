import json
import math
import os
from collections import defaultdict
from audio_utils import AcousticFeatureExtractor, CODEBOOK_FILE_PATH, LEXICON_FILE_PATH, INDEX_FILE_PATH, METADATA_FILE_PATH
from audio_quantizer import AudioQuantizer

class AudioSearchEngine:
    def __init__(self, lexicon_path=LEXICON_FILE_PATH, postings_path=INDEX_FILE_PATH, codebook_path=CODEBOOK_FILE_PATH, metadata_path=METADATA_FILE_PATH):
        print("Inicializando Motor de Búsqueda 100% Local (Lexicon + Offset + TF-IDF)...")
        
        # 1. Cargar Lexicon en RAM
        try:
            with open(lexicon_path, 'r') as f:
                self.lexicon = json.load(f)
            print(f"Lexicon cargado: {len(self.lexicon)} palabras acústicas.")
        except Exception as e:
            print(f"Error al cargar el Lexicon: {e}")
            raise

        # 2. Cargar Metadata en RAM
        self.metadata = {}
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
            print(f"Metadata cargada: {len(self.metadata)} pistas en memoria.")

        # 3. Mantener abierto el archivo de Postings
        self.postings_file = open(postings_path, 'rb')

        # 4. Inicializar los módulos
        self.extractor = AcousticFeatureExtractor(window_ms=500)
        self.quantizer = AudioQuantizer(codebook_path=codebook_path)

        # 5. Precomputar TF-IDF (Safe Memory Streaming - SIN RAM BOMB)
        print("Precomputando magnitudes vectoriales TF-IDF de la base de datos...")
        self.doc_magnitudes = defaultdict(float)
        self.idf = {}
        
        # N calculado dinámicamente desde la metadata
        N = len(self.metadata) if self.metadata else 8000 
        
        # Barrido eficiente en disco (carga una línea, calcula, la destruye)
        for word_id_str in self.lexicon.keys():
            posting_list = self._get_posting_list(word_id_str)
            df = len(posting_list)
                
            self.idf[word_id_str] = math.log((N + 1) / (df + 1)) + 1.0
            idf_weight = self.idf[word_id_str]

            for doc_id, tf in posting_list:
                tfidf_score = tf * idf_weight
                self.doc_magnitudes[doc_id] += (tfidf_score ** 2)

        for doc_id in self.doc_magnitudes:
            self.doc_magnitudes[doc_id] = math.sqrt(self.doc_magnitudes[doc_id])

        print("Motor de Búsqueda listo.")

    def _get_posting_list(self, word_id_str):
        if word_id_str not in self.lexicon:
            return []
        offset = self.lexicon[word_id_str]
        self.postings_file.seek(offset)
        line_bytes = self.postings_file.readline()
        return json.loads(line_bytes.decode('utf-8'))

    def search(self, query_filepath, top_k=5):
        mfcc_vectors = self.extractor.extract_from_path(query_filepath)
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
            if word_id_str in self.lexicon:
                idf_weight = self.idf[word_id_str]
                posting_list = self._get_posting_list(word_id_str)
                
                for doc_id, doc_tf in posting_list:
                    d_tfidf = doc_tf * idf_weight
                    dot_products[doc_id] += (q_tfidf * d_tfidf)

        cosine_scores = {}
        for doc_id, dot_product in dot_products.items():
            doc_magnitude = self.doc_magnitudes.get(doc_id, 1.0)
            similarity = dot_product / (query_magnitude * doc_magnitude)
            cosine_scores[doc_id] = similarity
            
        sorted_results = sorted(cosine_scores.items(), key=lambda x: x[1], reverse=True)

        return [{"audio_id": int(doc_id), "similarity_score": float(score)} 
                for doc_id, score in sorted_results[:top_k]]

    def __del__(self):
        if hasattr(self, 'postings_file') and not self.postings_file.closed:
            self.postings_file.close()