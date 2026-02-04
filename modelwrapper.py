from ollama import chat
from ollama import ChatResponse

model = "qwen3:8b"

def ollamaQuery(context):#list of dictionaries containing roles and contents
    response: ChatResponse = chat(model = model, messages = context)
    return response['message']['content']

promptmodel = ollamaQuery
