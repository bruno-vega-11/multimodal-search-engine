import os
import json
from db import get_connection

BATCH_SIZE = 5000  

def _batched(rows, batch_size):
    for i in range(0, len(rows), batch_size):
        yield rows[i:i + batch_size]

def main():
    # --- CONFIGURACIÓN DE RUTAS RELATIVAS DINÁMICAS ---
    # RUTA_SCRIPT apuntará a la carpeta donde esté este archivo
    RUTA_SCRIPT = os.path.dirname(os.path.abspath(__file__))
    
    # Subimos a la raíz del módulo de imágenes si es necesario, 
    # o apuntamos directo a la carpeta data/processed
    # Si ejecutas desde la raíz del proyecto (multimodal-search-engine):
    RUTA_JSON = os.path.join(RUTA_SCRIPT, "imagen", "data", "processed", "image_histograms.json")
    
    # Control de seguridad por si acaso estás ejecutándolo parado dentro de la misma carpeta 'imagen'
    if not os.path.exists(RUTA_JSON):
        RUTA_JSON = os.path.join(RUTA_SCRIPT, "data", "processed", "image_histograms.json")

    # Verificar si el archivo JSON existe antes de continuar
    if not os.path.exists(RUTA_JSON):
        print(f"[ERROR] No se encontró el archivo de histogramas en: {RUTA_JSON}")
        print("Por favor, ejecuta primero 'build_imagen_histograms.py' para generarlo.")
        return

    # 1. LEER LOS DATOS PROCESADOS EN FRÍO
    print(f"\n[1/3] Leyendo archivo de histogramas desde: {RUTA_JSON}...")
    with open(RUTA_JSON, "r", encoding="utf-8") as f:
        histograms_dataset = json.load(f)

    # Reestructuramos los datos del JSON al formato de tuplas que requiere executemany
    rows = []
    for nombre_archivo, info in histograms_dataset.items():
        rows.append((nombre_archivo, info["ruta_original"], info["histograma"]))

    print(f"      Se prepararon {len(rows)} registros listos para la persistencia.")

    # 2. CONEXIÓN Y PERSISTENCIA EN POSTGRES
    # Usa tu db.py unificado que jala las credenciales de tu .env automáticamente
    conn = get_connection()
    try:
        print("\n[2/3] Limpiando la tabla 'fashion_images' en PostgreSQL...")
        with conn.cursor() as cur:
            # Reseteamos la tabla para que empiece limpia y con IDs desde 1
            cur.execute("TRUNCATE fashion_images RESTART IDENTITY CASCADE")
        conn.commit()

        print(f"\n[3/3] Insertando vectores en bloques de {BATCH_SIZE}...")
        insert_query = """
            INSERT INTO fashion_images (nombre_archivo, ruta_original, histograma_visual)
            VALUES (%s, %s, %s::vector);
        """
        
        with conn.cursor() as cur:
            # Insertamos en ráfagas eficientes gracias a psycopg v3
            for batch in _batched(rows, BATCH_SIZE):
                cur.executemany(insert_query, batch)
        
        conn.commit()
        print(f"\n[OK] Carga masiva finalizada. {len(rows)} imágenes guardadas con éxito en Postgres.")

    except Exception as e:
        print(f"\n[ERROR] Ocurrió un fallo durante la carga a la base de datos: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()