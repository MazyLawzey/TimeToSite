

import json
import pyaudio
import vosk
import sys
import os
import requests
from dotenv import load_dotenv
import pyttsx3

# Загружаем переменные окружения
load_dotenv()

# Проверяем, что модель существует
MODEL_PATH = "vosk-model-small-ru-0.22"
if not os.path.exists(MODEL_PATH):
    print(f"❌ Модель не найдена в {MODEL_PATH}")
    print("Скачай: https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip")
    sys.exit(1)

print("✅ Модель загружена!")
model = vosk.Model(MODEL_PATH)
rec = vosk.KaldiRecognizer(model, 16000)

# OpenRoute API
OPENROUTE_API_KEY = os.getenv("OPENROUTE_API_KEY")
if not OPENROUTE_API_KEY:
    print("❌ OPENROUTE_API_KEY не найден в .env")
    sys.exit(1)

# Синтезатор речи
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 0.9)

# Микрофон
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=4000)
stream.start_stream()

def get_ai_response(user_text):
    """Получить ответ от OpenRoute API"""
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTE_API_KEY}",
                "HTTP-Referer": "https://github.com",
                "X-Title": "VoskAI",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "Ты полезный ассистент. Отвечай кратко и естественно на русском языке."},
                    {"role": "user", "content": user_text}
                ],
                "temperature": 0.7,
                "max_tokens": 150
            },
            timeout=10
        )
        
        if response.status_code != 200:
            data = response.json()
            error_msg = data.get("error", {}).get("message", response.text)
            return f"Ошибка AI: {error_msg}"
            
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.Timeout:
        return "Время ожидания ответа истекло"
    except Exception as e:
        return f"Ошибка при обращении к AI: {str(e)}"

def speak(text):
    """Произнести текст"""
    print(f"🤖 {text}")
    engine.say(text)
    engine.runAndWait()

try:
    while True:
        data = stream.read(4000, exception_on_overflow=False)
        
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            text = result.get("text", "").lower()
            
            if text:
                print(f"👤 Ты: '{text}'")
                response = get_ai_response(text)
                speak(response)
        else:
            partial = json.loads(rec.PartialResult())
            if partial.get("partial"):
                print(f"🔍 {partial['partial']}", end='\r')
                
except KeyboardInterrupt:
    print("\n👋 Пока!")
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()
