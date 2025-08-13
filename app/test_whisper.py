# test_whisper.py
from faster_whisper import WhisperModel

model = WhisperModel("tiny", compute_type="int8")

segments, _ = model.transcribe("test_output.wav")
text = " ".join([seg.text for seg in segments]).strip()
print("Transcription:", text)
