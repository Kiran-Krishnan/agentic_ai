import requests
import json

def call_llm(prompt):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        },
        timeout=12000
    )
    return response.json()["response"]

## For line bt line chatgpt like steam instead of waiting for the full output

def call_llm_chat(prompt):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": True
        },
        stream=True,
        timeout=12000  # keep reasonable, not 12000
    )

    for line in response.iter_lines():
        if line:
            data = json.loads(line.decode("utf-8"))
            chunk = data.get("response", "")
            print(chunk, end="", flush=True)
