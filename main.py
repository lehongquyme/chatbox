from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import datetime
import os
import requests

# Replace this with your ngrok/cloudflared endpoint later
OLLAMA_API_BASE = os.getenv("OLLAMA_API", "https://6e352132955b.ngrok-free.app")


def get_llm_response(prompt: str) -> str:
    system_instruction = (
        "Bạn là một chatbot hữu ích. Hãy luôn trả lời bằng tiếng Việt, ngắn gọn, rõ ràng."
    )
    full_prompt = f"{system_instruction}\n\nNgười dùng: {prompt}\n\nChatbot:"

    try:
        res = requests.post(
            f"{OLLAMA_API_BASE}/api/generate",
            json={
                "model": "llama3",
                "prompt": full_prompt,
                "stream": False,
            },
            timeout=60
        )
        res.raise_for_status()
        return res.json()["response"].strip()
    except Exception as e:
        print(f"Lỗi Ollama: {e}")
        return "Bot không thể kết nối đến trí tuệ (Ollama). Hãy kiểm tra kết nối."

# Model input
class Message(BaseModel):
    message: str


chat_history = []
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def root():
    with open("static/index.html", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.post("/chat")
async def chat(msg: Message):
    prompt = msg.message.strip()
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")

    if not prompt:
        raise HTTPException(status_code=400, detail="Tin nhắn rỗng.")

    chat_history.append({"sender": "user", "text": prompt, "timestamp": timestamp})
    response = get_llm_response(prompt)
    chat_history.append({"sender": "bot", "text": response, "timestamp": datetime.datetime.now().strftime("%H:%M:%S")})
    return JSONResponse(content={"text": response, "error": False})

@app.get("/history")
async def get_history():
    return chat_history
@app.post("/clear_history")
async def clear_history():
    chat_history.clear()
    return {"message": "Lịch sử đã được xóa"}
