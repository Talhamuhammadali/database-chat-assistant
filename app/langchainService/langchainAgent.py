from langchain_community.llms.vllm import VLLMOpenAI

chat_llm = VLLMOpenAI(
    openai_api_base="http://localhost:8000/v1/",
    model_name="lama3_chat_instruct"
)
sql_llm = VLLMOpenAI(
    openai_api_base="http://localhost:8001/v1/",
    model_name="phi_2_finetuined"
)
def test():
    response = chat_llm.invoke("hi")
    print(response)
    return response