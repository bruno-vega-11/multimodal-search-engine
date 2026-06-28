CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS fashion_images (
    id SERIAL PRIMARY KEY,
    nombre_archivo VARCHAR(255) NOT NULL,
    ruta_original TEXT NOT NULL,
    histograma_visual vector(1000) 
);