import sounddevice as sd
from scipy.io.wavfile import write
import whisper
import pyttsx3
import requests
import json

# 1. Record voice input
def record_voice(duration=5, filename="input.wav"):
    fs = 44100
    print(" Recording...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=2)
    sd.wait()
    write(filename, fs, audio)
    print(" Recording saved as", filename)

# 2. Transcribe audio using Whisper
def transcribe_audio(filename="input.wav"):
    print(" Transcribing...")
    model = whisper.load_model("base")
    result = model.transcribe(filename)
    print(" You said:", result["text"])
    return result["text"]

# 3. Get empathetic response from Ollama
def get_therapist_reply(user_input):
    print("Thinking...")
    payload = {
        "model": "mistral",
        "prompt": f"You are a calm and empathetic therapist. Be kind and gentle.\nUser: {user_input}\nTherapist:",
        "stream": False
    }
    response = requests.post("http://localhost:11434/api/generate", json=payload)
    reply = response.json()["response"]
    print("🧘 Therapist:", reply)
    return reply

# 4. Speak the reply aloud
def speak_response(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# Run full loop
def main():
    record_voice()
    user_input = transcribe_audio()
    therapist_reply = get_therapist_reply(user_input)
    speak_response(therapist_reply)

# Start it
main()
