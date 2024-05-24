from llama_index.llms.nvidia_triton import NvidiaTriton
triton_url = "localhost:8001"
model_name = "ensemble"
resp = NvidiaTriton(
    server_url=triton_url,
    model_name=model_name,
    tokens=1024,
    temperature=1
).complete("Can you write a complete news article, 250 words, about the recent advances in renewable energy? ")
print(resp)