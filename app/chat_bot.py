import json
import logging
import time
from langchain import hub
from langchain.agents import Tool
from langchain.agents import (
    AgentExecutor,
    create_structured_chat_agent,
    create_react_agent
)
from langchain_nvidia_trt.llms import TritonTensorRTLLM
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from app.langchainService.langchain_util import GetInfo
from app.utils.connections import llms_clients_lang
from app.llamaIndex.llamaIndexAgent import ask
from app.utils.chat_bot_utils import SYSTEM_PROMPT

logging.basicConfig(level="INFO")
logger = logging.getLogger("Chat Bot")

def agent_test(user_question: str):
    chat_llm = llms_clients_lang()
    get_context = Tool(
        name="get_context",
        func=ask,
        description="Based on question, this will ",
        args_schema=GetInfo
    )
    tools_list = [get_context]
    print(tools_list)
    tool_names = ["get_context"]
    prompt = PromptTemplate.from_template(SYSTEM_PROMPT)

    logger.info(type(prompt))
    agent = create_react_agent(
        llm=chat_llm,
        tools=tools_list,
        prompt=prompt,
    )
    logger.info("inititalizing retrival process")
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools_list,
        verbose=True,
        handle_parsing_errors=True
    )
    response = agent_executor(
        {
            "input": user_question,
            "agent_scratchpad": [],
            "chat_history": []
        }
    )
    logger.info(response)
    return response
    
def ask_lang(query: str):
    start_time = time.time()
    agent_test(user_question=query)
    end_time = time.time()
    time_taken = end_time - start_time
    logger.info(f"Assistant took {time_taken}s to respond")