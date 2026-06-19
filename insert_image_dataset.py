import os
import glob
import mimetypes
import psycopg2
from PIL import Image

# Tras haber ejecutado "download_images_dataset.py", modificar la ruta donde están las imágenes
IMAGES_PATH = r"E:\Dataset-Visual-E-commerce\fashion-dataset\fashion-dataset\images"

def connect_db():
    return psycopg2.connect(
        dbname="sistema_multimodal",
        user="postgres",
        password="123456",
        host="localhost",
        port="5433"
    )


def obtener_datos_imagen(image_path):
    filename = os.path.basename(image_path)
    file_size = os.path.getsize(image_path)
    content_type, _ = mimetypes.guess_type(image_path)
    if content_type is None:
        content_type = "image/jpeg"
    with Image.open(image_path) as img:
        width, height = img.size
    with open(image_path, "rb") as f:
        image_data = f.read()
    return filename, image_data, content_type, file_size, width, height



def insertar_imagen(cursor, filename, image_data, content_type, file_size, width, height):
    sql = """
        INSERT INTO images_dataset (
            filename,
            image_data,
            content_type,
            file_size,
            width,
            height
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (filename) DO NOTHING;
    """
    cursor.execute(sql, (
        filename,
        psycopg2.Binary(image_data),
        content_type,
        file_size,
        width,
        height
    ))


def cargar_imagenes_a_postgres():
    image_files = glob.glob(os.path.join(IMAGES_PATH, "*.jpg"))
    print("Cantidad de imágenes encontradas:", len(image_files))
    conn = connect_db()
    cursor = conn.cursor()
    insertadas = 0
    duplicadas_o_ignoradas = 0
    errores = 0
    for i, image_path in enumerate(image_files, start=1):
        try:
            filename, image_data, content_type, file_size, width, height = obtener_datos_imagen(image_path)
            insertar_imagen(
                cursor,
                filename,
                image_data,
                content_type,
                file_size,
                width,
                height
            )
            if cursor.rowcount == 1:
                insertadas += 1
                print(f"[{i}] Insertada: {filename}")
            else:
                duplicadas_o_ignoradas += 1
                print(f"[{i}] Ya existía, ignorada: {filename}")
            if i % 500 == 0:
                conn.commit()
                print(f"Commit realizado hasta la imagen {i}")
        except Exception as e:
            errores += 1
            print(f"Error con imagen: {image_path}")
            print(e)

    conn.commit()
    cursor.close()
    conn.close()

    print("\nProceso terminado")
    print("Imágenes insertadas:", insertadas)
    print("Duplicadas o ignoradas:", duplicadas_o_ignoradas)
    print("Errores:", errores)

cargar_imagenes_a_postgres()