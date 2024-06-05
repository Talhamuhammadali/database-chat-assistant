import json
import logging
import time
import operator
import functools
from typing import (
    Annotated,
    Sequence,
    TypedDict,
    Literal,
    Optional
)
from langchain_core.tools import tool
from langchain import hub
from langchain_community.utilities import SQLDatabase
from langchain.agents import Tool
from langchain.agents import (
    AgentExecutor,
    create_sql_agent,
    create_structured_chat_agent
)
from langchain_core.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_nvidia_trt.llms import TritonTensorRTLLM
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.langchainService.prompts import (
    SUPERVISOR_SYSTEM_PROMPT,
    PLANNER_SYSTEM_PROMPT,
    TOOL_CALLING_PROMPT,
)
from langchain_core.messages import BaseMessage, HumanMessage
from app.langchainService.langchain_util import GenerateQuery, ExecutreQuery
from langgraph.graph import END, StateGraph
from app.utils.db_info import(
    REDMINE_DATABASE,
    REDMINE_EXAMPLES
)
from app.utils.connections import (
    chromadb_connection,
    mysql_connection,
    llms_clients_lang
)
logging.basicConfig(level="INFO")
logger = logging.getLogger("Multi-Agent-Db-Assistant")


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: str


def create_agent(
    llm: ChatGroq,
    tools: list,
    system_prompt: str,
    agent_type: Literal["sql", "chat"],
    db: Optional[SQLDatabase]
):
    """Create an agent."""
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                system_prompt
            ),
            MessagesPlaceholder(variable_name="messages"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ]
    )
    if agent_type == "chat":
        agent = create_structured_chat_agent(llm, tools, prompt)
    else:
        agent = create_sql_agent(llm, db=db, agent_type="openai-tools", verbose=True)
    executor = AgentExecutor(agent=agent, tools=tools)
    return executor

def agent_node(state, agent, name):
    result = agent.invoke(state)
    return {"messages": [HumanMessage(content=result["output"], name=name)]}

def supervisor_chain(llm: ChatGroq, members : list, options : list):
    function_def = {
        "name": "route",
        "description": "Select the next role.",
        "parameters": {
            "title": "routeSchema",
            "type": "object",
            "properties": {
                "next": {
                    "title": "Next",
                    "anyOf": [
                        {"enum": options},
                    ],
                }
            },
            "required": ["next"],
        },
    }
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SUPERVISOR_SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="messages"),
            (
                "system",
                "Given the conversation above, who should act next?"
                " Or should we FINISH? Select one of: {options}",
            ),
        ]
    ).partial(options=str(options), members=", ".join(members))


    supervisor_chain = (
        prompt
        | llm.bind_functions(functions=[function_def], function_call="route")
        | JsonOutputFunctionsParser()
    )
    return supervisor_chain
    
def adaptive_agent(user_question: str, chat_history: list):
    engine = mysql_connection()
    db = SQLDatabase(
       engine=engine,
       include_tables=[*REDMINE_DATABASE.keys()]
    )
    llm = llms_clients_lang()
    members = ["Planner", "SQL Coder"]
    options = ["FINISH"] + members
    logger.info(f"Creating A Cyclic multi agent assistant")
    logger.info("Initializing agents")
    supervisor_agent = supervisor_chain(llm=llm, members=members, options=options)
    sql_agent = create_agent(
        llm=llm,
        tools=[],
        db=db,
        system_prompt=SUPERVISOR_SYSTEM_PROMPT,
        agent_type="sql"
    )
    sql_node = functools.partial(agent_node, agent=sql_agent, name="SQL Coder")
    planner_agent = create_agent(
        llm=llm,
        tools=[],
        db=db,
        system_prompt=SUPERVISOR_SYSTEM_PROMPT,
        agent_type="chat"
    )
    planner_node = functools.partial(agent_node, planner_agent, name= "Planner")
    workflow = StateGraph(AgentState)
    workflow.add_node("Planner", planner_node)
    workflow.add_node("SQL Coder", sql_node)
    workflow.add_node("supervisor", supervisor_agent)
    workflow.set_entry_point("supervisor")
    for member in members:
        workflow.add_edge(member, "supervisor")
    # The supervisor populates the "next" field in the graph state
    # which routes to a node or finishes
    conditional_map = {k: k for k in members}
    conditional_map["FINISH"] = END
    graph = workflow.compile()
    graph.ainvoke(
        {
            "messages": [
                HumanMessage(content="Hi")
            ]
        }
    )
    return 0
   