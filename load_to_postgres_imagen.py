import os
import json
from tqdm import tqdm
from db import get_connection

def subir_a_bd():
    print("🔌 1. Conectando a PostgreSQL a través de db.py...")
    try:
        conn = get_connection()
        cursor = conn.cursor() 
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        return

    insert_query = """
        INSERT INTO fashion_images (nombre_archivo, ruta_original, histograma_visual)
        VALUES (%s, %s, %s::vector);
    """
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    archivo_datos = os.path.join(SCRIPT_DIR, "imagen", "data", "processed", "vectores_fashion.jsonl")

    print(f"📂 2. Leyendo datos desde: {archivo_datos}")
    
    procesados = 0
    errores = 0

    try:
        with open(archivo_datos, 'r', encoding='utf-8') as f:
            total_lineas = sum(1 for _ in f)

        with open(archivo_datos, 'r', encoding='utf-8') as f:
            for linea in tqdm(f, total=total_lineas, desc="Insertando vectores pgvector", unit="img"):
                try:
                    linea = linea.strip()
                    if not linea:
                        continue # Salta líneas vacías si las hay
                        
                    dato = json.loads(linea)
                    histograma_str = str(dato["histograma"])
                    
             
                    cursor.execute(insert_query, (
                        dato["nombre_archivo"], 
                        dato["ruta_original"], 
                        histograma_str
                    ))
                    procesados += 1
                    if procesados % 1000 == 0:
                        conn.commit()
                except Exception as e:
                    errores += 1
                    tqdm.write(f"❌ Error en línea {procesados + errores}: {e}")
                    continue
        conn.commit()
        print("\n💾 ¡Todos los cambios guardados correctamente en PostgreSQL!")
        
    except FileNotFoundError:
        print(f"❌ Error crítico: No se encontró el archivo JSONL en la ruta calculada:\n   {archivo_datos}")
    except Exception as e:
        print(f"❌ Ocurrió un error inesperado durante la carga: {e}")
    finally:
        cursor.close()
        conn.close()
        print("🔌 Conexión a la base de datos cerrada limpiamente.")
    
    print("\n=== RESUMEN DE INSERCIÓN ===")
    print(f"✅ Registros inyectados en fashion_images: {procesados}")
    print(f"❌ Errores omitidos:                      {errores}")

if __name__ == "__main__":
    subir_a_bd()
