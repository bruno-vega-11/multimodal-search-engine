from fastapi import FastAPI, UploadFile, File, Form, Query
from typing import List, Optional
import pydantic

app = FastAPI(
    title="Motor de Búsqueda Multimodal - BD2",
    description="API para la búsqueda unificada de Texto, Imagen y Audio usando métodos caseros y nativos.",
    version="1.0.0"
)

# --- MODELOS DE DATOS (Esquemas para las respuestas) ---
class SearchResult(pydantic.BaseModel):
    chunk_id: int
    video_id: str
    chunk_type: str  # 'text', 'image', 'audio'
    score: float     # El puntaje de similitud obtenido
    content_preview: str # Texto crudo o ruta del archivo multimedia

# --- ENDPOINTS DE LA SEMANA 1 (Estructura base) ---

@app.get("/", tags=["General"])
def read_root():
    return {"status": "online", "proyecto": "Motor Multimodal BD2", "dataset": "ontocord/VALID"}


# --- ENDPOINTS DE LA SEMANA 2 (Integración y Fusión) ---

@app.post("/search/text", response_model=List[SearchResult], tags=["Búsquedas Individuales"])
async def search_by_text(
    query: str = Query(..., description="Texto de consulta para el índice invertido (SPIMI/TF-IDF)"),
    top_k: int = 5
):
    """
    Endpoint para el Integrante 1 (Texto).
    Recibe un texto, debería pasarlo por el pipeline de limpieza y consultar su índice invertido casero.
    """
    # TODO: Aquí se llamará a la función del Integrante 1: pipeline_limpieza(query) -> buscar_spimi()
    print(f"Buscando texto crudo: '{query}'")
    
    # Simulación de respuesta (Mock data)
    return [
        SearchResult(chunk_id=101, video_id="vid_001", chunk_type="text", score=0.95, content_preview="Transcripción simulada que coincide con la query"),
        SearchResult(chunk_id=102, video_id="vid_002", chunk_type="text", score=0.82, content_preview="Otra descripción de texto que hace match")
    ]


@app.post("/search/image", response_model=List[SearchResult], tags=["Búsquedas Individuales"])
async def search_by_image(
    file: UploadFile = File(..., description="Imagen de consulta (se le extraerá SIFT)"),
    top_k: int = 5
):
    """
    Endpoint para el Integrante 2 (Imagen).
    Recibe un archivo de imagen, le extrae descriptores SIFT y genera el histograma basado en el Codebook Visual.
    """
    # TODO: Aquí se llamará al módulo de imagen: extraer_sift(file) -> cuantizar_con_codebook()
    print(f"Recibida imagen de consulta: {file.filename}")
    
    return [
        SearchResult(chunk_id=201, video_id="vid_005", chunk_type="image", score=0.89, content_preview="/data/frames/frame_23.jpg"),
        SearchResult(chunk_id=202, video_id="vid_001", chunk_type="image", score=0.74, content_preview="/data/frames/frame_89.jpg")
    ]


@app.post("/search/audio", response_model=List[SearchResult], tags=["Búsquedas Individuales"])
async def search_by_audio(
    file: UploadFile = File(..., description="Clip de audio de consulta (se le extraerá MFCC)"),
    top_k: int = 5
):
    """
    Endpoint para el Integrante 3 (Audio).
    Recibe un archivo de sonido, le aplica ventanas deslizantes, extrae MFCC y genera el histograma acústico.
    """
    # TODO: Aquí se llamará al módulo de audio: extraer_mfcc(file) -> cuantizar_con_codebook_acustico()
    print(f"Recibido audio de consulta: {file.filename}")
    
    return [
        SearchResult(chunk_id=301, video_id="vid_009", chunk_type="audio", score=0.91, content_preview="/data/audio/clip_12.wav"),
        SearchResult(chunk_id=302, video_id="vid_002", chunk_type="audio", score=0.79, content_preview="/data/audio/clip_04.wav")
    ]


# --- EL CORE DE TU ROL: FUSIÓN MULTIMODAL ---

@app.post("/search/multimodal", response_model=List[SearchResult], tags=["Core Multimodal"])
async def search_multimodal(
    text_query: Optional[str] = Form(None, description="Consulta opcional de texto"),
    image_file: Optional[UploadFile] = File(None, description="Consulta opcional de imagen"),
    audio_file: Optional[UploadFile] = File(None, description="Consulta opcional de audio"),
    alpha: float = Form(0.4, description="Peso para el score de texto"),
    beta: float = Form(0.3, description="Peso para el score de imagen"),
    gamma: float = Form(0.3, description="Peso para el score de audio"),
    method: str = Form("casero", description="Método de búsqueda: 'casero' (Tus histogramas/SPIMI) o 'nativo' (Índices Postgres GIN/HNSW)"),
    top_k: int = 5
):
    """
    ESTE ES TU ENDPOINT (Integrante 5).
    Aquí recibes consultas mixtas (pueden subir texto + imagen a la vez, o solo audio, etc.).
    Llamas a los submódulos correspondientes, obtienes los rankings individuales y aplicas tu 
    Algoritmo de Fusión de Scores multiplicando por los pesos (alpha, beta, gamma).
    Además, según el parámetro 'method', decides si tiras por tu lógica o por las búsquedas de Postgres nativo.
    """
    print(f"Ejecutando búsqueda multimodal usando método: {method}")
    print(f"Pesos configurados -> Texto (alpha): {alpha}, Imagen (beta): {beta}, Audio (gamma): {gamma}")
    
    # Simulación de la Fusión de Scores
    # En código real harás algo como: score_final = (alpha * score_txt) + (beta * score_img) + (gamma * score_audio)
    
    if method == "casero":
        return [
            SearchResult(chunk_id=501, video_id="vid_001", chunk_type="mixed", score=0.88, content_preview="Resultado unificado usando histogramas caseros"),
            SearchResult(chunk_id=502, video_id="vid_002", chunk_type="mixed", score=0.79, content_preview="Segundo resultado unificado casero")
        ]
    else:
        # Modo nativo usando índices GIN y HNSW en pgvector (Issue 7)
        return [
            SearchResult(chunk_id=501, video_id="vid_001", chunk_type="mixed", score=0.92, content_preview="Resultado indexado velozmente con HNSW en Postgres"),
            SearchResult(chunk_id=503, video_id="vid_012", chunk_type="mixed", score=0.85, content_preview="Resultado indexado velozmente con GIN/pgvector")
        ]