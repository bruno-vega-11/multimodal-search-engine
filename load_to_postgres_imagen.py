import json
from tqdm import tqdm

# Importamos las funciones directamente de tu archivo db.py
from db import get_connection, get_dict_cursor

def subir_a_bd(archivo_datos):
    print("1. Conectando a PostgreSQL a través de db.py...")
    try:
        # Reutilizamos tu función para abrir la conexión
        conn = get_connection()
        cursor = conn.cursor() 
        # Si en algún momento necesitas que el cursor devuelva diccionarios, 
        # podrías usar: cursor = get_dict_cursor(conn)
    except Exception as e:
        print(f"Error conectando a la base de datos: {e}")
        return

    # Mantenemos tu consulta original (con el cast ::vector de pgvector)
    insert_query = """
        INSERT INTO fashion_images (nombre_archivo, ruta_original, histograma_visual)
        VALUES (%s, %s, %s::vector);
    """

    procesados = 0
    errores = 0

    print(f"\n2. Leyendo datos desde '{archivo_datos}'...")
    
    try:
        # Contamos las líneas primero para que la barra de tqdm sea exacta
        with open(archivo_datos, 'r', encoding='utf-8') as f:
            total_lineas = sum(1 for _ in f)

        # Abrimos el archivo y lo procesamos línea por línea (eficiente en memoria)
        with open(archivo_datos, 'r', encoding='utf-8') as f:
            for linea in tqdm(f, total=total_lineas, desc="Insertando a BD", unit="img"):
                try:
                    linea = linea.strip()
                    if not linea:
                        continue # Salta líneas vacías si las hay
                        
                    # Reconstruimos el diccionario desde el texto JSON
                    dato = json.loads(linea)
                    
                    # Ejecutamos el INSERT con tus datos
                    cursor.execute(insert_query, (
                        dato["nombre_archivo"], 
                        dato["ruta_original"], 
                        dato["histograma"]
                    ))
                    procesados += 1
                    
                    # Commit en bloques de 1000 por seguridad y velocidad
                    if procesados % 1000 == 0:
                        conn.commit()
                        
                except Exception as e:
                    errores += 1
                    continue
                    
        # Commit final para los registros restantes
        conn.commit()
        print("\n💾 ¡Todos los cambios guardados correctamente!")
        
    except FileNotFoundError:
        print(f"❌ No se encontró el archivo '{archivo_datos}'.")
    except Exception as e:
        print(f"❌ Ocurrió un error inesperado durante la carga: {e}")
    finally:
        # Nos aseguramos de cerrar el cursor y la conexión siempre
        cursor.close()
        conn.close()
        print("🔌 Conexión a la base de datos cerrada limpiamente.")
    
    print("\n=== RESUMEN DE INSERCIÓN ===")
    print(f"✅ Registros inyectados en la Base de Datos: {procesados}")
    print(f"❌ Errores en BD: {errores}")

if __name__ == "__main__":
    # Nombre de tu archivo JSON Lines
    ARCHIVO_DATOS = "vectores_fashion.jsonl"
    
    subir_a_bd(ARCHIVO_DATOS)