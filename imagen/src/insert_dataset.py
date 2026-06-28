import os
import glob
import psycopg2
from tqdm import tqdm
from VisualQuantizer import VisualQuantizer

def procesar_e_insertar_imagenes(carpeta_imagenes, db_config):
    print("1. Conectando a PostgreSQL...")
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
    except Exception as e:
        print(f"Error conectando a la base de datos: {e}")
        return

    print("\n2. Levantando el motor de cuantización...")

    quantizer = VisualQuantizer("codebook_kmeans.npy", k_clusters=1000)
    
    image_paths = glob.glob(os.path.join(carpeta_imagenes, "*.jpg"))
    total_imagenes = len(image_paths)
    print(f"\n3. Iniciando procesamiento de {total_imagenes} imágenes...")

    insert_query = """
        INSERT INTO fashion_images (nombre_archivo, ruta_original, histograma_visual)
        VALUES (%s, %s, %s::vector);
    """

    procesados = 0
    errores = 0

    for path in tqdm(image_paths, desc="Insertando a BD", unit="img"):
        try:
            nombre_archivo = os.path.basename(path)
            
            vector_histograma = quantizer.image_to_histogram(path)
            
            if len(vector_histograma) != 1000:
                errores += 1
                continue
                
            cursor.execute(insert_query, (nombre_archivo, path, vector_histograma))
            procesados += 1
            
            if procesados % 1000 == 0:
                conn.commit()
                
        except Exception as e:
            errores += 1
            continue

    conn.commit()
    cursor.close()
    conn.close()
    
    print("\n=== RESUMEN DE INSERCIÓN ===")
    print(f"Imágenes insertadas exitosamente: {procesados}")

if __name__ == "__main__":
    CREDENCIALES_BD = {
        "dbname": "mydb", 
        "user": "postgres",            
        "password": "postgres",     
        "host": "localhost",
        "port": "5433"                
    }
    
    CARPETA_IMAGENES = "C:/Users/Hp/.cache/kagglehub/datasets/paramaggarwal/fashion-product-images-dataset/versions/1/fashion-dataset/images"
    
    procesar_e_insertar_imagenes(CARPETA_IMAGENES, CREDENCIALES_BD)