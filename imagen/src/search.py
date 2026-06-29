import os
import psycopg
from db import get_connection  # Asumiendo que get_dict_cursor ya no es necesario si configuras la conexión

class ImageSearchEngine:
    def __init__(self, codebook_path=None):
        """
        Inicializa el motor de imágenes abriendo una única conexión reutilizable
        y montando el cuantizador visual en memoria RAM utilizando rutas relativas.
        """
        self.conn = get_connection()
        
        # --- MANEJO DE RUTAS RELATIVAS PARA EL CODEBOOK ---
        if codebook_path is None:
            RUTA_SCRIPT = os.path.dirname(os.path.abspath(__file__)) # imagen/src
            RUTA_RAIZ_IMAGEN = os.path.dirname(RUTA_SCRIPT)         # imagen/
            codebook_path = os.path.join(RUTA_RAIZ_IMAGEN, "codebook_kmeans.npy")
            
            # Si no está en imagen/, buscamos en la raíz global del proyecto
            if not os.path.exists(codebook_path):
                codebook_path = os.path.join(os.path.dirname(RUTA_RAIZ_IMAGEN), "codebook_kmeans.npy")

        # Importación local para evitar que FastAPI truene si se inicializa mal la ruta
        from .VisualQuantizer import VisualQuantizer
        self.quantizer = VisualQuantizer(codebook_path, k_clusters=1000)
        print("[OK] Motor de Búsqueda de Imágenes (SIFT + pgvector) inicializado.")

    def search(self, ruta_imagen_temporal, top_k=5):
        """
        Toma una imagen nueva del usuario, la convierte en histograma de 1000 dims
        y busca en Postgres las prendas con menor distancia Euclidiana.
        """
        # Extrae SIFT y cuantiza la imagen de la consulta en caliente
        vector_query = self.quantizer.image_to_histogram(ruta_imagen_temporal)
        
        # Aseguramos que sea una lista estándar de Python antes de pasarla a psycopg v3
        if hasattr(vector_query, "tolist"):
            vector_query = vector_query.tolist()
        else:
            vector_query = list(vector_query)
        
        # Usamos el cursor de tipo diccionario nativo de psycopg v3
        # para que devuelva llaves estructuradas tipo {'id': 1, 'nombre_archivo': '...'}
        from psycopg.rows import dict_row
        
        with self.conn.cursor(row_factory=dict_row) as cursor:
            query_sql = """
                SELECT id, nombre_archivo, ruta_original,
                       (histograma_visual <-> %s::vector) AS score
                FROM fashion_images
                ORDER BY score ASC
                LIMIT %s;
            """
            # Ejecutamos pasando el vector una sola vez porque usamos el alias 'score' en el ORDER BY
            cursor.execute(query_sql, (vector_query, top_k))
            raw_results = cursor.fetchall()
            
            # Formateamos la salida para que sea fácil de consumir por el endpoint multimodal
            resultados_limpios = []
            for r in raw_results:
                resultados_limpios.append({
                    "id_prenda": r["id"],
                    "nombre": r["nombre_archivo"],
                    "ruta_original": r["ruta_original"],
                    "distancia": r["score"]  # A menor distancia, más idéntica es la ropa
                })
                
            return resultados_limpios

    def close(self):
        """Cierra la conexión de manera limpia al apagar el backend"""
        if self.conn:
            self.conn.close()
            print("[INFO] Conexión del motor de imágenes cerrada.")