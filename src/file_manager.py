import os
import fnmatch
import shutil
from datetime import datetime
import re
import logging
from typing import Optional, Tuple


class FileManagerError(Exception):
    """Custom exception for FileManager errors"""

    pass


class FileManager:
    def __init__(self, vault_path: str):
        """Initialize FileManager with vault path and setup logging."""
        self.logger = logging.getLogger(__name__)
        self.audio_input_dir = os.path.join(vault_path, "Audios/Translate")
        self.audio_output_dir = os.path.join(vault_path, "Audios/Translated")
        self.text_output_dir = os.path.join(vault_path, "Audios/SpeechToText")

        try:
            # Ensure directories exist
            for directory in [
                self.audio_input_dir,
                self.audio_output_dir,
                self.text_output_dir,
            ]:
                os.makedirs(directory, exist_ok=True)
                self.logger.info(f"Ensured directory exists: {directory}")
        except PermissionError as e:
            raise FileManagerError(f"Permission denied creating directories: {e}")
        except Exception as e:
            raise FileManagerError(f"Error creating directories: {e}")

    def _extract_date_from_filename(
        self, filename: str
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Extract date components from filename with pattern YYYY_MM_DD__HH_MM"""
        try:
            match = re.search(r"(\d{4})_(\d{2})_(\d{2})__", filename)
            if match:
                year, month, day = match.groups()
                return year, month, day
            return None, None, None
        except Exception as e:
            self.logger.warning(f"Error extracting date from filename {filename}: {e}")
            return None, None, None

    def _ensure_valid_path(self, path: str) -> None:
        """Validate and ensure path exists."""
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
        except Exception as e:
            raise FileManagerError(f"Error creating directory for path {path}: {e}")

    def save_transcription(self, transcript, title_words: Optional[str] = None) -> str:
        """Save transcription to a markdown file in year/month/day structure."""
        try:
            if title_words is None:
                title_words = " ".join(transcript.text.split()[:3])

            current_date = datetime.now()
            timestamp = current_date.strftime("%Y_%m_%d__%H_%M")

            # Create year/month/day directory structure
            year = current_date.strftime("%Y")
            month = current_date.strftime("%m")
            day = current_date.strftime("%d")

            date_dir = os.path.join(self.text_output_dir, year, month, day)
            self._ensure_valid_path(date_dir)

            filename = f"{timestamp}_{title_words}.md"
            file_path = os.path.join(date_dir, filename)

            self.logger.info(f"Saving transcription to: {file_path}")
            with open(file_path, "w", encoding="utf-8") as file:
                file.write('"' + transcript.text + '"')
            self.logger.info("Transcription saved successfully")
            return file_path

        except Exception as e:
            raise FileManagerError(f"Error saving transcription: {e}")

    def move_audio_file(
        self, source_path: str, title_words: Optional[str] = None
    ) -> str:
        """Move processed audio file to year/month/day structure."""
        try:
            if not os.path.exists(source_path):
                raise FileManagerError(f"Source audio file not found: {source_path}")

            if title_words is None:
                title_words = os.path.splitext(os.path.basename(source_path))[0]

            source_filename = os.path.basename(source_path)
            year, month, day = self._extract_date_from_filename(source_filename)

            if not all([year, month, day]):
                current_date = datetime.now()
                year = current_date.strftime("%Y")
                month = current_date.strftime("%m")
                day = current_date.strftime("%d")
                timestamp = current_date.strftime("%Y_%m_%d__%H_%M")
            else:
                timestamp_match = re.search(
                    r"(\d{4}_\d{2}_\d{2}__\d{2}_\d{2})", source_filename
                )
                if not timestamp_match:
                    raise FileManagerError(
                        f"Invalid timestamp format in filename: {source_filename}"
                    )
                timestamp = timestamp_match.group(1)

            date_dir = os.path.join(self.audio_output_dir, year, month, day)
            self._ensure_valid_path(date_dir)

            extension = os.path.splitext(source_path)[1]
            new_filename = f"{timestamp}_{title_words}{extension}"
            destination_path = os.path.join(date_dir, new_filename)

            self.logger.info(
                f"Moving audio file from {source_path} to {destination_path}"
            )
            shutil.move(source_path, destination_path)
            return destination_path

        except FileManagerError:
            raise
        except Exception as e:
            raise FileManagerError(f"Error moving audio file: {e}")

    def find_audio_files(self) -> list:
        """Find all audio files in the input directory."""
        try:
            audio_files = []
            for dirpath, _, filenames in os.walk(self.audio_input_dir):
                for extension in ["m4a", "webm", "wav"]:
                    for filename in fnmatch.filter(filenames, "*." + extension):
                        audio_files.append(os.path.join(dirpath, filename))
            return audio_files
        except Exception as e:
            raise FileManagerError(f"Error finding audio files: {e}")
