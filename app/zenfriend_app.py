from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from faster_whisper import WhisperModel
import sounddevice as sd
from scipy.io.wavfile import write
import pyttsx3
import requests
import os
import json
from datetime import datetime
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# ──────────────── App Setup ────────────────
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    return FileResponse("static/index.html")

# ──────────────── Config & Character ────────────────
CONFIG_FILE = "zenfriend_config.json"
JOURNAL_DIR = "zen_journal"
os.makedirs(JOURNAL_DIR, exist_ok=True)

DEFAULT_CHARACTER = {
    "name": "Zen",
    "personality": "Calm",
    "style_prompt": "You're a calm and supportive friend. Speak gently and listen.",
    "intro_text": "Hi! I'm Zen. I'm always here when you need someone to talk to."
}

whisper_model = WhisperModel("tiny", compute_type="int8")

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CHARACTER, f, indent=2)
        return DEFAULT_CHARACTER

character = load_config()

# ──────────────── Audio & AI Functions ────────────────
def record_voice(duration=4.0, filename="input.wav"):
    fs = 44100
    print("🎤 Listening...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    write(filename, fs, audio)

def transcribe_audio(filename="input.wav"):
    segments, _ = whisper_model.transcribe(filename)
    return " ".join([seg.text for seg in segments]).strip()

def get_ai_response(prompt, style_prompt):
    full_prompt = f"""{style_prompt}

### Conversation
User: {prompt}
{character['name']}:"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "phi",
            "prompt": full_prompt,
            "stream": False,
            "options": {"num_predict": 100, "stop": ["\nUser:", f"\n{character['name']}:"]
            }
        },
    )
    return response.json()["response"].strip()

def speak(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.say(text)
    engine.runAndWait()

def log_to_journal(user_input, ai_reply, name):
    now = datetime.now().strftime("%Y-%m-%d")
    log_entry = f"[{datetime.now().strftime('%H:%M:%S')}]\nYou: {user_input}\n{name}: {ai_reply}\n\n"
    with open(f"{JOURNAL_DIR}/{now}.txt", "a", encoding="utf-8") as f:
        f.write(log_entry)

# ──────────────── API Models ────────────────
class UpdateConfig(BaseModel):
    name: str
    personality: str

# ──────────────── Endpoints ────────────────
@app.post("/update_character")
def update_character(cfg: UpdateConfig):
    character["name"] = cfg.name
    character["personality"] = cfg.personality
    character["intro_text"] = f"Hi! I'm {cfg.name}. I'm always here when you need someone to talk to."
    character["style_prompt"] = {
        "Calm": "You're a calm and supportive friend. Speak gently and listen.",
        "Uplifting": "You're an optimistic friend. Cheer them up with kind words!",
        "Witty": "You're a clever, funny friend. Make them smile with smart humor."
    }[cfg.personality]
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(character, f, indent=2)
    return {"status": "ok", "intro_text": character["intro_text"]}

@app.post("/upload_audio")
async def process_audio(file: UploadFile):
    contents = await file.read()
    with open("input.wav", "wb") as f:
        f.write(contents)

    user_text = transcribe_audio("input.wav").strip()
    if not user_text:
        return {"user": "", "reply": "Didn't catch that. Try again?"}

    ai_reply = get_ai_response(user_text, character["style_prompt"])
    speak(ai_reply)
    log_to_journal(user_text, ai_reply, character["name"])
    return {"user": user_text, "reply": ai_reply}

@app.get("/intro")
def intro():
    speak(character["intro_text"])
    return {"message": f"{character['name']} says: {character['intro_text']}"}
