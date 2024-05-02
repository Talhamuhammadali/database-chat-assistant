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
    POSTGRES_PORT
)
# postgres_dsn = str(PostgresDsn.build(
#     scheme="postgresql",
#     username=POSTGRES_USER,
#     password=POSTGRES_PASSWORD,
#     host=POSTGRES_HOST,
#     port=POSTGRES_PORT,
#     path=POSTGRES_DATABASE,
# ))
# print(postgres_dsn)
# engine = create_engine(postgres_dsn, pool_pre_ping=True)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = psycopg2.connect(
    user="ummar",
    password="ticker1234",
    host="",
    port="5432",
    database="speech-to-text"
)

def get_db():
    try:
        yield db
    finally:
        db.close()


def check_database_connection():
    try:
        session = next(get_db())
        query_result = session.execute(text("SELECT schema_name FROM information_schema.schemata;"))
        schemas = [row[0] for row in query_result.fetchall()]
        print("Connected to database. Available schemas:", schemas)
        return True
    except Exception as e:
        print("Error connecting to database:", e)
        return False