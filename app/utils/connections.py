import chromadb
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from pydantic import PostgresDsn
import psycopg2
from app.utils.settings import (
    POSTGRES_HOST,
    POSTGRES_DATABASE,
    POSTGRES_USER,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
)
from app.utils.settings import (
    MYSQL_USER,
    MYSQL_PASS,
    MYSQL_HOST,
    MYSQL_PORT,
    MYSQL_DB,
)

def chromadb_connection(collection: str):
    db = chromadb.PersistentClient("./chromadb")
    chroma_collection = db.get_or_create_collection(collection)
    return chroma_collection

def mysql_connection():
    connection_string = f"mysql://{MYSQL_USER}:{MYSQL_PASS}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    engine = create_engine(connection_string)
    return engine

def sqlite_connection():
    # connection_string = f"mysql://{SQLITE_USER}:{SQLITE_PASS}@{SQLITE_HOST}:{SQLITE_PORT}/{SQLITE_DB}"
    # engine = create_engine(connection_string, future=True)
    engine = create_engine("sqlite:///mydatabase.db", future=True)
    return engine 