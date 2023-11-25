# Standard Packages
import json
import os
import uuid

# External Packages
import openai
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import Response, HTMLResponse


app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def speak_interface():
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>District Court Proceeding</title>
<style>
  body {
    display: flex;
    font-family: 'Poppins', sans-serif;
    background-color: black;
    color: white;
    width: 100%;
    margin: 0;
    justify-content: center;
    align-content: center;
    -webkit-box-pack: center;
  }
  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }
  .container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    position: relative;
    padding: 2.3rem;
    background: rgb(36,37,38);
    border-radius: 30px;
    row-gap: 0.5rem;
    width: 60rem;
    box-shadow: 0px 5px 10px 2px rgba(36,37,38,0.5);
  }
  .text {
    position: relative;
    align-self: flex-start;
  }
  #title {
    font-size: 28px;
    margin-bottom: 20px;
  }
  #description {
    font-size: 18px;
  }
  .actions-row {
    display: flex;
    position: relative;
    justify-content: space-between;
    width: 100%;
    padding: 0.5em;
  }
  .action-buttons {
    display: flex;
    column-gap: 0.5rem;
  }
  .button {
    display: flex;
    position: relative;
    padding: 0.5em;
    outline: none;
    border: none;
    border-radius: 30px;
    font-size: 1em;
    cursor: pointer;
    transition: all 0.3s;
  }
  .button-record {
    background-color: rgb(23, 201, 100);
  }
  .button-stop {
    background-color: rgb(26, 92, 255);
  }
</style>
</head>
<body>
<div class="container">
  <div id="title" class="text">District Court Proceeding</div>
  <p id="description" class="text">Generate Transcript</p>
  <div class="actions-row">
    <div></div>
    <div class="action-buttons">
        <button class="button button-record">
            <box-icon name="microphone" color="white"></box-icon>
        </button>
        <button class="button button-stop">
            <box-icon name="reset" color="white"></box-icon>
        </button>
    </div>
  </div>
</div>
<script src="https://unpkg.com/boxicons@2.1.4/dist/boxicons.js"></script>
<script>
// Add JavaScript here for button interactions if necessary
</script>
</body>
</html>
"""

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

