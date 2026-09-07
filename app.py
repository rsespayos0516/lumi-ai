import os
import httpx

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(title="LUMI-AI")

app.mount("/static", StaticFiles(directory="static"), name="static")


class ChatRequest(BaseModel):
    message: str


@app.get("/")
async def home():
    return FileResponse("static/index.html")


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "app": "LUMI-AI"
    }


@app.post("/api/chat")
async def chat(request: ChatRequest):

    api_key = os.getenv("LUMI_API_KEY")

    if not api_key:
        return {
            "reply": "LUMI-AI is running, but the AI API key has not been configured yet."
        }

    model = os.getenv("LUMI_MODEL", "gpt-5.6-luna")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "input": request.message
    }

    try:

        async with httpx.AsyncClient(timeout=120) as client:

            response = await client.post(
                "https://api.openai.com/v1/responses",
                headers=headers,
                json=payload
            )

            response.raise_for_status()

            data = response.json()

            reply = data.get("output_text")

            if not reply:
                reply = "I received the request, but no text response was returned."

            return {
                "reply": reply
            }

    except Exception as e:

        return {
            "reply": f"LUMI-AI could not contact the AI service: {str(e)}"
        }


if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080
    )
