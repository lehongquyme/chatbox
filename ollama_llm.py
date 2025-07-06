import requests # type: ignore

def get_llm_response(prompt: str) -> str:
    """
    Gửi yêu cầu đến Ollama API để lấy phản hồi từ mô hình LLM.
    Đảm bảo Ollama đang chạy và mô hình đã được tải.
    """
    # System instruction (hướng dẫn cho LLM) để đảm bảo phản hồi bằng tiếng Việt
    system_instruction = "Bạn là một chatbot hữu ích và thân thiện. Hãy trả lời các câu hỏi ngắn gọn và trực tiếp. Đừng đưa ra các danh sách dài dòng hoặc thông tin không liên quan. QUAN TRỌNG: Hãy LUÔN LUÔN trả lời bằng tiếng Việt."
    
    # Kết hợp system prompt với câu hỏi của người dùng
    full_prompt = f"{system_instruction}\n\nNgười dùng nói: {prompt}\n\nChatbot phản hồi:"

    try:
        response = requests.post(
            # ĐÂY LÀ ĐỊA CHỈ API CỦA OLLAMA TRÊN MÁY LOCAL CỦA BẠN (LUÔN LÀ LOCALHOST)
            "http://localhost:11434/api/generate", 
            json={
                "model": "llama3", # Đảm bảo bạn đã pull mô hình này bằng `ollama pull llama3`
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7, # Độ "sáng tạo" của câu trả lời (0.0-2.0)
                    "top_p": 0.9      # Kiểm soát sự đa dạng của từ được chọn (0.0-1.0)
                }
            },
            timeout=120 # Đặt timeout lớn hơn cho các phản hồi của LLM
        )
        response.raise_for_status() # Ném lỗi nếu status code là lỗi (4xx, 5xx)
        
        # Trích xuất và trả về phản hồi từ JSON
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