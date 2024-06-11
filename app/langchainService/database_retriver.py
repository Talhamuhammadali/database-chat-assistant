import logging
from langchain_community.utilities import SQLDatabase
from app.utils.connections import (
    chromadb_connection,
    mysql_connection
)
from app.utils.db_info import(
    REDMINE_DATABASE,
    REDMINE_EXAMPLES
)
from sqlalchemy import MetaData

logging.basicConfig(level="INFO")
logger = logging.getLogger("langchain database retriever")

def test_retrival():
    engine = mysql_connection()
    db = SQLDatabase(
       engine=engine,
       metadata=MetaData(),
       include_tables=[*REDMINE_DATABASE.keys()]
    )
    metadata_obj = MetaData()
    sql_database = SQLDatabase(engine)
    tables = [*REDMINE_DATABASE.keys()]
    metadata_obj.reflect(bind=engine, only=tables)
    context = db.get_context()
    table_info = db.get_table_info()
    # logger.info(db.get_table_info())
    # logger.info(db.get_usable_table_names())
    return {"context": context, "table_info": db._schema}
