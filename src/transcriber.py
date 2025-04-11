from openai import OpenAI


class Transcriber:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def transcribe(self, audio_file_path):
        """Transcribe audio file to text using OpenAI's API."""
        try:
            with open(audio_file_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",  # Using the correct model name
                    file=audio_file,
                    language="en",
                )
            return transcript
        except Exception as e:
            print(f"Error during transcription: {str(e)}")
            raise
