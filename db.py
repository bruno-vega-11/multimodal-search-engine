import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

# Carga un .env si existe (no falla si no existe).
load_dotenv()

def get_connection():
    """
    Crea y retorna una nueva conexion a Postgres usando
    variables de entorno. Cada llamada abre una conexion nueva;
    para scripts batch (carga, busqueda) basta con una sola
    conexion reutilizada durante todo el proceso.
    """
    host = os.getenv("PGHOST", "localhost")
    port = os.getenv("PGPORT", "5433")
    dbname = os.getenv("PGDATABASE", "sistema_multimodal")
    user = os.getenv("PGUSER", "postgres")
    password = os.getenv("PGPASSWORD", "123456")
    dsn = ( f"host={host} port={port} dbname={dbname} " f"user={user} password={password}")
    return psycopg.connect(dsn)

def get_dict_cursor(conn):
    """
    Cursor que retorna filas como dict (en vez de tuplas
    posicionales).
    En psycopg v3 esto se logra con row_factory=dict_row al
    crear el cursor, no con un cursor_factory en la conexion
    (que es como se hacia en psycopg2).
    """
    return conn.cursor(row_factory=dict_row)