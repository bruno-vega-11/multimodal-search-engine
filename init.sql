CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE images_dataset (
    image_id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL UNIQUE,
    image_data BYTEA NOT NULL,
    content_type VARCHAR(50) DEFAULT 'image/jpeg',
    file_size BIGINT,
	width INT,
    height INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


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

DROP TABLE text_dataset


CREATE TABLE text_dataset (
    text_id SERIAL PRIMARY KEY,
    track_id VARCHAR(100) UNIQUE,
    track_name TEXT,
    track_artist TEXT,
    lyrics TEXT,
    track_popularity INT,
    track_album_id VARCHAR(100),
    track_album_name TEXT,
    track_album_release_date DATE,
    playlist_name TEXT,
    playlist_id VARCHAR(100),
    playlist_genre VARCHAR(100),
    playlist_subgenre VARCHAR(100),
    danceability DOUBLE PRECISION,
    energy DOUBLE PRECISION,
    key_ INT,
    loudness DOUBLE PRECISION,
    mode_ INT,
    speechiness DOUBLE PRECISION,
    acousticness DOUBLE PRECISION,
    instrumentalness DOUBLE PRECISION,
    liveness DOUBLE PRECISION,
    valence DOUBLE PRECISION,
    tempo DOUBLE PRECISION,
    duration_ms INT,
    language_ VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
