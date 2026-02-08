from ollama import chat
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

def ollamaQueryVerbose(context):
    options = {
        "num_ctx":window
    }    
    print("\n--- Ollama Response Start ---")
    full_response = ""

    iterator = chat(model=model, messages=context, stream=True, tools=None, options=options)
    try:
        for response in iterator:
            token = response.get('message', {}).get('content', '')
            print(token, end="", flush=True)
            full_response += token
    except ResponseError as e:
        if "error parsing tool call" in str(e):
            # Extract what the model actually output
            token = rawFromException(e)
            print(token, end="", flush=True)
            full_response += token
        else:
            raise

    print("\n--- Ollama Response End ---\n")
    return full_response

promptmodel = ollamaQueryVerbose

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
