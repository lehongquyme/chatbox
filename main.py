from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/chat")
async def chat(prompt: str = Form(...)):
    # Tạm phản hồi giả lập
    if "tên" in prompt.lower():
        reply = "Tôi tên là Qfriend, chatbot của bạn!"
    else:
        reply = "Xin lỗi, tôi chưa hiểu. Hãy hỏi lại nhé!"
    return JSONResponse({"response": reply})
