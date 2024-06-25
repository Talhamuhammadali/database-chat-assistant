from sqlalchemy import text
from langchain_core.output_parsers.string import StrOutputParser
from langchain.schema.runnable import RunnableLambda
from langchain_core.prompts import PromptTemplate
from app.utils.connections import postgres_connection, llms_clients_lang
from app.langchainService.summary_chain.summary_utils import urdu_proper_nouns
from app.langchainService.summary_chain.summary_prompt import CORRECTION_PROMPT
from typing import List

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
    return result_list

def clean_output():
    return 0

def get_summary():
    rows = get_recent_STT()
    rows.reverse()
    text_to_process = ".".join(rows)
    llm = llms_clients_lang()
    prompt = PromptTemplate.from_template(CORRECTION_PROMPT)
    print(prompt.metadata)
    correction_chain = prompt | llm | StrOutputParser()
    corrections = correction_chain.invoke(
        {
            "nouns": urdu_proper_nouns,
            "text": text_to_process
        }
    )
    return corrections