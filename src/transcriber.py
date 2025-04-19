from openai import OpenAI
from dataclasses import dataclass


@dataclass
class TranscriptionResult:
    """Simple wrapper for transcription results."""

    text: str


class Transcriber:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def transcribe(self, audio_file_path):
        """
        Transcribe audio file to text using OpenAI's API.

        Returns:
            TranscriptionResult: Object containing the transcribed text
        """
        try:
            with open(audio_file_path, "rb") as audio_file:
                transcript_text = self.client.audio.transcriptions.create(
                    model="gpt-4o-transcribe",  # Using the latest model for better accuracy
                    file=audio_file,
                    language="en",
                    response_format="text",  # Get plain text response
                )
            return TranscriptionResult(text=transcript_text)
        except Exception as e:
            print(f"Error during transcription: {str(e)}")
            raise
