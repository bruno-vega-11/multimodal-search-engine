import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    host = os.getenv("PGHOST", "localhost")
    port = os.getenv("PGPORT", "5433")
    dbname = os.getenv("PGDATABASE", "sistema_multimodal")
    user = os.getenv("PGUSER", "postgres")
    password = os.getenv("PGPASSWORD", "123456")
    dsn = ( f"host={host} port={port} dbname={dbname} " f"user={user} password={password}")
    return psycopg.connect(dsn)

def get_dict_cursor(conn):
    return conn.cursor(row_factory=dict_row)
