from ollama import chat
from ollama import ChatResponse
import requests

model = "gpt-oss:20b"
def ollamaQuery(context):#list of dictionaries containing roles and contents
    success = False
    while not success:
        try:
            response: ChatResponse = chat(model = model, messages = context, tools = None)
            success = True
        except ollama._types.ResponseError as e:
            print(str(e)+", trying again")
    return response['message']['content']

def ollamaQueryVerbose(context):
    print("\n--- Ollama Response Start ---\n")
    full_response = ""
    success = False
    while not success:
        try:
            for response in chat(model=model, messages=context, stream=True, tools = None):
                token = response.get('message',{}).get('content','')
                print(token, end="", flush=True)  # print tokens as they come
                full_response += token
            success = True
        except ollama._types.ResponseError as e:
            print(str(e)+", trying again")
            full_response = ""
    print("\n\n--- Ollama Response End ---\n")
    return full_response

def geminiQuery(context):
    """
    context: list of dictionaries with "role" and "content", e.g.,
             [{"role": "user", "content": "Hello"}]
    """
    key = "AIzaSyBCc8P5VmrfiAzKtEyIFUIHaO7m2muCcgU"
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent"
    
    headers = {
        "x-goog-api-key": key,
        "Content-Type": "application/json"
    }

    # Map OLLAMA-style roles to Gemini-style roles
    role_map = {
        "system": "system",
        "user": "user",
        "assistant": "model"  # Gemini uses 'model' for the assistant
    }

    contents = []
    for msg in context:
        g_role = role_map.get(msg["role"], "user")  # default to 'user'
        contents.append({
            "role": g_role,
            "parts": [{"text": msg["content"]}]
        })

    payload = {"contents": contents}

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()

    data = response.json()
    #print(data)
    # Combine all parts in all contents
    output_text = ""
    for item in data.get("contents", []):
        for part in item.get("parts", []):
            output_text += part.get("text", "")

    # If no text yet, fallback to 'candidates'
    if not output_text:
        for candidate in data.get("candidates", []):
            for part in candidate.get("content", {}).get("parts", []):
                output_text += part.get("text", "")
    return output_text

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
