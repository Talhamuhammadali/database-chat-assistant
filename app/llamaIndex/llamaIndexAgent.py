from pprint import pprint
from llama_index.core.prompts.default_prompts import DEFAULT_TEXT_TO_SQL_PROMPT
from llama_index.core import PromptTemplate
from llama_index.core.llms import ChatResponse
from llama_index.core import Settings
from llama_index.core import SQLDatabase, VectorStoreIndex
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.llms.groq import Groq
from llama_index.llms.nvidia_triton import NvidiaTriton
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.retrievers import SQLRetriever
from typing import List
from llama_index.core.query_pipeline import (
    QueryPipeline as QP,
    Link,
    InputComponent,
    CustomQueryComponent,
    FnComponent
)
from llama_index.core.objects import (
    SQLTableNodeMapping,
    ObjectIndex,
    SQLTableSchema,
)
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    String,
    Integer,
    inspect,
    select,
    column,
)

def llms_clients():
    api_key="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"
    chat_llm = Groq(model="llama3-8b-8192",
    api_key=api_key,
    temperature=0.5
    )
    sql_llm = ""
    embediing_model = HuggingFaceEmbedding(model_name='thenlper/gte-base')
    Settings.embed_model=embediing_model
    return chat_llm, sql_llm

def sql_connection():
    engine = create_engine("sqlite:///mydatabase.db", future=True)
    metadata_obj = MetaData()
    table_name = "city_stats"
    try:
        city_stats_table = Table(
        table_name,
        metadata_obj,
        Column("city_name", String(16), primary_key=True),
        Column("population", Integer),
        Column("country", String(16), nullable=False),
        )
    except Exception as ex:
        print(f"Error: {ex}")
    metadata_obj.create_all(engine)
    return engine, metadata_obj

if __name__ == "__main__":
    chat_llm, _ = llms_clients()
    # response = chat_llm.complete("hi")
    # print(response)
    engine, metadata_obj = sql_connection()
    table = metadata_obj.tables["city_stats"].columns
    print(table)
    