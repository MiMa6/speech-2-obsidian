import os
import sys
import logging
import sounddevice as sd
from src.audio_recorder import AudioRecorder
from src.transcriber import Transcriber
from src.file_manager import FileManager, FileManagerError
from src.config import Config
from src.settings import Settings
from src.voice_memos import find_latest_recording
from src.theme_extractor import ThemeExtractor
from pydub import AudioSegment


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


def load_settings() -> Settings:
    """Load and validate settings from environment variables."""
    try:
        return Settings()
    except Exception as e:
        print(f"Error loading settings: {str(e)}")
        sys.exit(1)


def process_recording(file_manager, recorder, transcriber, theme_extractor, logger):
    """Handle the recording and transcription process."""
    try:
        logger.info("Starting new recording session")
        audio_file = recorder.record()

        logger.info("Converting speech to text")
        transcript = transcriber.transcribe(audio_file)
        print(f"\nTranscript: {transcript.text}")

        # Extract themes
        logger.info("Extracting themes from transcript")
        themes = theme_extractor.extract_themes(transcript.text)
        print("\nExtracted themes:", ", ".join(themes))

        # Get first three words for file naming
        title_words = " ".join(transcript.text.split()[:3])

        # Save transcription and move audio file
        transcription_path = file_manager.save_transcription(
            transcript, title_words, themes
        )
        audio_path = file_manager.move_audio_file(audio_file, title_words)

        logger.info(
            f"Successfully processed recording:\nTranscription: {transcription_path}\nAudio: {audio_path}"
        )
        return True

    except Exception as e:
        logger.error(f"Error processing recording: {str(e)}", exc_info=True)
        print(f"\nError: {str(e)}")
        return False


def process_voice_memo(file_manager, transcriber, theme_extractor, logger):
    """Process the latest voice memo from iPhone."""
    try:
        # Find latest voice memo
        latest_memo = find_latest_recording()
        if not latest_memo:
            print("\nNo valid voice memo found.")
            return False

        print(f"\nProcessing latest voice memo: {os.path.basename(latest_memo)}")

        # Transcribe the audio
        logger.info(f"Transcribing voice memo: {latest_memo}")
        transcript = transcriber.transcribe(latest_memo)
        print(f"Transcript: {transcript.text}")

        # Extract themes
        logger.info("Extracting themes from transcript")
        themes = theme_extractor.extract_themes(transcript.text)
        print("\nExtracted themes:", ", ".join(themes))

        # Get first three words for file naming
        title_words = " ".join(transcript.text.split()[:3])

        # Save transcription and copy audio file
        transcription_path = file_manager.save_transcription(
            transcript, title_words, themes
        )
        audio_path = file_manager.move_audio_file(latest_memo, title_words)

        logger.info(
            f"Successfully processed voice memo:\nTranscription: {transcription_path}\nAudio: {audio_path}"
        )
        print("✓ Voice memo processed successfully")
        return True

    except Exception as e:
        logger.error(f"Error processing voice memo: {str(e)}", exc_info=True)
        print(f"\nError: {str(e)}")
        return False


def display_menu():
    """Display the main menu options."""
    print("\nAvailable commands:")
    print("1: Record new audio")
    print("2: Quit")
    print("3: Translate existing audio files in 'Translate' Obsidian folder")
    print("4: Translate latest audio file in 'Voice memo' App (Mac & iOS)")
    print("5: Split audio files in 'Translate' folder (Audio splitter)")
    return input("\nEnter command (1-5): ").strip()


def process_existing_audio_files(file_manager, transcriber, theme_extractor, logger):
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

                # Extract themes
                logger.info("Extracting themes from transcript")
                themes = theme_extractor.extract_themes(transcript.text)
                print("\nExtracted themes:", ", ".join(themes))

                # Get first three words for file naming
                title_words = " ".join(transcript.text.split()[:3])

                # Save transcription and move audio file
                transcription_path = file_manager.save_transcription(
                    transcript, title_words, themes
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


MAX_AUDIO_CHUNK_SIZE = 25 * 1024 * 1024  # 25 MB


def split_audio_files_in_translate(file_manager, logger):
    """Split audio files in the Translate folder into chunks under 25MB."""
    try:
        audio_files = file_manager.find_audio_files()
        if not audio_files:
            print("\nNo audio files found in the Translate directory.")
            return False

        print(f"\nFound {len(audio_files)} audio file(s) to split.")
        for audio_file in audio_files:
            try:
                print(f"\nSplitting: {os.path.basename(audio_file)}")
                logger.info(f"Splitting file: {audio_file}")
                audio = AudioSegment.from_file(audio_file)
                chunk_length_ms = 60 * 1000  # Start with 1 minute
                chunks = []
                start = 0
                part = 1
                while start < len(audio):
                    end = start + chunk_length_ms
                    chunk = audio[start:end]
                    # Adjust chunk size to stay under 25MB
                    while (
                        len(chunk.raw_data) > MAX_AUDIO_CHUNK_SIZE
                        and chunk_length_ms > 10 * 1000
                    ):
                        chunk_length_ms -= 10 * 1000  # Reduce by 10 seconds
                        end = start + chunk_length_ms
                        chunk = audio[start:end]
                    if len(chunk.raw_data) > MAX_AUDIO_CHUNK_SIZE:
                        print(
                            f"✗ Cannot split {os.path.basename(audio_file)} into small enough chunks. Skipping."
                        )
                        logger.error(
                            f"Chunk too large for {audio_file} even after reducing chunk size."
                        )
                        break
                    # Save chunk
                    base, ext = os.path.splitext(audio_file)
                    chunk_filename = f"{base}_p{part}{ext}"
                    chunk.export(chunk_filename, format=ext[1:])
                    print(f"✓ Saved chunk: {os.path.basename(chunk_filename)}")
                    logger.info(f"Saved chunk: {chunk_filename}")
                    part += 1
                    start = end
            except Exception as e:
                print(
                    f"✗ Error splitting file {os.path.basename(audio_file)}: {str(e)}"
                )
                logger.error(
                    f"Error splitting file {audio_file}: {str(e)}", exc_info=True
                )
                continue
        print("\nAudio splitting complete.")
        return True
    except Exception as e:
        logger.error(f"Error splitting audio files: {str(e)}", exc_info=True)
        print(f"\nError: {str(e)}")
        return False


def main():
    logger = setup_logging()
    logger.info("Starting Speech-to-Text Converter")

    try:
        # Load and validate settings
        settings = load_settings()

        # Initialize components
        file_manager = FileManager(settings.OBSIDIAN_VAULT_PATH)
        recorder = AudioRecorder(
            file_manager.audio_input_dir, mic_name=settings.MICROPHONE_NAME
        )
        transcriber = Transcriber(settings.OPENAI_API_KEY)
        theme_extractor = ThemeExtractor(settings.OPENAI_API_KEY)

        print("\n=== Speech-to-Text Converter ===")
        print("This program will record your voice and convert it to text.")

        while True:
            command = display_menu()

            if command == "2":
                logger.info("User requested to quit")
                print("Goodbye!")
                break
            elif command == "1":
                process_recording(
                    file_manager, recorder, transcriber, theme_extractor, logger
                )
            elif command == "3":
                print("\nProcessing existing audio files...")
                process_existing_audio_files(
                    file_manager, transcriber, theme_extractor, logger
                )
            elif command == "4":
                print("\nProcessing latest iPhone voice memo...")
                process_voice_memo(file_manager, transcriber, theme_extractor, logger)
            elif command == "5":
                print("\nSplitting audio files in Translate folder...")
                split_audio_files_in_translate(file_manager, logger)
            else:
                print(
                    "\nInvalid command. Please enter 1 to record, 2 to quit, 3 to process existing files, 4 for voice memo, or 5 for audio splitter."
                )

    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        print(f"\nFatal error: {str(e)}")
        sys.exit(1)
    finally:
        # Clean up sounddevice resources
        sd.stop()
        sys.exit(0)


if __name__ == "__main__":
    main()
