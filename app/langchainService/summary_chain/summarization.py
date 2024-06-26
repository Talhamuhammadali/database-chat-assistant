import logging
from sqlalchemy import text
from langchain_core.output_parsers.string import StrOutputParser
from langchain.schema.runnable import RunnableLambda
from langchain_core.prompts import PromptTemplate
from app.utils.connections import postgres_connection, llms_clients_lang
from app.langchainService.summary_chain.summary_utils import urdu_proper_nouns, urdu_adjectives
from app.langchainService.summary_chain.summary_prompt import (
    CORRECTION_PROMPT,
    TOPIC_SUMMARIZATION_PROMPT,
    TRANSLATION_PROMPT
)
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
    DESC Limit 5;"""
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

def clean_output():
    string = """Respond in the following format:
    Corrected Text:
    Text goes here"""
    return 0

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

def get_summary(model: str = ""):
    if model:
        llm = llms_clients_lang(model=model)
    text_to_process = get_recent_STT()
    prompt = PromptTemplate.from_template(TOPIC_SUMMARIZATION_PROMPT)
    topic_summarization_chain = prompt | llm | StrOutputParser()
    topic_summarization = topic_summarization_chain.invoke(
        {
            "urdu": text_to_process
        }
    )
    trans_prompt = PromptTemplate.from_template(TRANSLATION_PROMPT)
    trans_chain = trans_prompt | llm | StrOutputParser()
    translation = trans_chain.invoke(
        {
            "urdu": text_to_process
        }
    )
    return topic_summarization