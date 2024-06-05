import json
import logging
import time
from langchain import hub
from langchain_community.utilities import SQLDatabase
from langchain.agents import Tool
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_nvidia_trt.llms import TritonTensorRTLLM
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.langchainService.prompts import (
    SYSTEM_PROMPT,
    FIRST_STEP_PROMPT,
    TOOL_CALLING_PROMPT,
    REDMINE_TABLES
)
from app.langchainService.langchain_util import(
    GenerateQuery,
    ExecutreQuery
)
from langgraph.graph import END, StateGraph
from app.utils.connections import (
    chromadb_connection,
    mysql_connection,
    llms_clients_lang
)
logging.basicConfig(level="INFO")
logger = logging.getLogger("Multi-Agent-Db-Assistant")


def create_agent(llm: ChatGroq, tools, system_message: str):
    """Create an agent."""
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful AI assistant, collaborating with other assistants."
                " Use the provided tools to progress towards answering the question."
                " If you are unable to fully answer, that's OK, another assistant with different tools "
                " will help where you left off. Execute what you can to make progress."
                " If you or any of the other assistants have the final answer or deliverable,"
                " prefix your response with FINAL ANSWER so the team knows to stop."
                " You have access to the following tools: {tool_names}.\n{system_message}",
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    prompt = prompt.partial(system_message=system_message)
    prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
    return prompt | llm.bind_tools(tools)

def adaptive_agent():
   engine = mysql_connection()
   db = SQLDatabase(
       engine=engine,
       include_tables=[*REDMINE_TABLES.keys()]
    )
   llm = llms_clients_lang()
   logger.info(f"{engine} {db.get_table_names()}")
   