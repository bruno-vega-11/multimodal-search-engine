import json
from audio_utils import LEXICON_FILE_PATH, INDEX_FILE_PATH

class InvertedIndex:
    def __init__(self):
        self.index = {}

    def add_document(self, audio_id, histogram):
        for word_id, frequency in histogram.items(): 
            word_id_str = str(word_id) 
            if word_id_str not in self.index:
                self.index[word_id_str] = []
            self.index[word_id_str].append((audio_id, frequency))

    def save_with_offsets(self, lexicon_path=LEXICON_FILE_PATH, output_path=INDEX_FILE_PATH):
        """Guarda el índice separando los punteros (RAM) de los datos masivos (Disco)."""
        lexicon = {}
        
        try:
            with open(output_path, 'wb') as f_postings:
                for word_id, posting_list in self.index.items():
                    current_offset = f_postings.tell()
                    lexicon[word_id] = current_offset
                    
                    line_data = json.dumps(posting_list) + '\n'
                    f_postings.write(line_data.encode('utf-8'))
                    
            with open(lexicon_path, 'w') as f_lexicon:
                json.dump(lexicon, f_lexicon, indent=2)
                
            print("Índice masivo guardado exitosamente con arquitectura de Offsets.")
            print(f"Lexicon (RAM): {lexicon_path}")
            print(f"Inverted Index (Disco): {output_path}")
            
        except Exception as e:
            print(f"Error al guardar con offsets: {e}")