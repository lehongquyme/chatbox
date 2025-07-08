from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import datetime
import os
import requests

# ========================
# Cấu hình cho Ollama API
# ========================
OLLAMA_API_BASE = os.getenv("OLLAMA_API", "http://localhost:11434")

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
        print(f"[LỖI OLLAMA] {e}")
        return "Bot không thể kết nối đến trí tuệ (Ollama). Hãy kiểm tra kết nối."

# ========================
# Khai báo FastAPI
# ========================
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# ========================
# Model dữ liệu gửi từ frontend
# ========================
class Message(BaseModel):
    message: str

# ========================
# Bộ nhớ tạm cho lịch sử trò chuyện
# ========================
chat_history = []

# ========================
# Giao diện frontend (index.html)
# ========================
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    return FileResponse("static/index.html")

# ========================
# API: gửi tin nhắn
# ========================
@app.post("/chat")
async def chat(msg: Message):
    prompt = msg.message.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Tin nhắn rỗng.")

    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    chat_history.append({"sender": "user", "text": prompt, "timestamp": timestamp})

    response = get_llm_response(prompt)
    chat_history.append({
        "sender": "bot",
        "text": response,
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    })
    return JSONResponse(content={"text": response, "error": False})

# ========================
# API: lấy lịch sử chat
# ========================
@app.get("/history")
async def get_history():
    return JSONResponse(content=chat_history)

# ========================
# API: xóa lịch sử chat
# ========================
@app.post("/clear_history")
async def clear_history():
    chat_history.clear()
    return JSONResponse(content={"message": "Lịch sử đã được xóa"})
