# Standard Packages
import json
import os
import uuid

# External Packages
import openai
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import Response


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/speak")
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
        api_key = os.getenv("OPENAI_API_KEY")
        response = openai.Audio.translate(model="whisper-1", file=audio_file, api_key=api_key)
        user_message = response["text"]
    finally:
        # Close and Delete the temporary audio file
        audio_file.close()
        os.remove(audio_filename)

    if user_message is None:
        return Response(status_code=500)

    # Return the spoken text
    content = json.dumps({"text": user_message})
    return Response(content=content, media_type="application/json", status_code=200)

