# Sistema Multimodal de Recuperación por Contenido

Proyecto de recuperación multimodal que permite buscar información usando tres tipos de entrada: texto, audio e imagen. El sistema está diseñado para comparar contenido real, no solo metadatos, por lo que cada modalidad transforma los datos en representaciones vectoriales especializadas.

## Modalidades

### Texto

Permite buscar canciones a partir de fragmentos o consultas textuales.
Las letras se procesan, se dividen en chunks y se indexan usando TF-IDF e índice invertido. El sistema retorna coincidencias por canción completa y por fragmento relevante.

### Audio

Permite buscar canciones con similitud acústica.
Cada audio se transforma en vectores MFCC, luego se cuantiza usando un codebook acústico y se representa como histograma de palabras acústicas. La búsqueda se realiza con TF-IDF y similitud coseno.

### Imagen

Permite buscar productos visualmente similares.
Las imágenes se procesan con descriptores SIFT, se cuantizan contra un codebook visual y se representan como histogramas de palabras visuales. El sistema retorna productos similares a partir de una imagen de consulta.

## Arquitectura

El sistema cuenta con un backend unificado en FastAPI que centraliza las consultas de las tres modalidades. Cada motor especializado se inicializa al levantar el servidor y expone endpoints independientes para texto, audio e imagen.

Endpoints principales:

```text
POST /search/text
POST /search/audio
POST /search/image
```

## Datasets

* Texto: Spotify Million Song Dataset.
* Audio: FMA Small.
* Imagen: Fashion Product Images Dataset.

Cada dataset se procesa previamente para construir sus índices y representaciones internas.

## Tecnologías utilizadas

* Python
* FastAPI
* PostgreSQL
* OpenCV / SIFT
* FAISS
* Librosa
* TF-IDF
* Índices invertidos
* K-Means / Codebooks

## Objetivo

El objetivo del proyecto es demostrar cómo una base de datos multimodal puede integrar texto, audio e imagen para resolver tareas de recuperación por contenido, como buscar canciones por letra, encontrar música acústicamente similar o recuperar productos visualmente parecidos.

