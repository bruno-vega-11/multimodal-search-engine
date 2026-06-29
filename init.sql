
-- TEXTO
-- ------------------------------------------------------------
-- codebook: top-k palabras del vocabulario (Fase 2 / Modulo Codebook)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS codebook (
    term        TEXT PRIMARY KEY,
    rank        INTEGER NOT NULL   -- posicion en el top-k (0 = mas frecuente)
);

-- ------------------------------------------------------------
-- term_index: idf + posting list de cada termino, fusionados.
--
-- Reemplaza las tablas separadas "idf" y "postings" (fila por
-- chunk_id) por una sola fila por termino, con la posting list
-- completa empacada como JSONB:
--
--   [[chunk_id, tf], [chunk_id, tf], ...]
--
-- Justificacion: el patron de uso de este proyecto es carga
-- unica (se construye una sola vez al procesar el dataset) y
-- solo lecturas despues (search.py nunca actualiza un posting
-- individual). Con ese patron, JSONB es preferible a una fila
-- por (term, chunk_id):
--   - 5,000 filas en vez de ~4.4 millones
--   - una sola lectura por termino trae idf + posting list
--     completa (antes eran 2 queries a 2 tablas distintas)
--   - mucho menor tamaño en disco (sin overhead de fila repetido
--     4.4 millones de veces)
-- El costo tipico de JSONB (reescribir el array completo en
-- cada UPDATE) no aplica aqui porque nunca se actualiza un
-- posting suelto despues de la carga inicial.
--
-- Esto es independiente del experimento de Fase 3, donde se
-- compara tu indice invertido propio (SPIMI, archivo
-- final_index.idx, que ya tiene exactamente este mismo formato
-- por linea) contra un indice GIN nativo de Postgres sobre la
-- tabla "metadata".
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS term_index (
    term        TEXT PRIMARY KEY REFERENCES codebook(term),
    idf_value   DOUBLE PRECISION NOT NULL,
    postings    JSONB NOT NULL
);

-- ------------------------------------------------------------
-- metadata: un row por chunk (parrafo de cancion)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS metadata (
    chunk_id     INTEGER PRIMARY KEY,
    document_id  INTEGER NOT NULL,
    title        TEXT NOT NULL,
    artist       TEXT NOT NULL,
    text         TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_metadata_document_id
    ON metadata (document_id);

-- ------------------------------------------------------------
-- doc_norms: norma euclidiana del vector tf-idf de cada chunk
-- (necesaria para normalizar el coseno en la busqueda)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS doc_norms (
    chunk_id    INTEGER PRIMARY KEY REFERENCES metadata(chunk_id),
    norm_value  DOUBLE PRECISION NOT NULL
);

-- IMAGEN
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS fashion_images (
    id SERIAL PRIMARY KEY,
    nombre_archivo VARCHAR(255) NOT NULL,
    ruta_original TEXT NOT NULL,
    histograma_visual vector(1000) 
);