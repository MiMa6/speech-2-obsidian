import os
from dotenv import load_dotenv
from src.audio_recorder import AudioRecorder
from src.transcriber import Transcriber
from src.file_manager import FileManager


def main():
    # Load environment variables
    load_dotenv()

    # Get environment variables
    OBSIDIAN_VAULT_PATH = os.getenv("OBSIDIAN_VAULT_PATH")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    # Optional: Get custom microphone name from environment
    MIC_NAME = os.getenv("MICROPHONE_NAME")  # Will use default if not set

    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    if not OBSIDIAN_VAULT_PATH:
        raise ValueError("OBSIDIAN_VAULT_PATH environment variable is not set")

    # Initialize components
    file_manager = FileManager(OBSIDIAN_VAULT_PATH)
    recorder = AudioRecorder(file_manager.audio_input_dir, mic_name=MIC_NAME)
    transcriber = Transcriber(OPENAI_API_KEY)

    print("\n=== Speech-to-Text Converter ===")
    print("This program will record your voice and convert it to text.")
    print("The recording will automatically stop after 2 seconds of silence.")

    while True:
        print("\nAvailable commands:")
        print("1: Record new audio")
        print("2: Quit")

        command = input("\nEnter command (1 or 2): ").strip()

        if command == "2":
            print("Goodbye!")
            break
        elif command == "1":
            try:
                # Record audio
                print(
                    "\nStarting new recording (will automatically stop after 2 seconds of silence)..."
                )
                audio_file = recorder.record()

                # Transcribe audio
                print("Converting speech to text...")
                transcript = transcriber.transcribe(audio_file)
                print(f"\nTranscript: {transcript.text}")

                # Get first three words for file naming
                title_words = " ".join(transcript.text.split()[:3])

                # Save transcription and move audio file
                file_manager.save_transcription(transcript, title_words)
                file_manager.move_audio_file(audio_file, title_words)

            except Exception as e:
                print(f"\nError: {str(e)}")
                print("Please try again.")
        else:
            print("\nInvalid command. Please enter 1 to record or 2 to quit.")


if __name__ == "__main__":
    main()
