import sounddevice as sd
from scipy.io.wavfile import write
from faster_whisper import WhisperModel
import pyttsx3
import requests

# Step 1: Record voice input
print("🎙️ Speak something for 3 seconds...")
fs = 44100
duration = 3
audio = sd.rec(int(duration * fs), samplerate=fs, channels=2)
sd.wait()
write("test_input.wav", fs, audio)
print("✅ Recording saved.")

# Step 2: Transcribe using Whisper
print("🧠 Transcribing...")
whisper_model = WhisperModel("tiny", compute_type="int8")
segments, _ = whisper_model.transcribe("test_input.wav")
user_text = " ".join([seg.text for seg in segments])
print("📝 You said:", user_text)

# Step 3: Get AI reply
print("🤖 Getting AI response...")
response = requests.post(
    "http://localhost:11434/api/generate",  # Make sure Ollama is running
    json={
        "model": "phi",
        "prompt": f"You are a friendly AI friend.\n\nUser: {user_text}\nFriend:",
        "stream": False,
        "options": {"num_predict": 80, "stop": ["\nUser:", "\nFriend:"]}
    }
)
ai_reply = response.json()["response"].strip()
print("🤖 AI says:", ai_reply)

# Step 4: Speak response
print("🔊 Speaking...")
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.say(ai_reply)
engine.runAndWait()
