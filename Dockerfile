FROM python:3.11-slim

WORKDIR /app

# Librerias de sistema requeridas por opencv-python (libGL/libglib) y por
# librosa/soundfile para decodificar audio (libsndfile, ffmpeg).
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# torch solo lo usa imagen/src/sift.py (no hay GPU en este contenedor); se
# instala primero contra el indice CPU-only oficial de PyTorch para no traer
# las dependencias de CUDA (nvidia-*), que pesan varios GB y no se usan.
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt

# texto/src/preprocess.py carga stopwords.words("english") al importarse
# (backend.py -> search.py -> preprocess.py), asi que el corpus debe estar
# ya presente en la imagen: el contenedor no tiene por que tener salida a
# internet en tiempo de arranque.
RUN python -m nltk.downloader -d /usr/local/share/nltk_data stopwords
ENV NLTK_DATA=/usr/local/share/nltk_data

COPY . .

EXPOSE 8000

CMD ["uvicorn", "backend:app", "--host", "0.0.0.0", "--port", "8000"]
