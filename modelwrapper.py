from ollama import chat, generate
from ollama import ChatResponse
from ollama._types import ResponseError
import re

def rawFromException(e: ResponseError) -> str:
    search = re.search(r"raw='(.*)', err=", str(e))
    if search:
        return search.group(1)
    else:
        return ""

model = "gpt-oss:20b"
window = 4096

def ollamaChat(context, stoptokens = []):
    options = {
        "num_ctx":window
    }
    print("\n--- Ollama Response Start ---")
    full_response = ""

    iterator = chat(model=model, messages=context, stream=True, tools=None, options=options)
    for response in iterator:
        try:
            token = response.get('message', {}).get('content', '')
        except ResponseError as e:
            if "error parsing tool call" in str(e):
                token = rawFromException(e)
            else:
                raise
        print(token, end="", flush=True)
        hit = False
        full_response += token
        for stops in stoptokens:
            if stops in full_response:
                full_response = full_response.split(stops)[0]
                hit = True
                break
        if hit:
            break
    print("\n--- Ollama Response End ---\n")
    return full_response

def ollamaContinue(context, stoptokens = ["[END]","[STOP]","SYSTEM:","USER:","ASSISTANT:"],strip=True):
    options = {
        "num_ctx":window
    }
    textprompt = ""
    for message in context:
        textprompt += f"{message['role'].upper()}:\n{message['content']}\n\n"
    print("\n--- Ollama Continuation Start ---")
    full_response = ""
    iterator = generate(model=model, prompt=textprompt, stream=True, tools=None, options=options)
    for response in iterator:
        try:
            token = response.get('response','')
        except ResponseError as e:
            if "error parsing tool call" in str(e):
                token = rawFromException(e)
            else:
                raise
        print(token, end="", flush=True)
        hit = False
        full_response += token
        for stops in stoptokens:
            if stops in full_response:
                full_response = full_response.split(stops)[0]
                hit = True
                break
        if hit:
            break
    print("\n--- Ollama Continuation End ---\n")
    if strip:
        return full_response.rstrip()
    else:
        return full_response

queryoptions = {
    "chat": ollamaChat,
    "continue": ollamaContinue
}

promptmodel = ollamaChat

if __name__ == "__main__":
    testpayload = [
        {
            "role": "system",
            "content": "If you see this, everything is working correctly. Give the user a one-sentence joke."
        },
        {
            "role": "user",
            "content": "hello!"
        },
    ]
    print(promptmodel(testpayload))
