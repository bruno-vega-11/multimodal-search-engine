import pandas as pd
import psycopg2

# No cambiar ruta
CSV_FILE = "spotify_songs.csv"

def connect_db():
    return psycopg2.connect(
        dbname="sistema_multimodal",
        user="postgres",
        password="123456",
        host="localhost",
        port="5433"
    )


def limpiar_texto(valor):
    if pd.isna(valor):
        return None
    valor = str(valor).strip()
    return valor if valor != "" else None


def limpiar_int(valor):
    if pd.isna(valor) or str(valor).strip() == "":
        return None
    try:
        return int(float(valor))
    except Exception:
        return None


def limpiar_float(valor):
    if pd.isna(valor) or str(valor).strip() == "":
        return None
    try:
        return float(valor)
    except Exception:
        return None



def leer_csv():
    try:
        df = pd.read_csv(CSV_FILE, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(CSV_FILE, encoding="latin1")
    df.columns = df.columns.str.strip()
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    print("Columnas encontradas:")
    print(df.columns.tolist())
    return df



def limpiar_fecha(valor):
    if pd.isna(valor):
        return None
    fecha = pd.to_datetime(valor, errors="coerce")
    if pd.isna(fecha):
        return None
    return fecha.date()




def importar_textos():
    df = leer_csv()
    columnas_necesarias = [
        "track_id",
        "track_name",
        "track_artist",
        "lyrics",
        "track_popularity",
        "track_album_id",
        "track_album_name",
        "track_album_release_date",
        "playlist_name",
        "playlist_id",
        "playlist_genre",
        "playlist_subgenre",
        "danceability",
        "energy",
        "key",
        "loudness",
        "mode",
        "speechiness",
        "acousticness",
        "instrumentalness",
        "liveness",
        "valence",
        "tempo",
        "duration_ms",
        "language"
    ]

    faltantes = [col for col in columnas_necesarias if col not in df.columns]
    if faltantes:
        print("Faltan columnas en el CSV:")
        print(faltantes)
        return

    df = df[columnas_necesarias]
    df["track_album_release_date"] = pd.to_datetime(
        df["track_album_release_date"],
        errors="coerce"
    ).dt.date
    conn = connect_db()
    cursor = conn.cursor()
    sql = """
        INSERT INTO text_dataset (
            track_id,
            track_name,
            track_artist,
            lyrics,
            track_popularity,
            track_album_id,
            track_album_name,
            track_album_release_date,
            playlist_name,
            playlist_id,
            playlist_genre,
            playlist_subgenre,
            danceability,
            energy,
            key_,
            loudness,
            mode_,
            speechiness,
            acousticness,
            instrumentalness,
            liveness,
            valence,
            tempo,
            duration_ms,
            language_
        )
        VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s
        )
        ON CONFLICT (track_id) DO NOTHING;
    """

    insertados = 0
    ignorados = 0
    errores = 0
    for i, row in df.iterrows():
        try:
            lyrics = limpiar_texto(row["lyrics"])
            track_id = limpiar_texto(row["track_id"])

            if track_id is None or lyrics is None:
                ignorados += 1
                continue
            cursor.execute(sql, (
                track_id,
                limpiar_texto(row["track_name"]),
                limpiar_texto(row["track_artist"]),
                lyrics,
                limpiar_int(row["track_popularity"]),
                limpiar_texto(row["track_album_id"]),
                limpiar_texto(row["track_album_name"]),
                limpiar_fecha(row["track_album_release_date"]),
                limpiar_texto(row["playlist_name"]),
                limpiar_texto(row["playlist_id"]),
                limpiar_texto(row["playlist_genre"]),
                limpiar_texto(row["playlist_subgenre"]),
                limpiar_float(row["danceability"]),
                limpiar_float(row["energy"]),
                limpiar_int(row["key"]),
                limpiar_float(row["loudness"]),
                limpiar_int(row["mode"]),
                limpiar_float(row["speechiness"]),
                limpiar_float(row["acousticness"]),
                limpiar_float(row["instrumentalness"]),
                limpiar_float(row["liveness"]),
                limpiar_float(row["valence"]),
                limpiar_float(row["tempo"]),
                limpiar_int(row["duration_ms"]),
                limpiar_texto(row["language"])
            ))

            if cursor.rowcount == 1:
                insertados += 1
            else:
                ignorados += 1

            if insertados % 1000 == 0 and insertados > 0:
                conn.commit()
                print(f"Insertados: {insertados}")

        except Exception as e:
            conn.rollback()
            errores += 1
            print(f"Error real en fila {i}: {e}")

    conn.commit()
    cursor.close()
    conn.close()

    print("\nProceso terminado")
    print("Canciones insertadas:", insertados)
    print("Registros ignorados:", ignorados)
    print("Errores:", errores)

importar_textos()