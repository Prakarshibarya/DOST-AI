from fastapi import FastAPI, UploadFile
from backend import chat, start_intro, save_character_config, update_avatar
import uvicorn

app = FastAPI()

@app.get("/intro")
def play_intro():
    return {"text": start_intro()}

@app.post("/chat")
def run_chat():
    user, ai = chat()
    return {"user": user, "ai": ai}

@app.post("/save")
def save_character(name: str, personality: str):
    msg, avatar_url = save_character_config(name, personality, "")
    return {"message": msg, "avatar": avatar_url}

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
