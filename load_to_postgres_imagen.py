import os
import json
from tqdm import tqdm

# Importamos las funciones directamente de tu archivo db.py
from db import get_connection

def subir_a_bd():
    print("🔌 1. Conectando a PostgreSQL a través de db.py...")
    try:
        # Reutilizamos tu función para abrir la conexión en psycopg v3
        conn = get_connection()
        cursor = conn.cursor() 
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        return

    # Mantenemos tu consulta original (con el cast ::vector de pgvector)
    insert_query = """
        INSERT INTO fashion_images (nombre_archivo, ruta_original, histograma_visual)
        VALUES (%s, %s, %s::vector);
    """

    # --- CONFIGURACIÓN DE RUTA DINÁMICA CORREGIDA ---
    # Como el script está en la raíz 'multimodal-search-engine', SCRIPT_DIR obtiene esa misma carpeta.
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Entramos directo a la subcarpeta del dataset de imágenes sin retroceder de más
    archivo_datos = os.path.join(SCRIPT_DIR, "imagen", "data", "processed", "vectores_fashion.jsonl")

    print(f"📂 2. Leyendo datos desde: {archivo_datos}")
    
    procesados = 0
    errores = 0

    try:
        # Contamos las líneas primero para que la barra de tqdm sea exacta
        with open(archivo_datos, 'r', encoding='utf-8') as f:
            total_lineas = sum(1 for _ in f)

        # Abrimos el archivo y lo procesamos línea por línea (eficiente en memoria)
        with open(archivo_datos, 'r', encoding='utf-8') as f:
            for linea in tqdm(f, total=total_lineas, desc="Insertando vectores pgvector", unit="img"):
                try:
                    linea = linea.strip()
                    if not linea:
                        continue # Salta líneas vacías si las hay
                        
                    # Reconstruimos el diccionario desde el texto JSON
                    dato = json.loads(linea)
                    
                    # Convertimos la lista del histograma a string con formato de vector para pgvector: '[0.1, 0.2, ...]'
                    histograma_str = str(dato["histograma"])
                    
                    # Ejecutamos el INSERT
                    cursor.execute(insert_query, (
                        dato["nombre_archivo"], 
                        dato["ruta_original"], 
                        histograma_str
                    ))
                    procesados += 1
                    
                    # Commit en bloques de 1000 por rendimiento y seguridad
                    if procesados % 1000 == 0:
                        conn.commit()
                        
                except Exception as e:
                    errores += 1
                    # Usamos tqdm.write para no romper la barra de carga en consola
                    tqdm.write(f"❌ Error en línea {procesados + errores}: {e}")
                    continue
                    
        # Commit final para los registros restantes
        conn.commit()
        print("\n💾 ¡Todos los cambios guardados correctamente en PostgreSQL!")
        
    except FileNotFoundError:
        print(f"❌ Error crítico: No se encontró el archivo JSONL en la ruta calculada:\n   {archivo_datos}")
    except Exception as e:
        print(f"❌ Ocurrió un error inesperado durante la carga: {e}")
    finally:
        # Nos aseguramos de cerrar el cursor y la conexión siempre
        cursor.close()
        conn.close()
        print("🔌 Conexión a la base de datos cerrada limpiamente.")
    
    print("\n=== RESUMEN DE INSERCIÓN ===")
    print(f"✅ Registros inyectados en fashion_images: {procesados}")
    print(f"❌ Errores omitidos:                      {errores}")

if __name__ == "__main__":
    subir_a_bd()