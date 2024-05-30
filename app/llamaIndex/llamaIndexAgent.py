import time
import json
import logging
import phoenix as px
from phoenix.trace import SpanEvaluations
from phoenix.session.evaluation import (
    get_qa_with_reference,
    get_retrieved_documents
)
from llama_index.core.llms import ChatResponse
from llama_index.core import (
    PromptTemplate,
    Settings,
    SQLDatabase,
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    set_global_handler,
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
    SimpleObjectNodeMapping,
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
from app.llamaIndex.db_utils import (
    REDMINE_TABLES,
    EXAMPLES, 
    TEXT_TO_SQL_PROMPT,
    RESPONSE_SYNTHESIS_PROMPT
)

px.launch_app()
set_global_handler("arize_phoenix")

logging.basicConfig(level="INFO")
logger = logging.getLogger("Redmine-Assitant")
logger.setLevel(logging.INFO)

def llms_clients():
    api_key="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"
    chat_llm = Groq(model="llama3-8b-8192",
    api_key=api_key,
    temperature=0.3
    )
    #triton_url = "localhost:8001"
    #model_name = "ensemble"
    #chat_llm = NvidiaTriton(server_url=triton_url, model_name=model_name)
    sql_llm = ""
    embediing_model = HuggingFaceEmbedding(model_name='intfloat/e5-base-v2')
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
        table = SQLTableSchema(table_name=table_name)
        table.context_str = REDMINE_TABLES[table_name]["description"]
        table_schema_objs.append(table)
        
    db_index = ObjectIndex.from_objects(
        table_schema_objs,
        table_node_mapping,
        VectorStoreIndex,
        storage_context
    )
    db_retriever = db_index.as_retriever(similarity_top_k=top_k)
    return db_retriever

def get_context_string(table_data: List[SQLTableSchema]):
    """Get table context string."""
    context_strs = []
    for table_schema_obj in table_data:
        table_info = REDMINE_TABLES[table_schema_obj.table_name]
        description = json.dumps(table_info)
        context_str = f"Table and column description for table '{table_schema_obj.table_name}':\n {description}"  
        context_strs.append(context_str)
    return "\n\n".join(context_strs)

def retrieve_examples(query: str):
    chroma_collection = chromadb_connection(collection="sql_examples")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    node_mappings = SimpleObjectNodeMapping.from_objects(EXAMPLES)
    obj_idx = ObjectIndex.from_objects(
        EXAMPLES,
        node_mappings,
        VectorStoreIndex,
        storage_context
    )
    retriever = obj_idx.as_retriever(similarity_top_k=1)
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

def sql_parser(response: ChatResponse):
    """Parse response to SQL."""
    response = response.message.content
    check = "select no;"
    sql_query_start = response.find("SQLQuery:")
    if sql_query_start != -1:
        response = response[sql_query_start:]
        if response.startswith("SQLQuery:"):
            response = response[len("SQLQuery:") :]
    sql_result_start = response.find("SQLResult:")
    if sql_result_start != -1:
        response = response[:sql_result_start]
    if response.lower().strip().strip("```").strip() == check:
        return "SELECT * FROM rx_statistics_charts;"
    return response.strip().strip("```").strip()

def ask(query: str):
    chat_llm, _ = llms_clients()
    engine = mysql_connection()
    metadata_obj = MetaData()
    sql_database = SQLDatabase(engine)
    tables = [*REDMINE_TABLES.keys()]
    metadata_obj.reflect(bind=engine, only=tables)
    start_time = time.time()
    # Initializing pipline components 
    db_retriever = set_up_database_retriever(
        sql_database=sql_database,
        metadata_obj=metadata_obj,
        top_k=5
    )
    sql_template = PromptTemplate(TEXT_TO_SQL_PROMPT)
    table_parser_component = FnComponent(fn=get_context_string)
    ex_retriever = FnComponent(fn=retrieve_examples)
    extract_sql_query = FnComponent(fn=sql_parser)
    sql_retriever = SQLRetriever(sql_database)
    response_prompt = PromptTemplate(RESPONSE_SYNTHESIS_PROMPT)
    response_prompt = response_prompt.partial_format(
        query_str=query,
        
    )
    time_taken = time.time() - start_time
    logger.info(f"time taken to process db tables:{time_taken}s")
    
    # Creating Sql pipeline
    start_time = time.time()

    text2sql_prompt = sql_template.partial_format(
    dialect=engine.dialect.name
    )
    qp = QP(
        modules={
            "input": InputComponent(),
            "table_retriever": db_retriever,
            "examples": ex_retriever,
            "table_output_parser": table_parser_component,
            "text2sql_prompt": text2sql_prompt,
            "text2sql_llm": chat_llm,
            "extract_sql_query": extract_sql_query,
            "sql_retriever": sql_retriever,
            "response_prompt": response_prompt,
            "final_response_llm": chat_llm,
        },
        verbose=True,
    )
    qp.add_chain(["input", "table_retriever", "table_output_parser"])
    qp.add_chain(["input", "examples"])
    qp.add_link("input", "text2sql_prompt", dest_key="query_str")
    qp.add_link("table_output_parser", "text2sql_prompt", dest_key="schema")
    qp.add_link("examples", "text2sql_prompt", dest_key="examples")
    qp.add_chain(["text2sql_prompt", "text2sql_llm", "extract_sql_query", "sql_retriever"])
    qp.add_link("sql_retriever", "response_prompt", dest_key="context_str")
    qp.add_link("extract_sql_query", "response_prompt", dest_key="sql_query")
    qp.add_chain(["response_prompt", "final_response_llm"])
    
    response = qp.run(query=query) 
    # replace chat_llm with sql query llm to get better 
    # query_engine = SQLTableRetrieverQueryEngine(
    #     sql_database=sql_database,
    #     table_retriever=db_retriever,
    #     llm=chat_llm,
    #     synthesize_response=True,
    # )
    # response = query_engine.query(query)
    time_taken = time.time() - start_time
    logger.info(f"time taken to respond:{time_taken}s")
    logger.info(response)
    df = get_qa_with_reference(px.active_session()) 
    # hallucination_eval, qa_correctness_eval = evaluation(queries_df=df, llm=chat_llm)
    # px.Client().log_evaluations(
    #     SpanEvaluations(eval_name="Hallucination", dataframe=hallucination_eval),
    #     SpanEvaluations(eval_name="QA Correctness", dataframe=qa_correctness_eval),
    # )
    logger.info(f"Check traces here:{px.active_session().url}")
    return response

