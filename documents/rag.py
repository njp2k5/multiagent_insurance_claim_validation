import os
import requests

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

def summarize_documents(context: str) -> str:
    payload = {
        "model": os.getenv("OPENROUTER_MODEL"),
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an insurance document validation assistant. "
                    "Summarize the documents and assess legitimacy."
                )
            },
            {
                "role": "user",
                "content": context
            }
        ]
    }

    headers = {
        "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
        "Content-Type": "application/json"
    }

    res = requests.post(OPENROUTER_URL, json=payload, headers=headers, timeout=30)
    res.raise_for_status()
    return res.json()["choices"][0]["message"]["content"]
