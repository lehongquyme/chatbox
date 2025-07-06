from fastapi import FastAPI, HTTPException # type: ignore
from fastapi.responses import JSONResponse, HTMLResponse # type: ignore
from fastapi.staticfiles import StaticFiles # type: ignore
from pydantic import BaseModel # type: ignore
import datetime
import os
import requests # type: ignore # Ignore type checking warnings for the requests library

# This function interacts with Ollama running on your local machine
def get_llm_response(prompt: str) -> str:
    """
    Sends a request to the Ollama API to get a response from the LLM.
    Ensures Ollama is running and the model is loaded.
    """
    # System instruction (guidance for the LLM) to ensure responses are in Vietnamese
    system_instruction = "Bạn là một chatbot hữu ích và thân thiện. Hãy trả lời các câu hỏi ngắn gọn và trực tiếp. Đừng đưa ra các danh sách dài dòng hoặc thông tin không liên quan. QUAN TRỌNG: Hãy LUÔN LUÔN trả lời bằng tiếng Việt."
    
    # Combine the system prompt with the user's question
    full_prompt = f"{system_instruction}\n\nNgười dùng nói: {prompt}\n\nChatbot phản hồi:"

    try:
        response = requests.post(
            # THIS ADDRESS MUST BE THE OLLAMA API ON YOUR LOCAL MACHINE
            # NEVER USE YOUR NGROK ADDRESS HERE!
            "http://localhost:11434/api/generate", # Default Ollama port
            json={
                "model": "llama3", # Make sure you have pulled this model using `ollama pull llama3`
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7, # Controls the "creativity" of the response (0.0-2.0)
                    "top_p": 0.9      # Controls the diversity of chosen words (0.0-1.0)
                }
            },
            timeout=120 # Set a longer timeout for LLM responses
        )
        response.raise_for_status() # Raise an exception for HTTP errors (4xx, 5xx)
        
        # Extract and return the response from JSON
        return response.json()["response"].strip()
        
    except requests.exceptions.ConnectionError:
        print("Lỗi kết nối: Không thể kết nối tới Ollama. Vui lòng đảm bảo Ollama đang chạy trên cổng 11434.")
        return "Xin lỗi, tôi không thể kết nối với trí tuệ của mình. Vui lòng kiểm tra xem Ollama có đang chạy không nhé!"
    except requests.exceptions.Timeout:
        print("Lỗi Timeout: Ollama không phản hồi kịp thời. Mô hình có thể quá lớn hoặc hệ thống chậm.")
        return "Xin lỗi, tôi mất quá nhiều thời gian để suy nghĩ. Vui lòng thử lại hoặc câu hỏi ngắn gọn hơn."
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi gọi Ollama API: {e}")
        return f"Bot gặp lỗi hệ thống khi liên lạc với trí tuệ: {e}. Vui lòng thử lại sau."
    except KeyError:
        print(f"Lỗi: Không tìm thấy khóa 'response' trong JSON phản hồi từ Ollama.")
        return "Bot gặp lỗi hệ thống: Định dạng phản hồi từ trí tuệ không đúng."
    except Exception as e:
        print(f"Một lỗi không xác định xảy ra trong get_llm_response: {e}")
        return "Bot gặp một lỗi không xác định. Vui lòng thử lại hoặc liên hệ hỗ trợ."

# Initialize FastAPI app
app = FastAPI()

# Pydantic model to validate input data for the chat API
class Message(BaseModel):
    message: str

# Temporary chat history (stored in server memory, will be lost on server restart)
chat_history = []

# ==============================================================================
# CONFIGURATION FOR FASTAPI TO SERVE STATIC FILES (HTML, CSS, JS)
# ==============================================================================
# Mount the 'static' directory to serve static files.
# The path '/static' will be used to access files within the 'static' directory.
# IMPORTANT: DO NOT USE html=True HERE TO AVOID ROUTING CONFLICTS
app.mount("/static", StaticFiles(directory="static"), name="static")

# Route for the root path ("/") to return the index.html file
@app.get("/", response_class=HTMLResponse)
async def read_root():
    # Use os.path.join to create a path compatible with all operating systems
    html_file_path = os.path.join("static", "index.html")
    
    # Check if index.html file exists
    if not os.path.exists(html_file_path):
        raise HTTPException(status_code=404, detail="index.html not found in static directory. Make sure it's in the 'static' folder.")
    
    with open(html_file_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)
# ==============================================================================

# API endpoint to handle chat requests
@app.post("/chat")
async def chat_with_llm(msg: Message):
    user_text = msg.message.strip()
    if not user_text:
        raise HTTPException(status_code=400, detail="Tin nhắn không được để trống.")
        
    current_time = datetime.datetime.now().strftime("%H:%M:%S")

    # Add user message to history
    chat_history.append({"sender": "user", "text": user_text, "timestamp": current_time})

    try:
        # Call get_llm_response to get the response from Ollama
        llm_response = get_llm_response(user_text)
        
        # Add LLM's response to history
        chat_history.append({"sender": "bot", "text": llm_response, "timestamp": datetime.datetime.now().strftime("%H:%M:%S")})
        
        # Return response to the frontend
        return JSONResponse(content={"text": llm_response, "error": False})
        
    except HTTPException as http_exc:
        # Catch HTTPExceptions raised from get_llm_response or elsewhere
        chat_history.append({"sender": "bot", "text": http_exc.detail, "timestamp": datetime.datetime.now().strftime("%H:%M:%S"), "error": True})
        raise http_exc # Re-raise HTTPException for FastAPI to handle status code
    except Exception as e:
        # Handle other unexpected errors during chat processing
        error_message = f"Có lỗi xảy ra khi xử lý yêu cầu chat: {str(e)}"
        print(f"Lỗi hệ thống: {error_message}")
        chat_history.append({"sender": "bot", "text": error_message, "timestamp": datetime.datetime.now().strftime("%H:%M:%S"), "error": True})
        raise HTTPException(status_code=500, detail="Máy chủ gặp lỗi nội bộ khi xử lý tin nhắn của bạn.")

# API endpoint to retrieve the entire chat history
@app.get("/history")
async def get_history():
    return JSONResponse(content=chat_history)

# API endpoint to clear chat history (optional, can be used with a UI button)
@app.post("/clear_history")
async def clear_history():
    chat_history.clear()
    return JSONResponse(content={"message": "Lịch sử trò chuyện đã được xóa."})
