import os
import pydantic
from typing import List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Response
from contextlib import asynccontextmanager

from texto.src.search import SearchEngine           
from audio.src.audio_search_engine import AudioSearchEngine 

from imagen.src.VisualQuantizer import VisualQuantizer 

from db import get_connection

MOTOR_TEXTO = None
MOTOR_AUDIO = None
MOTOR_IMAGEN = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global MOTOR_TEXTO, MOTOR_AUDIO, MOTOR_IMAGEN
    print("[INFO] Iniciando Backend: Inicializando motores en memoria RAM...")
    
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

    yield  
    
    print("[INFO] Apagando Backend: Liberando recursos...")
    if MOTOR_TEXTO:
        try: MOTOR_TEXTO.close()
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


@app.post("/search/text", response_model=List[SearchResult], tags=["Texto"])
async def search_by_text(query_text: str = Form(..., description="Fragmento a buscar"), top_k: int = 5):
    if not MOTOR_TEXTO:
        raise HTTPException(status_code=503, detail="Motor de texto no disponible.")
    resultados = []
    try:
        raw_results = MOTOR_TEXTO.search(query_text, top_k=top_k)
        for r in raw_results:
            resultados.append(SearchResult(
                id=str(r["chunk_id"]), dataset_type="letra", score=float(r["rank_key"]),
                metadata={"title": r["title"], "artist": r["artist"], "text": r["text"]}
            ))
        resultados.sort(key=lambda x: x.score, reverse=True)
        return resultados[:top_k]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/search/audio", response_model=List[SearchResult], tags=["Audio"])
async def search_by_audio(query_audio: UploadFile = File(...), top_k: int = 5):
    if not MOTOR_AUDIO:
        raise HTTPException(status_code=503, detail="Motor de audio no disponible.")
    if not query_audio.filename.endswith(('.mp3', '.wav', '.ogg')):
        raise HTTPException(status_code=400, detail="Formato de audio no soportado.")
    resultados = []
    try:
        audio_bytes = await query_audio.read()
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
async def search_by_image(query_image: UploadFile = File(...), top_k: int = 5):
    if not MOTOR_IMAGEN:
        raise HTTPException(status_code=503, detail="El motor de imagen no está listo.")

    if not query_image.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
        raise HTTPException(status_code=400, detail="Formato de imagen no válido.")

    try:
        nombre_temporal = f"temp_{query_image.filename}"
        with open(nombre_temporal, "wb") as f:
            f.write(await query_image.read())
        try:
            histogram_vector = MOTOR_IMAGEN.image_to_histogram(nombre_temporal)
        finally:
            if os.path.exists(nombre_temporal):
                os.remove(nombre_temporal)
        vector_str = str(histogram_vector)
        sql_search = """
            SELECT id, nombre_archivo, ruta_original, (histograma_visual <=> %s::vector) AS distancia
            FROM fashion_images
            ORDER BY histograma_visual <=> %s::vector ASC
            LIMIT %s;
        """
        resultados = []
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql_search, (vector_str, vector_str, top_k))
                rows = cursor.fetchall()
                
                for row in rows:
                    id_img, nombre, ruta, distancia = row  # Ahora 'id_img' mapea correctamente el 'id'
                    resultados.append(
                        SearchResult(
                            id=str(id_img),
                            dataset_type="prenda",
                            score=round(1.0 - float(distancia), 4),
                            metadata={"nombre_archivo": nombre, "ruta_original": ruta}
                        )
                    )
        return resultados

    except Exception as e:
        print(f"[ERROR IMAGEN] Error en endpoint: {e}")
        raise HTTPException(status_code=500, detail="Error interno procesando la imagen.")


@app.get("/imagen/render/{imagen_id}", tags=["Imagen"])
async def render_image(imagen_id: int):
    """
    Busca la ruta_original en la base de datos usando el imagen_id,
    lee el archivo físico del disco duro y lo transmite al navegador.
    """
    sql = "SELECT ruta_original FROM fashion_images WHERE id = %s;"
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (imagen_id,))
                row = cursor.fetchone()
                if not row:
                    raise HTTPException(status_code=404, detail="Registro de imagen no encontrado en la base de datos.")
                ruta_original = row[0]
                
        ruta_limpia = os.path.normpath(ruta_original)

        if not os.path.exists(ruta_limpia):
            print(f"[WARN IMAGEN] El registro existe en BD pero el archivo físico no está en: {ruta_limpia}")
            raise HTTPException(status_code=404, detail="El archivo físico de la imagen no existe en el servidor.")

        with open(ruta_limpia, "rb") as f:
            contenido_imagen = f.read()
            
        return Response(content=contenido_imagen, media_type="image/jpeg")

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR RENDER] Falla al transmitir imagen_id {imagen_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno al recuperar la imagen física.")
