import os
import time
import json
import pydantic
from typing import List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Response
from contextlib import asynccontextmanager

from texto.src.search import SearchEngine
from metrics import MetricsTracker
from audio.src.audio_search_engine import AudioSearchEngine

from imagen.src.VisualQuantizer import VisualQuantizer
from imagen.src.image_local_search import ImageLocalSearch

from db import get_connection

MOTOR_TEXTO = None
MOTOR_AUDIO = None
MOTOR_IMAGEN = None
INDICE_IMAGEN = None

_SERVER_START = None
_SEARCH_COUNTS = {"texto": 0, "audio": 0, "imagen": 0}


def _record_metrics(response: Response, modality: str, tracker_result: dict):
    """Agrega latencia/memoria/disco de tracker_result + throughput acumulado
    de esa modalidad al header X-Search-Metrics de la respuesta."""
    _SEARCH_COUNTS[modality] += 1
    elapsed = time.perf_counter() - _SERVER_START
    throughput_qps = _SEARCH_COUNTS[modality] / elapsed if elapsed > 0 else 0.0

    metrics = dict(tracker_result)
    metrics["throughput_consultas_seg"] = round(throughput_qps, 3)
    response.headers["X-Search-Metrics"] = json.dumps(metrics)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global MOTOR_TEXTO, MOTOR_AUDIO, MOTOR_IMAGEN, INDICE_IMAGEN, _SERVER_START
    print("[INFO] Iniciando Backend: Inicializando motores en memoria RAM...")
    _SERVER_START = time.perf_counter()

    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

    try:
        MOTOR_TEXTO = SearchEngine()
        print("[OK] Motor de búsqueda de texto conectado correctamente.")
    except Exception as e:
        print(f"[ERROR] No se pudo levantar el motor de texto: {e}")

    try:
        MOTOR_AUDIO = AudioSearchEngine()
        print("[OK] Motor de búsqueda de audio cargado en RAM.")
    except Exception as e:
        print(f"[ERROR] No se pudo levantar el motor de audio: {e}")

    try:
        codebook_path = os.path.join(SCRIPT_DIR, "imagen" , "data","codebook","codebook_kmeans.npy")
        MOTOR_IMAGEN = VisualQuantizer(codebook_path, k_clusters=1000)
        print("[OK] Motor de búsqueda de imágenes (SIFT + FAISS) cargado correctamente.")
    except Exception as e:
        print(f"[ERROR] No se pudo levantar el motor de imagen: {e}")

    try:
        INDICE_IMAGEN = ImageLocalSearch(base_dir=SCRIPT_DIR)
        print(f"[OK] Índice invertido de imágenes listo ({len(INDICE_IMAGEN)} imágenes, postings en disco).")
    except Exception as e:
        print(f"[ERROR] No se pudo levantar el índice local de imágenes: {e}")

    yield  
    
    print("[INFO] Apagando Backend: Liberando recursos...")
    if MOTOR_TEXTO:
        try: MOTOR_TEXTO.close()
        except: pass
    if INDICE_IMAGEN:
        try: INDICE_IMAGEN.close()
        except: pass
    print("[INFO] Servidor apagado limpiamente.")


app = FastAPI(
    title="Motor de Búsqueda Heterogéneo Multimodal - BD2",
    description="Backend unificado para consultas distribuidas de Texto, Audio e Imagen.",
    version="3.0.0",
    lifespan=lifespan
)

class SearchResult(pydantic.BaseModel):
    id: str
    dataset_type: str  # 'letra', 'cancion' o 'prenda'
    score: float       # Métrica de similitud
    metadata: dict     # Campos para pintar en el Frontend


class TextSearchResponse(pydantic.BaseModel):
    by_song: List[SearchResult]   # ranking a nivel cancion completa
    by_chunk: List[SearchResult]  # ranking a nivel fragmento/parrafo


def obtener_metadata_cancion(audio_id: int) -> dict:
    sql = "SELECT filename, title, collaborators, album, duration_seconds FROM audio_dataset WHERE audio_id = %s;"
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (audio_id,))
                row = cursor.fetchone()
                if row:
                    return {
                        "filename": row[0],
                        "title": row[1] if row[1] else "Desconocido",
                        "artist": row[2] if row[2] else "Desconocido",
                        "album": row[3] if row[3] else "Desconocido",
                        "duration_seconds": float(row[4]) if row[4] else 0.0
                    }
    except Exception as e:
        print(f"[ERROR BD] Metadata audio: {e}")
    return


@app.post("/search/text", response_model=TextSearchResponse, tags=["Texto"])
async def search_by_text(response: Response, query_text: str = Form(..., description="Fragmento a buscar"), top_k: int = 5):
    if not MOTOR_TEXTO:
        raise HTTPException(status_code=503, detail="Motor de texto no disponible.")
    try:
        with MetricsTracker() as m:
            raw_results = MOTOR_TEXTO.search(query_text, top_k=top_k)

        por_cancion = [
            SearchResult(
                id=str(r["document_id"]), dataset_type="cancion", score=float(r["score"]),
                metadata={"title": r["title"], "artist": r["artist"]}
            )
            for r in raw_results["by_song"]
        ]

        por_chunk = [
            SearchResult(
                id=str(r["chunk_id"]), dataset_type="letra", score=float(r["score"]),
                metadata={"title": r["title"], "artist": r["artist"], "text": r["text"]}
            )
            for r in raw_results["by_chunk"]
        ]

        _record_metrics(response, "texto", m.result)

        return TextSearchResponse(by_song=por_cancion, by_chunk=por_chunk)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/search/audio", response_model=List[SearchResult], tags=["Audio"])
async def search_by_audio(response: Response, query_audio: UploadFile = File(...), top_k: int = 5):
    if not MOTOR_AUDIO:
        raise HTTPException(status_code=503, detail="Motor de audio no disponible.")
    if not query_audio.filename.endswith(('.mp3', '.wav', '.ogg')):
        raise HTTPException(status_code=400, detail="Formato de audio no soportado.")
    resultados = []
    try:
        audio_bytes = await query_audio.read()

        with MetricsTracker() as m:
            raw_audio_results = MOTOR_AUDIO.search(audio_bytes, top_k=top_k)

        for r in raw_audio_results:
            audio_id = r["audio_id"]
            metadata_bd = obtener_metadata_cancion(audio_id)
            BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
            metadata_bd["audio_url"] = f"{BASE_URL}/audio/stream/{audio_id}"
            resultados.append(SearchResult(
                id=str(audio_id), dataset_type="cancion", score=float(r["similarity_score"]), metadata=metadata_bd
            ))
        resultados.sort(key=lambda x: x.score, reverse=True)

        _record_metrics(response, "audio", m.result)

        return resultados[:top_k]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/audio/stream/{audio_id}", tags=["Audio"])
async def stream_audio(audio_id: int):
    sql = "SELECT audio_data, content_type FROM audio_dataset WHERE audio_id = %s;"
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (audio_id,))
                row = cursor.fetchone()
                if not row: raise HTTPException(status_code=404, detail="Audio no encontrado.")
                return Response(content=row[0], media_type=row[1] if row[1] else "audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/search/image", response_model=List[SearchResult], tags=["Imagen"])
async def search_by_image(response: Response, query_image: UploadFile = File(...), top_k: int = 5):
    if not MOTOR_IMAGEN:
        raise HTTPException(status_code=503, detail="El motor de imagen no está listo.")
    if not INDICE_IMAGEN:
        raise HTTPException(status_code=503, detail="El índice local de imágenes no está listo.")

    if not query_image.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
        raise HTTPException(status_code=400, detail="Formato de imagen no válido.")

    try:
        contenido_subida = await query_image.read()
        nombre_temporal = f"temp_{query_image.filename}"

        with MetricsTracker() as m:
            with open(nombre_temporal, "wb") as f:
                f.write(contenido_subida)
            try:
                histogram_vector = MOTOR_IMAGEN.image_to_histogram(nombre_temporal)
            finally:
                if os.path.exists(nombre_temporal):
                    os.remove(nombre_temporal)

            # Búsqueda 100% local en RAM (sin base de datos): similitud coseno
            # contra los histogramas precalculados del JSONL.
            raw_image_results = INDICE_IMAGEN.search(histogram_vector, top_k=top_k)

            resultados = [
                SearchResult(
                    id=str(r["id"]),
                    dataset_type="prenda",
                    score=r["score"],
                    metadata={"nombre_archivo": r["nombre_archivo"], "ruta_original": r["ruta_original"]}
                )
                for r in raw_image_results
            ]

        _record_metrics(response, "imagen", m.result)

        return resultados

    except Exception as e:
        print(f"[ERROR IMAGEN] Error en endpoint: {e}")
        raise HTTPException(status_code=500, detail="Error interno procesando la imagen.")


@app.get("/imagen/render/{imagen_id}", tags=["Imagen"])
async def render_image(imagen_id: int):
    """
    Resuelve la ruta física de la imagen 100% en local (sin base de datos):
    toma la ruta relativa del índice cargado en RAM (JSONL), la une con la ruta
    base de la máquina, lee el archivo físico del disco y lo transmite al navegador.
    """
    if not INDICE_IMAGEN:
        raise HTTPException(status_code=503, detail="El índice local de imágenes no está listo.")

    try:
        ruta_limpia = INDICE_IMAGEN.resolver_ruta(imagen_id)
        if ruta_limpia is None:
            raise HTTPException(status_code=404, detail="Registro de imagen no encontrado en el índice local.")

        if not os.path.exists(ruta_limpia):
            print(f"[WARN IMAGEN] El registro existe en el índice pero el archivo físico no está en: {ruta_limpia}")
            raise HTTPException(status_code=404, detail="El archivo físico de la imagen no existe en el servidor.")

        with open(ruta_limpia, "rb") as f:
            contenido_imagen = f.read()

        return Response(content=contenido_imagen, media_type="image/jpeg")

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR RENDER] Falla al transmitir imagen_id {imagen_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno al recuperar la imagen física.")
