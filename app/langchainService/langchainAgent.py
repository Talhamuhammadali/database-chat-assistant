import logging
from langchain_community.llms.vllm import VLLM
logging.basicConfig(level="INFO")
logger = logging.getLogger("langchain_service")

chat_llm = VLLM(
    openai_api_key="EMPTY",
    openai_api_base="http://localhost:8000/v1/",
    model_name="lama3_chat_instruct"
)
sql_llm = VLLM(
    openai_api_key="EMPTY",
    openai_api_base="http://localhost:8001/v1/",
    model_name="phi_2_finetuined"
)
def test():
    logger.info("Testing langchain")
    response = chat_llm.invoke("hi")
    print(response)
    return response