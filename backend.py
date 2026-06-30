import os
import pydantic
from typing import List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Response
from contextlib import asynccontextmanager

# --- IMPORTACIONES DE LOS MOTORES (MÓDULOS PROPIOS) ---
from texto.src.search import SearchEngine           
from audio.src.audio_search_engine import AudioSearchEngine 

# 🔥 IMPORTACIÓN DEL MOTOR DE IMAGEN DESDE TU ARCHIVO
# Ajusta la ruta de importación según dónde guardaste el archivo de tu amigo
from imagen.src.VisualQuantizer import VisualQuantizer 

from db import get_connection

# --- CONFIGURACIÓN DE LAS VARIABLES GLOBALES ---
MOTOR_TEXTO = None
MOTOR_AUDIO = None
MOTOR_IMAGEN = None

# --- EVENTO DE INICIALIZACIÓN Y APAGADO (LIFESPAN) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    global MOTOR_TEXTO, MOTOR_AUDIO, MOTOR_IMAGEN
    print("[INFO] Iniciando Backend: Inicializando motores en memoria RAM...")
    
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

    # 1. Inicializar Motor de Texto
    try:
        MOTOR_TEXTO = SearchEngine()
        print("[OK] Motor de búsqueda de texto conectado correctamente.")
    except Exception as e:
        print(f"[ERROR] No se pudo levantar el motor de texto: {e}")

    # 2. Inicializar Motor de Audio
    try:
        MOTOR_AUDIO = AudioSearchEngine()
        print("[OK] Motor de búsqueda de audio cargado en RAM.")
    except Exception as e:
        print(f"[ERROR] No se pudo levantar el motor de audio: {e}")

    # 3. Inicializar Motor de Imagen (Cargando tu componente importado)
    try:
        # Buscamos el codebook_kmeans.npy en la raíz del backend
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


# --- INSTANCIA OFICIAL DE FASTAPI ---
app = FastAPI(
    title="Motor de Búsqueda Heterogéneo Multimodal - BD2",
    description="Backend unificado para consultas distribuidas de Texto, Audio e Imagen.",
    version="3.0.0",
    lifespan=lifespan
)

# --- ESQUEMA DE RESPUESTA PYDANTIC ---
class SearchResult(pydantic.BaseModel):
    id: str
    dataset_type: str  # 'letra', 'cancion' o 'prenda'
    score: float       # Métrica de similitud
    metadata: dict     # Campos para pintar en el Frontend


# --- HELPER DE AUDIO ---
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

# =========================================================================
# 🔤 ENDPOINT 1: BÚSQUEDA POR TEXTO (Letras)
# =========================================================================
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


# =========================================================================
# 🎵 ENDPOINT 2: BÚSQUEDA POR AUDIO (Muestras .mp3)
# =========================================================================
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
            metadata_bd["audio_url"] = f"http://localhost:8000/audio/stream/{audio_id}"
            resultados.append(SearchResult(
                id=str(audio_id), dataset_type="cancion", score=float(r["similarity_score"]), metadata=metadata_bd
            ))
        resultados.sort(key=lambda x: x.score, reverse=True)
        return resultados[:top_k]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================================================================
# 🔊 ENDPOINT 3: TRANSMITIR AUDIO BINARIO
# =========================================================================
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


# =========================================================================
# 🖼️ ENDPOINT 4: BÚSQUEDA POR IMAGEN (Corregido con la columna 'id' real)
# =========================================================================
@app.post("/search/image", response_model=List[SearchResult], tags=["Imagen"])
async def search_by_image(query_image: UploadFile = File(...), top_k: int = 5):
    if not MOTOR_IMAGEN:
        raise HTTPException(status_code=503, detail="El motor de imagen no está listo.")

    if not query_image.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
        raise HTTPException(status_code=400, detail="Formato de imagen no válido.")

    try:
        # 1. Creamos el archivo temporal en disco
        nombre_temporal = f"temp_{query_image.filename}"
        with open(nombre_temporal, "wb") as f:
            f.write(await query_image.read())
        
        try:
            # 2. Extraemos el histograma con el código de tu amigo
            histogram_vector = MOTOR_IMAGEN.image_to_histogram(nombre_temporal)
        finally:
            if os.path.exists(nombre_temporal):
                os.remove(nombre_temporal)
        
        vector_str = str(histogram_vector)

        # 3. 🔥 SQL CORREGIDO: Cambiado 'id_imagen' por el 'id' real de tu tabla
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

# =========================================================================
# 🖼️ ENDPOINT 5: TRANSMITIR IMAGEN FÍSICA (Para renderizar en Web)
# =========================================================================
@app.get("/imagen/render/{imagen_id}", tags=["Imagen"])
async def render_image(imagen_id: int):
    """
    Busca la ruta_original en la base de datos usando el imagen_id,
    lee el archivo físico del disco duro y lo transmite al navegador.
    """
    # 1. Consultamos la ruta en la base de datos
    sql = "SELECT ruta_original FROM fashion_images WHERE id = %s;"
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (imagen_id,))
                row = cursor.fetchone()
                
                if not row:
                    raise HTTPException(status_code=404, detail="Registro de imagen no encontrado en la base de datos.")
                
                ruta_original = row[0]
                
        # 2. Normalizamos la ruta por si tiene slashes cruzados de Windows/Linux
        ruta_limpia = os.path.normpath(ruta_original)

        # 3. Verificamos si el archivo realmente existe en el disco duro
        if not os.path.exists(ruta_limpia):
            print(f"[WARN IMAGEN] El registro existe en BD pero el archivo físico no está en: {ruta_limpia}")
            raise HTTPException(status_code=404, detail="El archivo físico de la imagen no existe en el servidor.")

        # 4. Leemos los bytes de la imagen y los transmitimos
        with open(ruta_limpia, "rb") as f:
            contenido_imagen = f.read()
            
        # Retornamos la respuesta binaria cruda
        return Response(content=contenido_imagen, media_type="image/jpeg")

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR RENDER] Falla al transmitir imagen_id {imagen_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno al recuperar la imagen física.")