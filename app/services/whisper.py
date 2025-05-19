import os
import json
from dotenv import load_dotenv
from groq import Groq
from fastapi import UploadFile
from tempfile import NamedTemporaryFile

load_dotenv()
client = Groq()

async def transcribe_audio(file: UploadFile) -> str:
    with NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
        temp_file.write(await file.read())
        temp_file_path = temp_file.name

    with open(temp_file_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-large-v3-turbo",
            prompt="",
            response_format="verbose_json",
            timestamp_granularities=["segment"],
            language="pt",
            temperature=0.0
        )

    os.remove(temp_file_path)
    return transcription.text
