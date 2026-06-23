from fastapi import FastAPI, UploadFile, File, Form
from contextlib import asynccontextmanager
from typing import List, Optional
import pydantic
import os

# --- VARIABLES GLOBALES PARA LOS ÍNDICES ---
# Aquí se guardarán los índices cargados en memoria
INDICES = {}

# --- EVENTO DE INICIALIZACIÓN (LIFESPAN) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Este bloque se ejecuta UNA SOLA VEZ Se cargan los índices que ya debieron ser construidos
    previamente.
    """
    print("Iniciando Backend: Cargando índices en memoria...")
    
    # Verificación de seguridad por si el profesor olvidó correr los scripts previos
    if not os.path.exists("indices/indice_texto.pkl"):
        print("⚠️ ¡ALERTA! No se encontraron los índices construidos. Ejecuta primero 'build_indexes.py'")
    
    # Aquí cargarías tus estructuras de datos reales (ej. con pickle, faiss, etc.)
    INDICES["texto"] = "Estructura SPIMI/TF-IDF cargada"
    INDICES["imagen"] = "Codebook Visual SIFT cargado"
    INDICES["audio"] = "Codebook Acústico MFCC cargado"
    
    yield  # Aquí es donde el backend se queda "escuchando" peticiones
    
    # Esto se ejecuta cuando se apaga el servidor
    print("Apagando Backend: Liberando memoria...")


# --- INSTANCIA DE FASTAPI ---
app = FastAPI(
    title="Motor de Búsqueda Heterogéneo - BD2",
    version="2.0.0",
    lifespan=lifespan # <--- Le decimos a FastAPI que use el ciclo de vida de arriba
)

class SearchResult(pydantic.BaseModel):
    id: str
    dataset_type: str
    score: float
    metadata: dict


@app.post("/search", response_model=List[SearchResult], tags=["Búsqueda"])
async def search(
    query_text: Optional[str] = Form(None),
    query_image: Optional[UploadFile] = File(None),
    query_audio: Optional[UploadFile] = File(None),
    method: str = Form("casero"),
    top_k: int = 5
):
    resultados = []

    if query_text:
        # ¡Aquí ya puedes usar el índice cargado globalmente!
        print(f"Usando para la búsqueda: {INDICES['texto']}")
        # Lógica de búsqueda real...
        resultados.append(SearchResult(id="letra_042", dataset_type="letra", score=0.91, metadata={"titulo": "Bohemian Rhapsody"}))

    if query_image:
        print(f"Usando para la búsqueda: {INDICES['imagen']}")
        # Lógica de búsqueda real...
        resultados.append(SearchResult(id="ropa_981", dataset_type="ropa", score=0.85, metadata={"categoria": "Casaca"}))

    if query_audio:
        print(f"Usando para la búsqueda: {INDICES['audio']}")
        # Lógica de búsqueda real...
        resultados.append(SearchResult(id="track_112", dataset_type="cancion", score=0.78, metadata={"artista": "Daft Punk"}))

    resultados.sort(key=lambda x: x.score, reverse=True)
    return resultados[:top_k]