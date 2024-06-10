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
from langchain_core.tools import tool
from langchain import hub
from langchain_community.utilities import SQLDatabase
from langchain.agents import (
    AgentExecutor,
    create_sql_agent,
    create_structured_chat_agent,
    create_tool_calling_agent,
    Tool,
)
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_nvidia_trt.llms import TritonTensorRTLLM
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.langchainService.prompts import (
    SUPERVISOR_SYSTEM_PROMPT,
    PLANNER_SYSTEM_PROMPT,
    PLANNER_GENERATION_PROMPT,
    SQL_SYSTEM_PROMPT,
    SQL_GENERATION_PROMPT
)
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    AIMessage,
    SystemMessage
)
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
    input: str
    chat_history: Annotated[Sequence[BaseMessage], operator.add]
    agent_outcome: Union[AgentAction, AgentFinish, None]
    messages: Annotated[list[tuple[AgentAction, str]], operator.add]
    next: str
    

class Agent:
    def __init__(self, llm, tools=[], system=""):
        self.llm = llm
        self.system = system
        graph = StateGraph(AgentState)
        graph.add_node("llm", self.ask_llm)
        graph.add_node("action", self.take_actions)
        graph.add_conditional_edges(
            "llm",
            self.check_tool_calls,
            {True: "action", False: END}
        )
        graph.add_edge("action", "llm")
        graph.set_entry_point("llm")
        self.graph = graph.compile()
        self.tools = {t.name: t for t in tools}
        self.model = llm.bind_tools(tools)
    
    def check_tool_calls(self, state: AgentState):
        last_message = state["messages"][-1]
        action_re = re.compile('^Action: (\w+): (.*)$') 
        actions = [
            action_re.match(action) for action in
            last_message.split("\n") if action_re.match(action)
        ]
        if actions:
            return True
        else:
            return False
        
    def take_actions(self, state: AgentState):
        return 0 
    
    def ask_llm(self, state: AgentState):
        messages = state["chat_history"]
        if self.system:
            messages = [
                SystemMessage(
                    content=self.system
                )
            ] + messages
        response = self.llm.invoke(messages)
        return {"chat_history": response}

def adaptive_agent(user_question: str, chat_history: list):
    engine = mysql_connection()
    db = SQLDatabase(
       engine=engine,
       include_tables=[*REDMINE_DATABASE.keys()]
    )
    llm = llms_clients_lang()
    members = ["Planner", "SQL Coder", "Evaluator"]
    options = ["FINISH"] + members
    logger.info(f"Creating A Cyclic multi agent assistant")
    logger.info("Initializing agents")
    supervisor = Agent(
        llm=llm,
        system=SUPERVISOR_SYSTEM_PROMPT,
        tools=[]
    )
    messages = [HumanMessage(content="Hi")]
    result = supervisor.graph.invoke({"input": "hi"})
    logger.info(result)
    return 0
   