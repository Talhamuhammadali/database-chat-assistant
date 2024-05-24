import time
import phoenix as px
from pprint import pprint
from phoenix.trace import SpanEvaluations
from phoenix.session.evaluation import (
    get_qa_with_reference,
    get_retrieved_documents
)
from llama_index.core.prompts.default_prompts import DEFAULT_TEXT_TO_SQL_PROMPT
from llama_index.core.llms import ChatResponse
from llama_index.core import (
    PromptTemplate,
    Settings,
    SQLDatabase,
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    set_global_handler
)
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.query_engine import NLSQLTableQueryEngine, SQLTableRetrieverQueryEngine
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
    MetaData
)
from app.llamaIndex.eval_query import evaluation
from app.utils.connections import (
    chromadb_connection,
    mysql_connection
)
from app.llamaIndex.db_utils import redmine_tables


px.launch_app()
set_global_handler("arize_phoenix")


def llms_clients():
    #api_key="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"
    #chat_llm = Groq(model="llama3-8b-8192",
    #api_key=api_key,
    #temperature=0.5
    #)
    triton_url = "localhost:8001"
    model_name = "ensemble"
    chat_llm = NvidiaTriton(server_url=triton_url, model_name=model_name)
    sql_llm = ""
    embediing_model = HuggingFaceEmbedding(model_name='all-MiniLM-L6-v2')
    Settings.embed_model=embediing_model
    return chat_llm, sql_llm

def set_up_database_retriever(sql_database: SQLDatabase, metadata_obj: MetaData, top_k: int):
    # creating a vector store
    chroma_collection = chromadb_connection(collection="sql_tables")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    # Creating index for each table in database
    table_node_mapping = SQLTableNodeMapping(sql_database)
    table_schema_objs = []
    for table_name in metadata_obj.tables.keys():
        table_schema_objs.append(SQLTableSchema(table_name=table_name))
    db_index = ObjectIndex.from_objects(
        table_schema_objs,
        table_node_mapping,
        VectorStoreIndex,
        storage_context
    )
    db_retriever = db_index.as_retriever(similarity_top_k=top_k)
    
    return db_retriever


def ask(query: str):
    chat_llm, _ = llms_clients()
    # response = chat_llm.complete("hi")
    # print(response)
    engine = mysql_connection()
    metadata_obj = MetaData()
    sql_database = SQLDatabase(engine)
    tables = [*redmine_tables.keys()]
    print(tables)
    metadata_obj.reflect(bind=engine, only=tables)
    start_time = time.time()
    db_retriever = set_up_database_retriever(
        sql_database=sql_database,
        metadata_obj=metadata_obj,
        top_k=3
    )
    time_taken = time.time() - start_time
    print(f"time taken to process db tables:{time_taken}s")
    start_time = time.time()
    # replace chat_llm with sql query llm to get better 
    query_engine = SQLTableRetrieverQueryEngine(
        sql_database=sql_database,
        table_retriever=db_retriever,
        llm=chat_llm,
        synthesize_response=True
    )
    response = query_engine.query(query)
    time_taken = time.time() - start_time
    print(f"time taken to respond:{time_taken}s")
    df = get_qa_with_reference(px.active_session()) 
    # hallucination_eval, qa_correctness_eval = evaluation(queries_df=df, llm=chat_llm)
    # px.Client().log_evaluations(
    #     SpanEvaluations(eval_name="Hallucination", dataframe=hallucination_eval),
    #     SpanEvaluations(eval_name="QA Correctness", dataframe=qa_correctness_eval),
    # )
    print(f"Check traces here:{px.active_session().url}")
    return response
    # print(response.metadata)