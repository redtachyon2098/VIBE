import os
import json
import requests

DEFAULT_HOST = "http://localhost:11434"
REMOTE_FILE = "remote.txt"
model = "gpt-oss:20b"
window = 4096

if os.path.isfile(REMOTE_FILE):
    with open(REMOTE_FILE, "r") as f:
        lines = f.read().splitlines()
        if len(lines) >= 2:
            HOST = f"http://{lines[0].strip()}"
            TOKEN = lines[1].strip()
        else:
            HOST = DEFAULT_HOST
            TOKEN = None
else:
    HOST = DEFAULT_HOST
    TOKEN = None

HEADERS = {"Content-Type": "application/json"}
if TOKEN and HOST != DEFAULT_HOST:
    print(f"Modelwrapper: Remote server set to: {DEFAULT_HOST}")
    HEADERS["Authorization"] = f"Bearer {TOKEN}"

def stream_chat(messages, stops=[], options={}):
    url = f"{HOST}/v1/chat/completions"
    payload = {
        "model": model,
        "messages": messages,
        "options": options,
        "stream": True
    }
    full_response = ""
    with requests.post(url, headers=HEADERS, json=payload, stream=True) as r:
        r.raise_for_status()
        for line in r.iter_lines(decode_unicode=True):
            if not line or line.startswith("event: ping"):
                continue
            try:
                payload_line = line.strip()
                if payload_line.startswith("data: "):
                    payload_line = payload_line[len("data: "):]
                if payload_line == "[DONE]":
                    break
                token_json = json.loads(payload_line)
                token = token_json.get("choices", [{}])[0].get("delta", {}).get("content", "")
                print(token, end="", flush=True)
                full_response += token
                for stop in stops:
                    if stop in full_response:
                        full_response = full_response.split(stop)[0]
                        return full_response
            except Exception:
                continue
    print()
    return full_response

def stream_generate(prompt: str, stops=[], options={}, chunk_size=10):
    full_response = ""
    current_prompt = prompt

    while True:
        payload = {
            "model": model,
            "prompt": current_prompt,
            "options": {**options, "max_tokens": chunk_size}
        }
        r = requests.post(f"{HOST}/api/generate", headers=HEADERS, json=payload)
        r.raise_for_status()
        data = r.json()
        chunk = data.get("response", "")
        print(chunk, end="", flush=True)
        full_response += chunk
        stop_hit = False
        for stop in stops:
            if stop in full_response:
                full_response = full_response.split(stop)[0]
                stop_hit = True
                break
        if stop_hit or chunk.strip() == "":
            break
        current_prompt += chunk
    print()
    return full_response

def ollamaChat(context, stoptokens=[]):
    options = {"num_ctx": window}
    print("\n--- Ollama Response Start ---")
    response = stream_chat(context, stops=stoptokens, options=options)
    print("\n--- Ollama Response End ---\n")
    return response

def ollamaContinue(context, stoptokens=["SYSTEM:","USER:"], strip=True):
    textprompt = ""
    for message in context:
        textprompt += f"{message['role'].upper()}:\n{message['content']}\n\n"
    textprompt += "ASSISTANT:\n"

    options = {"num_ctx": window}
    print("\n--- Ollama Continuation Start ---")
    response = stream_generate(textprompt, stops=stoptokens, options=options)
    print("\n--- Ollama Continuation End ---\n")
    return response.rstrip() if strip else response

queryoptions = {
    "chat": ollamaChat,
    "continue": ollamaContinue
}
promptmodel = ollamaChat

if __name__ == "__main__":
    testpayload = [
        {"role": "system", "content": "Give a one-sentence joke."},
        {"role": "user", "content": "hello!"}
    ]
    print(promptmodel(testpayload))
