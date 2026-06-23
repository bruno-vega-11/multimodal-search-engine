import os
import glob
import psycopg2
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3

# Tras haber descargado los audios, modificar esta rutas
AUDIO_DIR = r"E:\Dataset-Musical-Inteligente\fma_small"
def connect_db():
    return psycopg2.connect(
        dbname="sistema_multimodal",
        user="postgres",
        password="123456",
        host="localhost",
        port="5433"
    )

def obtener_metadata_audio(audio_path):
    filename = os.path.basename(audio_path)
    file_size = os.path.getsize(audio_path)
    # Duración del audio
    audio_info = MP3(audio_path)
    duration_seconds = audio_info.info.length
    track_number = None
    title = None
    collaborators = None
    album = None

    try:
        tags = EasyID3(audio_path)
        title = tags.get("title", [None])[0]
        collaborators = tags.get("artist", [None])[0]
        album = tags.get("album", [None])[0]
        track_raw = tags.get("tracknumber", [None])[0]
        if track_raw is not None:
            track_number = int(str(track_raw).split("/")[0])

    except Exception:
        pass

    with open(audio_path, "rb") as f:
        audio_data = f.read()
    return {
        "filename": filename,
        "track_number": track_number,
        "title": title,
        "collaborators": collaborators,
        "album": album,
        "audio_data": audio_data,
        "content_type": "audio/mpeg",
        "file_size": file_size,
        "duration_seconds": duration_seconds
    }



def insertar_audio(cursor, data):
    sql = """
        INSERT INTO audio_dataset (
            filename,
            track_number,
            title,
            collaborators,
            album,
            audio_data,
            content_type,
            file_size,
            duration_seconds
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (filename) DO NOTHING;
    """
    cursor.execute(sql, (
        data["filename"],
        data["track_number"],
        data["title"],
        data["collaborators"],
        data["album"],
        psycopg2.Binary(data["audio_data"]),
        data["content_type"],
        data["file_size"],
        data["duration_seconds"]
    ))

def cargar_audios_a_postgres():
    audio_files = glob.glob(
        os.path.join(AUDIO_DIR, "**", "*.mp3"),
        recursive=True
    )
    print("Cantidad de audios encontrados:", len(audio_files))
    conn = connect_db()
    cursor = conn.cursor()
    insertados = 0
    ignorados = 0
    errores = 0
    for i, audio_path in enumerate(audio_files, start=1):
        try:
            data = obtener_metadata_audio(audio_path)
            insertar_audio(cursor, data)
            if cursor.rowcount == 1:
                insertados += 1
                print(f"[{i}] Insertado: {data['filename']} | {data['title']}")
            else:
                ignorados += 1
                print(f"[{i}] Ya existía, ignorado: {data['filename']}")

            if i % 200 == 0:
                conn.commit()
                print(f"Commit realizado hasta el audio {i}")

        except Exception as e:
            errores += 1
            print(f"Error con audio: {audio_path}")
            print(e)

    conn.commit()
    cursor.close()
    conn.close()
    print("\nProceso terminado")
    print("Audios insertados:", insertados)
    print("Audios ignorados por duplicado:", ignorados)
    print("Errores:", errores)

cargar_audios_a_postgres()