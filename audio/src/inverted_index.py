import json

class InvertedIndex:
   
    def __init__(self):
        self.index = {}

    def add_document(self, audio_id, histogram):
        for word_id, frequency in histogram.items(): 
            word_id_str = str(word_id) 
            
            if word_id_str not in self.index:
                self.index[word_id_str] = []
                 
            self.index[word_id_str].append((audio_id, frequency))

    def save_to_disk(self, output_path="acoustic_inverted_index.json"):
        try:
            with open(output_path, 'w') as f:
                json.dump(self.index, f, indent=2)
            print(f"Índice invertido guardado exitosamente en {output_path}")
            print(f"Total de palabras indexadas: {len(self.index)}")
        except Exception as e:
            print(f"Error al guardar el índice: {e}")
