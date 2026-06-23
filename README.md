# multimodal-search-engine

Sistema unificado de recuperación y búsqueda que soporta modalidades de texto - imagen - audio

Este repositorio contiene los scripts necesarios para levantar una base de datos PostgreSQL con pgvector e importar los datasets correspondientes a los módulos de imagen, audio y texto del sistema multimodal.

El sistema trabaja con tres tipos de datos:

- Imágenes de productos de moda `.jpg`
- Audios musicales en formato `.mp3`
- Letras de canciones y metadata musical en formato `.csv`

---

## Flujo para levantar el proyecto

### 1. Levantar PostgreSQL con Docker Compose

Primero se debe levantar el contenedor de PostgreSQL usando Docker Compose.
Desde la carpeta raíz del proyecto, ejecutar:

```bash
docker compose up -d
```

Esto levantará un contenedor PostgreSQL con soporte para pgvector.

---

### 2. Credenciales de la base de datos

Los scripts de Python se conectan a PostgreSQL con las siguientes credenciales:

- Base de datos: `sistema_multimodal`
- Usuario: `postgres`
- Contraseña: `123456`
- Host: `localhost`
- Puerto: `5433`

La conexión usada en los scripts es:

```python
psycopg2.connect(
    dbname="sistema_multimodal",
    user="postgres",
    password="123456",
    host="localhost",
    port="5433"
)
```

---

### 3. Crear las tablas de la base de datos

Luego de levantar el contenedor, se deben crear las tablas ejecutando el archivo `init.sql`.
Ejecutar manualmente el contenido de `init.sql` desde pgAdmin. Esto incluye la activación de la librería pgvector.

---

### 4. Instalar dependencias de Python

Antes de ejecutar cualquier script, instalar las dependencias del proyecto:

```bash
pip install -r requirements.txt
```

El archivo `requirements.txt` contiene:

```
kagglehub
psycopg2-binary
pandas
Pillow
mutagen
```

Estas librerías se usan para:

- Descargar datasets desde Kaggle.
- Conectarse a PostgreSQL.
- Leer archivos CSV.
- Procesar imágenes.
- Leer metadata de audios `.mp3`.

---

### 5. Descargar Datasets

#### Sistema de texto

El encargado del sistema de texto debe usar los siguientes archivos:

- `download_text_dataset.py`
- `insert_text_dataset.py`

Ejecutar:

```bash
python download_texto_dataset.py
```

Este script descarga el dataset de Kaggle:

```
notshrirang/spotify-million-song-dataset
```

En una ruta relativa.

Luego de descargar el dataset correspondiente a texto, ejecutar:

```bash
python insert_text_dataset.py
```

Este script lee la información del dataset e inserta en la tabla `text_dataset`.

La tabla guarda:

- ID de canción.
- Nombre de canción.
- Artista.
- Letra completa.
- Popularidad.
- Álbum.
- Fecha de lanzamiento.
- Playlist.
- Género.
- Subgénero.
- Features musicales.
- Idioma de la letra.
- Fecha de creación.

---

#### Sistema de imágenes

El encargado del sistema de imágenes debe usar los siguientes archivos:

- `download_images_dataset.py`
- `insert_image_dataset.py`

Ejecutar:

```bash
python download_images_dataset.py
```

Este script descarga el dataset de Kaggle:

```
paramaggarwal/fashion-product-images-dataset
```

En una ruta relativa.

Luego de descargar las imágenes, ejecutar:

```bash
python insert_image_dataset.py
```

Este script lee las imágenes `.jpg` desde la ruta:

```
E:\Dataset-Visual-E-commerce
```

e inserta la información en la tabla `images_dataset`.

La tabla guarda:

- Nombre del archivo.
- Imagen real en formato binario BYTEA.
- Tipo de contenido.
- Tamaño del archivo.
- Ancho.
- Alto.
- Fecha de creación.

---

#### Sistema de audio

El encargado del sistema de audio debe usar el archivo `insert_audio_dataset.py`.

Antes de ejecutar el script, se debe tener descargado el dataset de audios FMA Small.
La carpeta esperada es (modificar):

```
E:\Dataset-Musical-Inteligente\fma_small
```

Pasos para descargar:

1. Ingresar al repositorio: https://github.com/mdeff/fma
2. Dentro del readme, hacer click en `fma_small.zip`.
3. Una vez terminada la descarga, descomprimirlo en la carpeta `E:\Dataset-Musical-Inteligente\fma_small` (modificable).

Dentro de esa carpeta deben existir subcarpetas como:

```
000, 001, 002, 003 ...
```

Dentro de esas subcarpetas deben estar los archivos `.mp3`, por ejemplo:

```
000002.mp3, 000005.mp3, 000010.mp3 ...
```

Luego, ejecutar:

```bash
python insert_audio_dataset.py
```

Este script recorre todas las subcarpetas dentro de `E:\Dataset-Musical-Inteligente\fma_small` (modificar), busca archivos `.mp3` e inserta cada audio en la tabla `audio_dataset`.

La tabla guarda:

- Nombre del archivo.
- Número de pista.
- Título.
- Colaboradores o artistas.
- Álbum.
- Audio real en formato binario BYTEA.
- Tipo de contenido.
- Tamaño del archivo.
- Duración en segundos.
- Fecha de creación.
