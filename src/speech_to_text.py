import whisper
import os
import certifi
os.environ["SSL_CERT_FILE"] = certifi.where()

def transcribe_audio(audio_path: str, model_size: str = "base") -> str:
    model = whisper.load_model(model_size)
    result = model.transcribe(audio_path)
    return result["text"]