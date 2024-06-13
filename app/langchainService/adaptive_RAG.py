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
from langchain_core.pydantic_v1 import Field
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
    SQL_GENERATION_PROMPT,
    EVALUATION_SYSTEM_PROMPT,
    EVALUATION_PROMPT
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
from app.utils.connections import llms_clients_lang
from app.langchainService.database_retriver import get_table_context, execute_query


logging.basicConfig(level="INFO")
logger = logging.getLogger("Multi-Agent-Db-Assistant")
llm = llms_clients_lang()

class AgentState(TypedDict):
    task: str = Field(description="Task that requires sql query")
    strategy: str = Field(description="Strategy required to construct an SQL query.")
    sql_query: str = Field(description="SQL query that can achive the task")
    evaluation: str = Field(description="Evaluating the sql queries based on task and data retrieved")
    max_revisions: int = Field(description="Max revisions possible")
    revision_number: int = Field(description="Current Revision")
    dialect: str = Field(description="Name of the SQL dialect to query from")
    table_info: str = Field(description="Relevant tables information: create table, sample rows, descriptions")
    examples: str = Field(description="Relevant examples")
    messages: Annotated[Sequence[AnyMessage], operator.add] = Field(description="TODO")
    step: str = Field(description="Current step the SQL process is on")
    

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
    return {
        "step": response.content
    }

def planner_node(state: AgentState):
    logger.info("Planning phase for the query")
    context = get_table_context(query=state["task"])
    system = SystemMessage(
        content=PLANNER_SYSTEM_PROMPT
    )
    user = HumanMessage(
        content=PLANNER_GENERATION_PROMPT.format(
            table_info=context.get("table_info", ""),
            examples=context.get("examples", ""),
            task=state["task"]
        )
    )
    messages = [system, user]
    response = llm.invoke(messages)
    return {
        "step": "planning completed",
        "table_info": context.get("table_context", ""),
        "examples": context.get("examples", ""),
        "strategy" : response.content,
        "dialect": context.get("dialect", "")
    }

def sql_node(state: AgentState):
    logger.info("Generating the SQL query")
    system = SystemMessage(content = SQL_SYSTEM_PROMPT)
    user = HumanMessage(
        content=SQL_GENERATION_PROMPT.format(
            dialect=state["dialect"],
            table_info=state["table_info"],
            strategy=state["strategy"],
            # examples=state["examples"],
            task=state["task"],
        )
    )
    messages = [system, user]
    response = llm.invoke(messages)
    content = response.content
    if content:
        sql_query_start = content.find("SQLQuery:")
        if sql_query_start != -1:
            sql = content[sql_query_start:]
            if sql.startswith("SQLQuery:"):
                sql = sql[len("SQLQuery:") :]
        sql_result_start = sql.find("SQLResult:")
        if sql_result_start != -1:
            sql = sql[:sql_result_start]
            sql = sql.replace("```", "").strip()
            
    return {
        "sql_query": sql
    }

def evaluator_node(state: AgentState):
    rows = execute_query(sql_query=state["sql_query"])
    system = SystemMessage(content=EVALUATION_SYSTEM_PROMPT)
    user = HumanMessage(
        content=EVALUATION_PROMPT.format(
            task=state["task"],
            sql=state["sql_query"],
            rows=rows,
        )
    )
    messages = [system, user]
    evaluation = llm.invoke(messages)
    return {
        "evaluation": evaluation.content,
        "revision_number": state.get('revision_number', 0)+1
    }

def condition_check(state: AgentState):
    if state["step"] == "supervisor":
        return "supervisor"
    if state["step"] == "planner":
        return "planner"
    if state["step"] == "sql":
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
    builder.add_node("sql coder", sql_node)
    builder.add_node("evaluator", evaluator_node)
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
    builder.add_edge("sql coder","supervisor")
    builder.add_edge("evaluator","supervisor")
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
   