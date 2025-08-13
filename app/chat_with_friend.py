import sounddevice as sd
from scipy.io.wavfile import write
import whisper
import pyttsx3
import requests
import re

engine = pyttsx3.init()
voices = engine.getProperty('voices')

for index, voice in enumerate(voices):
    print(f"{index}: {voice.name} - {voice.id}")



# Record voice
def record_voice(duration=3, filename="input.wav"):
    fs = 44100
    print("\n🎤 Speak now...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=2)
    sd.wait()
    write(filename, fs, audio)
    print("🎧 Saved:", filename)

# Transcribe with Whisper (fast mode)
def transcribe_audio(filename="input.wav"):
    model = whisper.load_model("tiny")  # faster!
    result = model.transcribe(filename)
    text = result["text"].strip()
    print("🗣️ You said:", text)
    return text

# Get reply from Ollama
def get_reply(chat_history):
    payload = {
        "model": "gemma:2b",  # or your preferred model
        "prompt": chat_history,
        "stream": False,
        "options": {
            "num_predict": 100,
            "stop": ["\nYou:", "\nFriend:", "\nZen:"]
        }
    }
    response = requests.post("http://localhost:11434/api/generate", json=payload)
    raw_reply = response.json()["response"].strip()

    # Remove unwanted meta lines
    filtered_reply = "\n".join(
        line for line in raw_reply.splitlines()
        if not line.lower().startswith("(prompt")
    ).strip()

    return filtered_reply


# Speak out loud
def speak_response(text):
    import re
    text = re.sub(r'[^\w\s.,!?\'\"-]', '', text)
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'\(.*?\)', '', text)
    text = re.sub(r'\s+', ' ', text).strip()

    engine = pyttsx3.init()
    voices = engine.getProperty('voices')

    # Try to select a softer voice
    for voice in voices:
        if 'zira' in voice.name.lower() or 'jenny' in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break

    engine.setProperty('rate', 155)  # slower, calmer speaking speed
    engine.say(text)
    engine.runAndWait()




# Main loop
def main():
    print("👋 Start chatting with your AI friend. Say 'end conversation' to stop.\n")

    chat_history = (
        "You're talking to your close friend named Zen. Zen is warm, funny, and loves listening.\n"
        "Zen talks casually like a real friend, not like a chatbot.\n\n"
    )

    while True:
        record_voice()
        user_input = transcribe_audio()

        if "end conversation" in user_input.lower():
            goodbye = "Bye! It was really fun talking to you. See you soon!"
            print( goodbye)
            speak_response(goodbye)
            break

        chat_history += f"You: {user_input}\nZen: "
        reply = get_reply(chat_history)
        print(" Zen:", reply)

        chat_history += reply + "\n"
        speak_response(reply)

main()
