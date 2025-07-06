import os
os.environ["SPEECHBRAIN_LOCAL_DOWNLOAD"] = "copy"

from speechbrain.inference.TTS import Tacotron2 # type: ignore
from speechbrain.inference.vocoders import HIFIGAN # type: ignore
import torchaudio # type: ignore
import uuid

# Load model TTS & vocoder
# LƯU Ý QUAN TRỌNG: Các mô hình này (tts-tacotron2-ljspeech và tts-hifigan-ljspeech)
# được đào tạo trên bộ dữ liệu LJSpeech (tiếng Anh).
# Để có tiếng Việt tự nhiên, bạn cần tìm một mô hình SpeechBrain được đào tạo trên dữ liệu tiếng Việt,
# hoặc xem xét các thư viện TTS khác có hỗ trợ tiếng Việt tốt hơn (ví dụ: Coqui TTS với các mô hình tiếng Việt).
try:
    tts = Tacotron2.from_hparams(source="speechbrain/tts-tacotron2-ljspeech", savedir="pretrained_models/tts")
    vocoder = HIFIGAN.from_hparams(source="speechbrain/tts-hifigan-ljspeech", savedir="pretrained_models/vocoder")
    print("SpeechBrain TTS models loaded successfully.")
except Exception as e:
    print(f"Error loading SpeechBrain TTS models: {e}")
    tts = None
    vocoder = None


def synthesize_speech(text, file_path=None):
    if tts is None or vocoder is None:
        raise Exception("SpeechBrain TTS models failed to load. Cannot synthesize speech.")
        
    if not file_path:
        # Đảm bảo đường dẫn này khớp với thư mục phục vụ file tĩnh trong main.py
        file_path = f"responses/{uuid.uuid4()}.wav"
    
    os.makedirs(os.path.dirname(file_path), exist_ok=True) # Đảm bảo thư mục tồn tại

    mel_output = tts.encode_text(text)
    waveforms = vocoder.decode_batch(mel_output)
    # Sample rate 22050 là chuẩn cho LJSpeech
    torchaudio.save(file_path, waveforms.squeeze(1), 22050)
    return file_path