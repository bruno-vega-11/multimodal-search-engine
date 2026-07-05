"""Construye el índice de audio 100% local a partir de los MP3 en disco.

A diferencia de indexer_pipeline.py (que leía audio_id/filepath desde Postgres),
este script recorre audio/data/raw/fma_small, asigna un audio_id local y
determinista, reutiliza el codebook acústico existente y genera:

  - lexicon.json                  (punteros a las postings)
  - acoustic_inverted_index.jsonl (índice invertido con offsets)
  - audio_metadata.json           (audio_id -> ruta + tags ID3)

Con esto la búsqueda, la metadata y el streaming quedan totalmente locales,
sin depender de la base de datos.

Ejecutar desde la raíz del repo:  python -m audio.src.build_audio_index_local
"""
import os
import sys
import glob
import json

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SRC_DIR))  # raíz del repo
# Ambos estilos de import conviven en este subproyecto; garantizamos las dos rutas.
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, SRC_DIR)

from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from tqdm import tqdm

from audio_utils import (
    AcousticFeatureExtractor,
    LEXICON_FILE_PATH,
    INDEX_FILE_PATH,
    METADATA_FILE_PATH,
    RAW_AUDIO_DIR,
)
from audio_quantizer import AudioQuantizer
from inverted_index import InvertedIndex


def leer_metadata_mp3(audio_path, audio_id):
    """Extrae metadata desde los tags ID3 del propio archivo (sin BD)."""
    filename = os.path.basename(audio_path)
    title = collaborators = album = None
    duration_seconds = 0.0

    try:
        info = MP3(audio_path)
        duration_seconds = float(info.info.length)
    except Exception:
        pass

    try:
        tags = EasyID3(audio_path)
        title = tags.get("title", [None])[0]
        collaborators = tags.get("artist", [None])[0]
        album = tags.get("album", [None])[0]
    except Exception:
        pass

    return {
        "audio_id": audio_id,
        "filename": filename,
        "filepath": os.path.abspath(audio_path),
        "title": title if title else "Desconocido",
        "artist": collaborators if collaborators else "Desconocido",
        "album": album if album else "Desconocido",
        "duration_seconds": duration_seconds,
    }


def build_local_index():
    if not os.path.isdir(RAW_AUDIO_DIR):
        print(f"[ERROR] No existe la carpeta de audios: {RAW_AUDIO_DIR}")
        return

    # Orden determinista: mismo audio_id en cada corrida.
    audio_files = sorted(glob.glob(os.path.join(RAW_AUDIO_DIR, "**", "*.mp3"), recursive=True))
    print(f"Audios encontrados: {len(audio_files)}")
    if not audio_files:
        return

    extractor = AcousticFeatureExtractor(window_ms=500)
    quantizer = AudioQuantizer()
    inverted_index = InvertedIndex()

    metadata = {}
    indexados = 0
    errores = 0

    for audio_id, audio_path in enumerate(tqdm(audio_files, desc="Indexando", unit="audio"), start=1):
        try:
            mfcc_vectors = extractor.extract_from_path(audio_path)
            if mfcc_vectors is None:
                errores += 1
                continue

            histogram = quantizer.quantize_to_histogram(mfcc_vectors)
            if not histogram:
                errores += 1
                continue

            # Casteamos a int nativo: numpy int rompe json.dumps en las postings.
            histogram = {int(word): int(freq) for word, freq in histogram.items()}
            inverted_index.add_document(audio_id, histogram)

            metadata[str(audio_id)] = leer_metadata_mp3(audio_path, audio_id)
            indexados += 1
        except Exception as e:
            errores += 1
            print(f"Error con {audio_path}: {e}")

    inverted_index.save_with_offsets(LEXICON_FILE_PATH, INDEX_FILE_PATH)

    with open(METADATA_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False)

    print("\n=== RESUMEN ===")
    print(f"Audios indexados: {indexados}")
    print(f"Errores/omitidos: {errores}")
    print(f"Metadata local:   {METADATA_FILE_PATH}")


if __name__ == "__main__":
    build_local_index()
