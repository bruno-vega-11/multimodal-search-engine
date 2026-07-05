import os
import json
import heapq
from collections import defaultdict

class ExternalMerger:
    def __init__(self, blocks_dir, output_songs_file, output_chunks_file, metadata_file="data/processed/metadata.json"):
        self.blocks_dir = blocks_dir
        self.output_songs_file = output_songs_file
        self.output_chunks_file = output_chunks_file
        self.metadata_file = metadata_file

    def _load_chunk_to_document(self):
        chunk_to_document = {}

        with open(self.metadata_file, "r", encoding="utf-8") as f:
            for line in f:
                record = json.loads(line)
                chunk_to_document[record["chunk_id"]] = record["document_id"]

        return chunk_to_document

    def _postings_by_document(self, postings, chunk_to_document):
        
        tf_by_document = defaultdict(int)

        for chunk_id, tf in postings:
            document_id = chunk_to_document[chunk_id]
            tf_by_document[document_id] += tf

        return sorted(tf_by_document.items(), key=lambda x: x[0])

    def _postings_by_chunk(self, postings):

        tf_by_chunk = defaultdict(int)

        for chunk_id, tf in postings:
            tf_by_chunk[chunk_id] += tf

        return sorted(tf_by_chunk.items(), key=lambda x: x[0])

    def merge(self):
        chunk_to_document = self._load_chunk_to_document()

        block_files = sorted([os.path.join(self.blocks_dir, file) for file in os.listdir(self.blocks_dir) if file.startswith("block_")])

        handles = [open(file, "r", encoding="utf-8") for file in block_files]

        heap = []

        for block_id, f in enumerate(handles):
            line = f.readline()

            if line:
                record = json.loads(line)

                heapq.heappush(heap,(record["term"], block_id, record["postings"]))

        with open(self.output_songs_file, "w", encoding="utf-8") as out_songs, open(self.output_chunks_file, "w", encoding="utf-8") as out_chunks:
            current_term = None
            current_postings = []
            while heap:
                term, block_id, postings = (heapq.heappop(heap))

                if current_term == term:
                    current_postings.extend(postings)
                else:
                    if current_term is not None:
                        document_postings = self._postings_by_document(current_postings, chunk_to_document)
                        out_songs.write(json.dumps({"term":current_term, "postings":document_postings})+ "\n")

                        chunk_postings = self._postings_by_chunk(current_postings)
                        out_chunks.write(json.dumps({"term":current_term, "postings":chunk_postings}) + "\n")

                    current_term = term
                    current_postings = postings

                next_line = handles[block_id].readline()

                if next_line:
                    record = json.loads(next_line)

                    heapq.heappush(heap, (record["term"], block_id, record["postings"]))

            if current_term is not None:
                document_postings = self._postings_by_document(current_postings, chunk_to_document)

                out_songs.write(json.dumps({"term":current_term, "postings":document_postings}) + "\n")

                chunk_postings = self._postings_by_chunk(current_postings)
                out_chunks.write(json.dumps({"term":current_term, "postings":chunk_postings}) + "\n")

        for f in handles:
            f.close()

        print()

        print("MERGE COMPLETADO")

        print(f"Bloques fusionados: "f"{len(block_files)}")

        print(f"Indice final (canciones): " f"{self.output_songs_file}")

        print(f"Indice final (chunks): " f"{self.output_chunks_file}")