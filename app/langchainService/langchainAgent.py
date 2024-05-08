import requests
import os
import logging
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_nvidia_ai_endpoints._common import NVEModel
from langchain_nvidia_trt.llms import TritonTensorRTLLM
logging.basicConfig(level="INFO")
logger = logging.getLogger("langchain_service")
api_key = "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"
base_url = "https://api.ngc.nvidia.com/v2/"
# UNCOMMENT to use for prod. currenly using nvida api for developement
# main_chat_llm = TritonTensorRTLLM(
#     server_url="http://localhost:8000",
#     model_name="llama",
#     temperature=0.2,
#     beam_width=2,
#     tokens=500,
#     )
chat_llm = ChatNVIDIA(api_key=api_key)

    
if __name__ == "__main__":
    # set_connection()
    models = NVEModel(api_key=api_key).available_models
    print(models)