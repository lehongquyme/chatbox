import whisper # type: ignore

model = whisper.load_model("base")

def transcribe_audio(file_path):
    # Thêm language='vi' để nhận diện tiếng Việt hiệu quả hơn
    result = model.transcribe(file_path, language='vi') 
    return result["text"]