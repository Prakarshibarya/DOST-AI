import sounddevice as sd
from scipy.io.wavfile import write
import whisper

def record_voice(duration=5, filename="input.wav"):
    fs = 44100  # Sample rate
    print("Recording...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=2)
    sd.wait()  # Wait until recording is finished
    write(filename, fs, audio)
    print("Saved:", filename)

def transcribe_audio(filename="input.wav"):
    print("Loading Whisper model...")
    model = whisper.load_model("base")
    print("Transcribing...")
    result = model.transcribe(filename)
    print("You said:", result["text"])

# Run the functions
record_voice()
transcribe_audio()
