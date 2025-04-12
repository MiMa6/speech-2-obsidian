import os
import sys
import logging
from dotenv import load_dotenv
from src.audio_recorder import AudioRecorder
from src.transcriber import Transcriber
from src.file_manager import FileManager, FileManagerError
from src.config import Config


def setup_logging():
    """Configure logging for the application."""
    config = Config.get_instance()
    log_config = config.log

    # Get log file path (creates log directory if needed)
    log_file = log_config.get_log_path()

    logging.basicConfig(
        level=getattr(logging, log_config.LOG_LEVEL),
        format=log_config.LOG_FORMAT,
        handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler(log_file)],
    )

    logger = logging.getLogger(__name__)
    logger.info(f"Logging to file: {log_file}")
    return logger


def load_environment():
    """Load and validate environment variables."""
    load_dotenv()

    required_vars = {
        "OBSIDIAN_VAULT_PATH": os.getenv("OBSIDIAN_VAULT_PATH"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    }

    missing_vars = [var for var, value in required_vars.items() if not value]
    if missing_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )

    return required_vars


def process_recording(file_manager, recorder, transcriber, logger):
    """Handle the recording and transcription process."""
    try:
        logger.info("Starting new recording session")
        audio_file = recorder.record()

        logger.info("Converting speech to text")
        transcript = transcriber.transcribe(audio_file)
        print(f"\nTranscript: {transcript.text}")

        # Get first three words for file naming
        title_words = " ".join(transcript.text.split()[:3])

        # Save transcription and move audio file
        transcription_path = file_manager.save_transcription(transcript, title_words)
        audio_path = file_manager.move_audio_file(audio_file, title_words)

        logger.info(
            f"Successfully processed recording:\nTranscription: {transcription_path}\nAudio: {audio_path}"
        )
        return True

    except Exception as e:
        logger.error(f"Error processing recording: {str(e)}", exc_info=True)
        print(f"\nError: {str(e)}")
        return False


def display_menu():
    """Display the main menu options."""
    print("\nAvailable commands:")
    print("1: Record new audio")
    print("2: Quit")
    return input("\nEnter command (1 or 2): ").strip()


def main():
    logger = setup_logging()
    logger.info("Starting Speech-to-Text Converter")

    try:
        # Load and validate environment
        env_vars = load_environment()

        # Initialize components
        file_manager = FileManager(env_vars["OBSIDIAN_VAULT_PATH"])
        recorder = AudioRecorder(
            file_manager.audio_input_dir, mic_name=os.getenv("MICROPHONE_NAME")
        )
        transcriber = Transcriber(env_vars["OPENAI_API_KEY"])

        print("\n=== Speech-to-Text Converter ===")
        print("This program will record your voice and convert it to text.")
        print("The recording will automatically stop after 2 seconds of silence.")

        while True:
            command = display_menu()

            if command == "2":
                logger.info("User requested to quit")
                print("Goodbye!")
                break
            elif command == "1":
                process_recording(file_manager, recorder, transcriber, logger)
            else:
                print("\nInvalid command. Please enter 1 to record or 2 to quit.")

    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        print(f"\nFatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
