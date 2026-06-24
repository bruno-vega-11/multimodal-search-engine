from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from texto.src.search import SearchEngine
from contextlib import asynccontextmanager
from typing import List, Optional
import pydantic
import os
import numpy as np
import pickle  


CODEBOOKS = {}
MOTOR_TEXTO = None

# --- EVENTO DE INICIALIZACIÓN (LIFESPAN) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    global MOTOR_TEXTO
    """
    Este bloque carga los Codebooks y modelos precalculados una sola vez al encender el backend.
    Evita tener que procesar el dataset entero en caliente.
    """
    print(" [INFO] Iniciando Backend: Cargando artefactos precalculados...")
    
    codebook_imagen_path = "imagen/data/codebook/codebook_kmeans.npy"
    codebook_audio_path = "audio/data/codebook/codebook_kmeans.pkl"
    
    # Validación por si acaso no están los archivos
    if not os.path.exists(codebook_imagen_path) or not os.path.exists(codebook_audio_path):
        print("[ALERTA] No se encontraron los codebooks precalculados en las carpetas.")
    
    try:
        if os.path.exists(codebook_imagen_path):
            CODEBOOKS["imagen"] = np.load(codebook_imagen_path)
            print(f"[OK] Codebook SIFT cargado con NumPy. Shape: {CODEBOOKS['imagen'].shape}")
        if os.path.exists(codebook_audio_path):
            with open(codebook_audio_path, "rb") as f:
                print(f"[OK] Codebook MFCC cargado con Pickle con exito.")
    except Exception as e:
        print(f"[ERROR] Hubo un problema al cargar los archivos: {e}")

    print("[INFO] Codebooks listos en memoria. Servidor escuchando peticiones.")
    yield  
    
    print("[INFO] Apagando Backend: Liberando memoria de Codebooks...")
    if MOTOR_TEXTO:
        MOTOR_TEXTO.close()
    CODEBOOKS.clear()

# --- INSTANCIA DE FASTAPI ---
app = FastAPI(
    title="Motor de Búsqueda - BD2",
    version="2.5.0",
    lifespan=lifespan
)

# Esquema de respuesta unificado y flexible
class SearchResult(pydantic.BaseModel):
    id: str
    dataset_type: str  # 'letra', 'ropa', 'cancion'
    score: float
    metadata: dict


# --- ENDPOINT PRINCIPAL DE BÚSQUEDA ---
@app.post("/search", response_model=List[SearchResult], tags=["Búsqueda"])
async def search(
    query_text: Optional[str] = Form(None, description="Letra de canción a buscar"),
    query_image: Optional[UploadFile] = File(None, description="Imagen de prenda de ropa para buscar similitud"),
    query_audio: Optional[UploadFile] = File(None, description="Archivo de audio para buscar canciones"),
    method: str = Form("casero"),
    top_k: int = 5
):
    resultados = []

    # =========================================================================
    # 1. BÚSQUEDA EN LETRAS DE CANCIONES (TEXTO)
    # =========================================================================
    if query_text:
        if method == "casero":
            if not MOTOR_TEXTO:
                raise HTTPException(status_code=500, detail="Motor de texto no incializado")
            print(f"Ejecutando búsqueda de texto casera para: '{query_text}'")
            raw_results = MOTOR_TEXTO.search(query_text,top_k=top_k)
            
        else:
            print(f"⚡ Buscando texto '{query_text}' mediante índice GIN nativo en Postgres")
            # query = "SELECT ... WHERE letras_tsvector @@ to_tsquery(%s)"
            resultados.append(SearchResult(id="letra_202", dataset_type="letra", score=0.88, metadata={"titulo": "Rap God", "artista": "Eminem"}))

    # =========================================================================
    # 2. BÚSQUEDA EN PRENDAS DE ROPA (IMAGEN)
    # =========================================================================
    if query_image:
        # TODO Integrante 2: Leer la imagen entrante, extraer descriptores SIFT 
        # y usar CODEBOOKS["imagen"] para armar el histograma/vector de ESTA imagen.
        # vector_query_img = cuantizar_con_codebook(query_image, CODEBOOKS["imagen"])
        
        if method == "casero":
            print(f"🔍 Buscando imagen '{query_image.filename}' calculando distancia Euclidiana en DB")
            # Tu query a Postgres calculando a mano la distancia entre el histograma generado y los de la BD
            resultados.append(SearchResult(id="ropa_401", dataset_type="ropa", score=0.89, metadata={"categoria": "Polera", "path": "/data/ropa/polera_roja.jpg"}))
        else:
            print(f"⚡ Buscando imagen '{query_image.filename}' usando índice HNSW (pgvector) en Postgres")
            # Tu query usando el operador <=> de pgvector para buscar el vecino más cercano indexado
            resultados.append(SearchResult(id="ropa_402", dataset_type="ropa", score=0.92, metadata={"categoria": "Casaca de cuero", "path": "/data/ropa/casaca_negra.jpg"}))

    # =========================================================================
    # 3. BÚSQUEDA EN CANCIONES (AUDIO)
    # =========================================================================
    if query_audio:
        # TODO Integrante 3: Leer el audio entrante, extraer coeficientes MFCC 
        # y usar CODEBOOKS["audio"] para armar el histograma/vector acústico de ESTE audio.
        # vector_query_audio = cuantizar_acustico(query_audio, CODEBOOKS["audio"])
        
        if method == "casero":
            print(f"🔍 Buscando audio '{query_audio.filename}' calculando similitud coseno en DB")
            resultados.append(SearchResult(id="track_701", dataset_type="cancion", score=0.81, metadata={"titulo": "Around the World", "artista": "Daft Punk"}))
        else:
            print(f"⚡ Buscando audio '{query_audio.filename}' usando índice HNSW (pgvector) en Postgres")
            resultados.append(SearchResult(id="track_702", dataset_type="cancion", score=0.85, metadata={"titulo": "Stairway to Heaven", "artista": "Led Zeppelin"}))

    # =========================================================================
    # ORDENAMIENTO Y RETORNO DE RESULTADOS
    # =========================================================================
    # Se ordenan todas las respuestas recolectadas de mayor a menor score
    resultados.sort(key=lambda x: x.score, reverse=True)
    
    return resultados[:top_k]