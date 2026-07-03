import csv
import json
import math
from collections import Counter
from preprocess import preprocess_text
from chunker import split_song_into_chunks

def build_collection(csv_file, processed_file, codebook_file, idf_file, idf_chunks_file, metadata_file, documents_file, top_k=10000):
    term_counter = Counter()
    df_counter = Counter()
    df_counter_chunk = Counter()
    total_docs = 0
    chunk_id = 0

    with open(csv_file, "r", encoding="utf-8") as csvfile, open(processed_file, "w", encoding="utf-8") as processed_out, open(metadata_file, "w", encoding="utf-8") as metadata_out, open(documents_file, "w", encoding="utf-8") as documents_out:
        reader = csv.DictReader(csvfile)

        for document_id, row in enumerate(reader):
            title = row["song"]

            artist = row["artist"]

            lyrics = str(row["text"])

            chunks = split_song_into_chunks(lyrics)

            doc_terms = set()

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

                doc_terms.update(tokens)

                for term in set(tokens):
                    df_counter_chunk[term] += 1

                chunk_id += 1

                if chunk_id % 10000 == 0:
                    print(f"Chunks procesados: {chunk_id}")

            documents_out.write(json.dumps({
                "document_id": document_id,
                "title": title,
                "artist": artist,
            }) + "\n")

            for term in doc_terms:
                df_counter[term] += 1

            total_docs += 1

    print(f"\nTotal canciones: {total_docs}")
    print(f"Total chunks: {chunk_id}")
    print(f"Vocabulario total: {len(term_counter)}")

    idf_all = {
        term: math.log10(total_docs / df_counter[term])
        for term in term_counter
    }

    vocab_score = {
        term: term_counter[term] * idf_all[term]
        for term in term_counter
    }

    top_terms = sorted(vocab_score.items(), key=lambda kv: kv[1], reverse=True)[:top_k]

    codebook = {}

    for idx, (term, _) in enumerate(top_terms):
        codebook[term] = idx

    idf = {term: idf_all[term] for term in codebook}

    total_chunks = chunk_id

    idf_chunks = {
        term: math.log10(total_chunks / df_counter_chunk[term])
        for term in codebook
    }

    with open(codebook_file, "w", encoding="utf-8") as f:
        json.dump(codebook, f, indent=4)

    with open(idf_file, "w", encoding="utf-8") as f:
        json.dump(idf,f,indent=4)

    with open(idf_chunks_file, "w", encoding="utf-8") as f:
        json.dump(idf_chunks, f, indent=4)

    print(f"Top-K guardado: {len(codebook)} términos")

    return (codebook, df_counter, idf, total_docs)