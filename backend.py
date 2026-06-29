import os
import pydantic
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from contextlib import asynccontextmanager

# --- IMPORTACIONES DE LOS MOTORES DE TUS COMPAÑEROS ---
from texto.src.search import SearchEngine          # Motor de texto (SPIMI / Postgres)

# --- CONFIGURACIÓN DE LAS VARIABLES GLOBALES ---
MOTOR_TEXTO = None

# --- EVENTO DE INICIALIZACIÓN Y APAGADO (LIFESPAN) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    global MOTOR_TEXTO, MOTOR_IMAGEN
    print("[INFO] Iniciando Backend: Inicializando motores en memoria RAM...")
    
    # 1. Inicializar Motor de Texto
    try:
        MOTOR_TEXTO = SearchEngine()
        print("[OK] Motor de búsqueda de texto conectado correctamente a Postgres.")
    except Exception as e:
        print(f"[ERROR] No se pudo levantar el motor de texto: {e}")

    # 2. Inicializar Motor de Imagen

    yield  # Aquí es donde el servidor se queda escuchando peticiones en la web
    
    # --- PROCESO DE APAGADO (Liberación de recursos) ---
    print("[INFO] Apagando Backend: Liberando conexiones de PostgreSQL y memoria...")
    if MOTOR_TEXTO:
        MOTOR_TEXTO.close()
    print("[INFO] Servidor apagado limpiamente.")


# --- INSTANCIA OFICIAL DE FASTAPI ---
app = FastAPI(
    title="Motor de Búsqueda Heterogéneo Multimodal - BD2",
    description="Backend unificado para búsquedas de letras (texto), ropa (imágenes) y audio.",
    version="3.5.0",
    lifespan=lifespan
)

# --- ESQUEMA DE RESPUESTA REQUERIDO POR PYDANTIC ---
class SearchResult(pydantic.BaseModel):
    id: str
    dataset_type: str  # 'letra', 'ropa', 'cancion'
    score: float       # rank_key continuo para texto, distancia L2 para imagen
    metadata: dict     # Información flexible que consumirá el Frontend


# --- ENDPOINT PRINCIPAL MULTIMODAL ---
@app.post("/search", response_model=List[SearchResult], tags=["Búsqueda"])
async def search(
    query_text: Optional[str] = Form(None, description="Letra de canción a buscar"),
    top_k: int = 5
):
    resultados = []

    # =========================================================================
    # 1. ENTRADA DE TEXTO (Letras de Canciones)
    # =========================================================================
    if query_text:
       raw_results = MOTOR_TEXTO.search(query_text,top_k=top_k)
       for r in raw_results:
           resultados.append(
               SearchResult(
                id=str(r["chunk_id"]),
                dataset_type="letra",
                score=r["rank_key"], # -> similitud coseno
                metadata={
                    "title": r["title"],
                    "artist": r["artist"],
                    "text": r["text"]
                    }   
                )   
           )

    # ========================================================================
    # ORDENAMIENTO GLOBAL Y RETORNO
    # =========================================================================
    # Nota de diseño: Si mezclan búsquedas (ej. texto e imagen a la vez), aquí se ordenan.
    # Para imágenes, recuerden que a menor distancia (score), más idéntica es la prenda.
    if query_text:
        # Si se buscó texto, ordenamos de mayor a menor score de similitud coseno
        resultados.sort(key=lambda x: x.score, reverse=True)
    return resultados[:top_k]