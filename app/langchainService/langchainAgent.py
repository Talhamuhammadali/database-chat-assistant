import logging
from langchain_community.llms.vllm import VLLM
logging.basicConfig(level="INFO")
logger = logging.getLogger("langchain_service")

chat_llm = VLLM(
    model="lama3_chat_instruct"
)
sql_llm = VLLM(
    model="phi_2_finetuined"
)
def test():
    logger.info("Testing langchain")
    response = chat_llm.invoke("hi")
    print(response)
    return response