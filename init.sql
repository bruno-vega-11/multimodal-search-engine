
-- TEXTO
CREATE TABLE IF NOT EXISTS codebook (
    term        TEXT PRIMARY KEY,
    rank        INTEGER NOT NULL   -- posicion en el top-k (0 = mas frecuente)
);

CREATE TABLE IF NOT EXISTS term_index (
    term        TEXT PRIMARY KEY REFERENCES codebook(term),
    idf_value   DOUBLE PRECISION NOT NULL,
    postings    JSONB NOT NULL
);

-- metadata: parrafo de cancion
CREATE TABLE IF NOT EXISTS metadata (
    chunk_id     INTEGER PRIMARY KEY,
    document_id  INTEGER NOT NULL,
    title        TEXT NOT NULL,
    artist       TEXT NOT NULL,
    text         TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_metadata_document_id
    ON metadata (document_id);

-- doc_norms: norma euclidiana del vector tf-idf de cada chunk
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

-- AUDIO
CREATE TABLE audio_dataset (
    audio_id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL UNIQUE,
    track_number INT,
    title VARCHAR(255),
    collaborators TEXT,
    album VARCHAR(255),
    audio_data BYTEA NOT NULL,
    content_type VARCHAR(50) DEFAULT 'audio/mpeg',
    file_size BIGINT,
    duration_seconds DOUBLE PRECISION,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
