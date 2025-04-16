from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os
import time  # ⏱️ pour mesurer le temps

VLLM_API_URL = os.getenv("VLLM_API_URL", "http://localhost:8000/v1/completions")

app = FastAPI()

class PromptRequest(BaseModel):
    prompt: str
    max_tokens: int = 100
    temperature: float = 0.7

@app.post("/generate/")
def generate_text(request: PromptRequest):
    payload = {
        "model": "/model",
        "prompt": request.prompt,
        "max_tokens": request.max_tokens,
        "temperature": request.temperature
    }

    try:
        start_time = time.time()  # ⏱️ Start timer
        response = requests.post(VLLM_API_URL, json=payload)
        response.raise_for_status()
        end_time = time.time()  # ⏱️ End timer

        elapsed_time = round(end_time - start_time, 2)  # arrondi en secondes

        return {
            "response": response.json()["choices"][0]["text"],
            "response_time_seconds": elapsed_time
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur vLLM : {str(e)}")
# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# import openai
# import time
# import os

# openai.api_base = os.getenv("VLLM_API_URL", "http://localhost:8000/v1")
# openai.api_key = "fake-api-key"  # vLLM ne vérifie pas l'API key

# app = FastAPI()

# class PromptRequest(BaseModel):
#     prompt: str
#     max_tokens: int = 100
#     temperature: float = 0.7

# @app.post("/generate/")
# def generate_text(request: PromptRequest):
#     try:
#         start = time.time()

#         response = openai.Completion.create(
#             model="/model",  # n'importe quel nom fonctionne avec vLLM
#             prompt=request.prompt,
#             max_tokens=request.max_tokens,
#             temperature=request.temperature,
#         )

#         elapsed = round(time.time() - start, 2)
#         return {
#             "response": response.choices[0].text.strip(),
#             "response_time_seconds": elapsed
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Erreur vLLM : {str(e)}")
