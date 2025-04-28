import requests
import json

VLLM_URL = "http://localhost:8000/v1/chat/completions"
MODEL_NAME = "deepseek"  # doit être le --served-model-name

# Image servie depuis image-server
image_url = "http://image-server:80/images/page_1.png"  # pour Docker, c'est bon

messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "Que vois-tu dans cette image ?"
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": image_url
                }
            }
        ]
    }
]

payload = {
    "model": MODEL_NAME,
    "messages": messages,
    "temperature": 0.2
}

headers = {"Content-Type": "application/json"}

response = requests.post(VLLM_URL, headers=headers, data=json.dumps(payload))
print(response.json()["choices"][0]["message"]["content"])
