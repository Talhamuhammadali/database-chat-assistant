import logging
import json
from typing import List
from langchain_community.utilities import SQLDatabase as Lang_db
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import (
    SQLDatabase as Llama_db,
    StorageContext,
    VectorStoreIndex,
    Settings
)
from llama_index.core.objects import (
    SQLTableNodeMapping,
    ObjectIndex,
    SQLTableSchema,
    SimpleObjectNodeMapping
)
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

def set_up_database_retriever(sql_database: Llama_db, metadata_obj: MetaData, top_k: int):
    # creating a vector store
    chroma_collection = chromadb_connection(collection="sql_tables")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    # Creating index for each table in database
    logger.info("Selecting appropriate tables")
    table_node_mapping = SQLTableNodeMapping(sql_database)
    table_schema_objs = []
    for table_name in metadata_obj.tables.keys():
        table = SQLTableSchema(table_name=table_name)
        table.context_str = REDMINE_DATABASE[table_name]["description"]
        table_schema_objs.append(table)
    db_index = ObjectIndex.from_objects(
        table_schema_objs,
        table_node_mapping,
        VectorStoreIndex,
        storage_context,
    )
    db_retriever = db_index.as_retriever(similarity_top_k=top_k)
    return db_retriever

def get_context_string(llama_db: Llama_db, table_data: List[SQLTableSchema]):
    context_strs = []
    for table_schema_obj in table_data:
        table_info = llama_db.get_single_table_info(
            table_schema_obj.table_name
        )
        sample_rows = llama_db.run_sql(f"select * from {table_schema_obj.table_name} limit 3")
        logger.info(sample_rows)
        additional_info = REDMINE_DATABASE[table_schema_obj.table_name]
        table_desc = additional_info["description"]
        important_columns = json.dumps(additional_info["important_columns"], indent=2)
        schema = json.dumps(table_info, indent=4)
        context_str = f"{schema}\n\n"  
        context_str += f"Table description for table '{table_schema_obj.table_name}':\n{table_desc}\n\n"
        context_str += f"Some important columns and descriptions for table '{table_schema_obj.table_name}':\n{important_columns}\n"
        context_str += f"Sample rows:\n\n{sample_rows}"
        context_strs.append(context_str)
    return "\n\n".join(context_strs)

def retrieve_examples(query: str, top_k: int = 3):
    chroma_collection = chromadb_connection(collection="sql_examples")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    node_mappings = SimpleObjectNodeMapping.from_objects(REDMINE_EXAMPLES)
    obj_idx = ObjectIndex.from_objects(
        REDMINE_EXAMPLES,
        node_mappings,
        VectorStoreIndex,
        storage_context
    )
    retriever = obj_idx.as_retriever(similarity_top_k=top_k)
    relavent_examples = retriever.retrieve(query)
    template = """Example Question: {question}\n
SQL Query:
    {sql_query}"""
    relavent_examples = [
        template.format(
            question=example["query"],
            sql_query=example["passage"]
        )
        for example in relavent_examples
    ]
    
    str_examples = "\n\n".join(relavent_examples)
    return str_examples

def get_table_context(query: str):
    embediing_model = HuggingFaceEmbedding(model_name='intfloat/e5-base-v2')
    Settings.embed_model=embediing_model
    engine = mysql_connection()
    tables = [*REDMINE_DATABASE.keys()]
    logger.info("Getting examples and table context")
    lang_db = Lang_db(
       engine=engine,
       include_tables=tables
    )
    llama_db = Llama_db(engine)
    metadata_obj = MetaData()
    metadata_obj.reflect(bind=engine, only=tables)
    db_retriever = set_up_database_retriever(
        sql_database=llama_db, 
        top_k=5,
        metadata_obj=metadata_obj
    )
    selected_tables = db_retriever.retrieve(query)
    table_context = get_context_string(
        llama_db=llama_db,
        table_data=selected_tables
    )
    examples_str = retrieve_examples(query=query, top_k=3)
    return {"table_context":table_context, "examples": examples_str}
