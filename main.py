from fastapi import FastAPI, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def serve_index():
    return FileResponse("static/index.html")

@app.post("/chat")
async def chat(prompt: str = Form(...)):
    return JSONResponse({"response": f"Bạn hỏi: {prompt}"})
