import json
import re
import logging
import operator
import time
import functools
from typing import (
    Annotated,
    Sequence,
    TypedDict,
    Literal,
    Optional,
    Union
)
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_community.utilities import SQLDatabase
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain_nvidia_trt.llms import TritonTensorRTLLM
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.langchainService.prompts import (
    ASSISTANT_SYSTEM_PROMPT,
    ASSISTANT_PROMPT,
    SUPERVISOR_SYSTEM_PROMPT,
    SUPERVISOR_PROMPT,
    PLANNER_SYSTEM_PROMPT,
    PLANNER_GENERATION_PROMPT,
    SQL_SYSTEM_PROMPT,
    SQL_GENERATION_PROMPT
)
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
    ToolMessage
)
from langgraph.graph import END, StateGraph
from langgraph.graph.message import AnyMessage, add_messages
from app.utils.db_info import(
    REDMINE_DATABASE,
    REDMINE_EXAMPLES
)
from app.utils.connections import (
    chromadb_connection,
    mysql_connection,
    llms_clients_lang
)
from app.langchainService.database_retriver import get_table_context


logging.basicConfig(level="INFO")
logger = logging.getLogger("Multi-Agent-Db-Assistant")
llm = llms_clients_lang()

class AgentState(TypedDict):
    task: str
    strategy: str
    sql_queries: list[str]
    evaluation: str
    max_revision: int
    revision_number: int
    messages: Annotated[Sequence[AnyMessage], operator.add]    
    step: str
    

def assistant_node(state: AgentState):
    prompt = ASSISTANT_PROMPT.format(question=state["task"])
    system = SystemMessage(content=ASSISTANT_SYSTEM_PROMPT)
    user = HumanMessage(content=prompt)
    messages = [system, user]
    response = llm.invoke(messages)
    print(response)
    return {
        "step": response.content
    }

def supervisor_node(state: AgentState):
    members = ["planner", "sql coder", "evaluator"]
    options = ["FINISH"] + members
    prompt = SUPERVISOR_PROMPT.format(
        options=options,
        status = state["step"] or "plan"
    )
    system = SystemMessage(
        content=SUPERVISOR_SYSTEM_PROMPT.format(members=members)
    )
    user = HumanMessage(content=prompt)
    
    messages = [system, user]
    response = llm.invoke(messages)
    print(response)
    return {
        "step": response.content
    }

def planner_node(state: AgentState):
    engine = mysql_connection()
    db = SQLDatabase(
       engine=engine,
       include_tables=[*REDMINE_DATABASE.keys()]
    )
    logger.info(db.get_usable_table_names())
    return {
        "step": "sql coder",
        "strategy" : "This isnt possible"
    }

def sql_node(state: AgentState):
    return 0

def evaluator_node(state: AgentState):
    return 0

def condition_check(state: AgentState):
    if state["step"] == "supervisor":
        return "supervisor"
    if state["step"] == "planner":
        return "planner"
    if state["step"] == "sql coder":
        return "sql coder"
    if state["step"] == "evaluator":
        return "evaluator"
    if state["step"] == "FINISH":
        return "FINISH"

def adaptive_agent(user_question: str, chat_history: list):
    memory = SqliteSaver.from_conn_string(":memory:")
    builder = StateGraph(AgentState)
    logger.info(f"Creating A Cyclic multi agent assistant")
    logger.info("Initializing agents")
    
    builder.add_node("assistant", assistant_node)
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("planner", planner_node)
    # builder.add_node("sql coder", sql_node)
    # builder.add_node("evaluator", evaluator_node)
    builder.add_conditional_edges(
        "assistant",
        condition_check,
        {"FINISH": END, "supervisor": "supervisor"}
    )
    builder.add_conditional_edges(
        "supervisor",
        condition_check,
        {
            "FINISH": "assistant",
            "planner": "planner",
            "sql coder": "sql coder",
            "evaluator": "evaluator"
        }
    )
    builder.add_edge("planner","supervisor")
    # builder.add_edge("assistant", "generate")
    builder.set_entry_point("assistant")
    graph = builder.compile(checkpointer=memory)
    # creating conversation thread
    thread_config = {"configurable": {"thread_id": "1"}}
    for s in graph.stream(
        {
            "task": user_question,
            "max_revisions": 1,
            "revision_number": 0
        }
    , thread_config):
        print(s)
    return 0
   