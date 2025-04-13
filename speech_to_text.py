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
    print("3: Translate existing audio files")
    return input("\nEnter command (1, 2, or 3): ").strip()


def process_existing_audio_files(file_manager, transcriber, logger):
    """Process all existing audio files in the Translate directory."""
    try:
        # Find all audio files
        audio_files = file_manager.find_audio_files()

        if not audio_files:
            print("\nNo audio files found in the Translate directory.")
            return False

        print(f"\nFound {len(audio_files)} audio file(s) to process.")

        for audio_file in audio_files:
            try:
                print(f"\nProcessing: {os.path.basename(audio_file)}")

                # Transcribe the audio
                logger.info(f"Transcribing file: {audio_file}")
                transcript = transcriber.transcribe(audio_file)
                print(f"Transcript: {transcript.text}")

                # Get first three words for file naming
                title_words = " ".join(transcript.text.split()[:3])

                # Save transcription and move audio file
                transcription_path = file_manager.save_transcription(
                    transcript, title_words
                )
                audio_path = file_manager.move_audio_file(audio_file, title_words)

                logger.info(
                    f"Successfully processed file:\nTranscription: {transcription_path}\nAudio: {audio_path}"
                )
                print("✓ File processed successfully")

            except Exception as e:
                logger.error(
                    f"Error processing file {audio_file}: {str(e)}", exc_info=True
                )
                print(f"✗ Error processing file: {str(e)}")
                continue

        return True

    except Exception as e:
        logger.error(f"Error processing audio files: {str(e)}", exc_info=True)
        print(f"\nError: {str(e)}")
        return False


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
            elif command == "3":
                print("\nProcessing existing audio files...")
                process_existing_audio_files(file_manager, transcriber, logger)
            else:
                print(
                    "\nInvalid command. Please enter 1 to record, 2 to quit, or 3 to process existing files."
                )

    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        print(f"\nFatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
