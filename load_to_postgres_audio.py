import os
import glob
from tqdm import tqdm
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from dotenv import load_dotenv

from db import get_connection


load_dotenv()
AUDIO_DIR = os.getenv("AUDIO_DIR", r"")

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
        data["audio_data"],
        data["content_type"],
        data["file_size"],
        data["duration_seconds"]
    ))

def cargar_audios_a_postgres():
    patron_busqueda = os.path.join(AUDIO_DIR, "**" , "*.mp3")
    audio_files = glob.glob(patron_busqueda, recursive=True)
    total_audios = len(audio_files)    
    if total_audios == 0:
        print("⚠ No se encontraron archivos .mp3 en la ruta especificada.")
        return

    try:
        conn = get_connection()
        cursor = conn.cursor()
    except Exception as e:
        print(f"Error crítico de conexión: {e}")
        return

    insertados = 0
    ignorados = 0
    errores = 0

    print("\n🚀 Iniciando carga de audios...")
    for i, audio_path in enumerate(tqdm(audio_files, desc="Inyectando audios", unit="track"), start=1):
        try:
            data = obtener_metadata_audio(audio_path)
            insertar_audio(cursor, data)
            
            if cursor.rowcount == 1:
                insertados += 1
            else:
                ignorados += 1

            if i % 200 == 0:
                conn.commit()

        except Exception as e:
            errores += 1
            tqdm.write(f"❌ Error procesando {os.path.basename(audio_path)}: {e}")

    conn.commit()
    cursor.close()
    conn.close()
    print("🔌 Conexión cerrada limpiamente.")

    print("\n=== RESUMEN DE CARGA DE AUDIOS ===")
    print(f"✅ Audios insertados exitosamente: {insertados}")
    print(f"🔕 Audios ignorados (duplicados):  {ignorados}")
    print(f"❌ Errores en el proceso:          {errores}")


if __name__ == "__main__":
    cargar_audios_a_postgres()
