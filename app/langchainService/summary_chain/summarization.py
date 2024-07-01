import requests
import logging
import time
from sqlalchemy import text
from langchain_core.output_parsers.string import StrOutputParser
from langchain.schema.runnable import RunnableLambda
from langchain_core.prompts import PromptTemplate
from app.utils.connections import postgres_connection, llms_clients_lang
from app.langchainService.summary_chain.summary_utils import urdu_proper_nouns, urdu_adjectives
from app.langchainService.summary_chain.summary_prompt import (
    CORRECTION_PROMPT,
    TOPIC_SUMMARIZATION_PROMPT
)
from app.utils.settings import TRANSLATION_URL
from typing import List

logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)
llm = llms_clients_lang(model="llama3-8b-8192")


def get_recent_STT():
    engine = postgres_connection()
    query = """SELECT
        transcription_urdu
    FROM
        whisper_app_speech_to_text_database
    ORDER BY 
        created_date
    DESC Limit 3;"""
    result = ""
    try:
        with engine.connect() as connection:
            result = connection.execute(text(query))
            result_list = [str(value) for row in result.fetchall() for value in row]
            print("PostgresSQL Database results:", result_list)
    except Exception as ex:
        print("Error Couldnt get:\n", ex)
    
    result_list.reverse()
    text_to_process = ".".join(result_list)
    return text_to_process

def get_correction():
    text_to_process = get_recent_STT()
    prompt = PromptTemplate.from_template(CORRECTION_PROMPT)

    correction_chain = prompt | llm | StrOutputParser()
    corrections = correction_chain.invoke(
        {
            "nouns": urdu_proper_nouns,
            "text": text_to_process
        }
    )
    return corrections

def get_summary(docs: List[str], model: str = ""):
    if model:
        llm = llms_clients_lang(model=model)
    # text_to_process = get_recent_STT()
    docs.reverse()
    text_to_process = "\nnext transcript\n".join(docs)
    prompt = PromptTemplate.from_template(TOPIC_SUMMARIZATION_PROMPT)
    topic_summarization_chain = prompt | llm | StrOutputParser()
    topic_summarization = topic_summarization_chain.invoke(
        {
            "urdu": text_to_process
        }
    )
    payload ={
        'text': topic_summarization
    }
    url = TRANSLATION_URL+"/translate"
    data = {}
    start_time = time.time()
    try:
        response = requests.post(url=url, json=payload)
        data = response.json()
    except Exception as ex:
        logger.info(f"Error: {ex}")
    end_time = time.time()
    time_taken = end_time - start_time
    logger.info(f"Time taken for translation: {time_taken}")
    logger.info(f"\n\n{data}")
    transation = data.get("translated_text", "")
    return {
        "topic_summaries":  topic_summarization,
        "urdu_translation": transation
    }