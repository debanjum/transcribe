# Standard Packages
import json
import os
import uuid

# External Packages
import openai
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import Response, HTMLResponse


app = FastAPI()


# Only Allow Specified Hosts, Origins
hosts = os.getenv("ALLOWED_HOSTS", "").split(",")
if isinstance(hosts, str):
    hosts = [hosts]
hosts = [host.strip() for host in hosts if host.strip() != ""]
origins = [f"https://{host.strip()}" for host in hosts if host.strip() != ""]

if hosts:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=hosts)
if origins:
    app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["*"], allow_headers=["*"])

# Configure OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")
if openai.api_key is None:
    raise Exception("Missing OPENAI_API_KEY environment variable")

# Load the index.html once on startup
with open("src/index.html", "r") as index_file:
    index_html = index_file.read()


@app.get("/", response_class=HTMLResponse)
def transcribe_widget():
    return HTMLResponse(content=index_html, status_code=200)


@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    audio_filename = f"{str(uuid.uuid4())}.webm"
    user_message: str = None

    # Transcribe the audio from the request
    try:
        # Store the audio from the request in a temporary file
        audio_data = await file.read()
        with open(audio_filename, "wb") as audio_file_writer:
            audio_file_writer.write(audio_data)
        audio_file = open(audio_filename, "rb")

        # Send the audio data to the Whisper API
        response = openai.audio.translations.create(model="whisper-1", file=audio_file)
        user_message = response.text
    finally:
        # Close and Delete the temporary audio file
        audio_file.close()
        os.remove(audio_filename)

    if user_message is None:
        return Response(status_code=500)

    # Return the spoken text
    content = json.dumps({"text": user_message})
    return Response(content=content, media_type="application/json", status_code=200)
