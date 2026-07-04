import csv
import json
import math
from collections import Counter
from preprocess import preprocess_text
from chunker import split_song_into_chunks

def build_collection(csv_file, processed_file, codebook_file, idf_file, metadata_file, top_k=5000):
    term_counter = Counter()
    df_counter = Counter()
    total_chunks = 0
    chunk_id = 0

    with open(csv_file, "r", encoding="utf-8") as csvfile, open(processed_file, "w", encoding="utf-8") as processed_out, open(metadata_file, "w", encoding="utf-8") as metadata_out:
        reader = csv.DictReader(csvfile)

        for document_id, row in enumerate(reader):
            title = row["song"]

            artist = row["artist"]

            lyrics = str(row["text"])

            chunks = split_song_into_chunks(lyrics)

            for chunk in chunks:
                tokens = preprocess_text(chunk)

                if len(tokens)==0:
                    continue

                processed_record = {
                    "chunk_id":chunk_id,
                    "document_id":document_id,
                    "tokens":tokens
                    }

                processed_out.write(json.dumps(processed_record) + "\n")

                metadata_record = {
                    "chunk_id":chunk_id,
                    "document_id":document_id,
                    "title":title,
                    "artist":artist,
                    "text":chunk
                    }

                metadata_out.write(json.dumps(metadata_record) + "\n")
                term_counter.update(tokens)
                unique_terms = set(tokens)
                for term in unique_terms:
                    df_counter[term] += 1
                total_chunks += 1
                chunk_id += 1
                if chunk_id % 10000 == 0:
                    print(f"Chunks procesados: {chunk_id}")

    print(f"\nTotal chunks: {total_chunks}")
    print(f"Vocabulario total: {len(term_counter)}")
    top_terms = (term_counter.most_common(top_k))

    codebook = {}

    for idx, (term, _) in enumerate(top_terms):
        codebook[term] = idx

    idf = {}

    for term in codebook:
        df_value = df_counter[term]

        idf[term] = (math.log((total_chunks + 1)/(df_value + 1)) + 1)

    with open(codebook_file, "w", encoding="utf-8") as f:
        json.dump(codebook, f, indent=4)

    with open(idf_file, "w", encoding="utf-8") as f:
        json.dump(idf,f,indent=4)

    print(f"Top-K guardado: {len(codebook)} términos")

    return (codebook, df_counter, idf, total_chunks)
