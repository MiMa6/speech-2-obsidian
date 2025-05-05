import os
import fnmatch
import shutil
from datetime import datetime
import re
import logging
from typing import Optional, Tuple, List


class FileManagerError(Exception):
    """Custom exception for FileManager errors"""

    pass


class FileManager:
    def __init__(self, vault_path: str):
        """Initialize FileManager with vault path and setup logging."""
        self.logger = logging.getLogger(__name__)

        # Set up directory paths
        self.audio_input_dir = os.path.join(vault_path, "Audios", "Translate")
        self.audio_output_dir = os.path.join(vault_path, "Audios", "Translated")
        self.text_output_dir = os.path.join(vault_path, "Audios", "SpeechToText")

        # Create all required directories
        self._create_directory_structure()

    def _create_directory_structure(self):
        """Create all required directories if they don't exist."""
        directories = [
            self.audio_input_dir,
            self.audio_output_dir,
            self.text_output_dir,
        ]

        for directory in directories:
            try:
                if not os.path.exists(directory):
                    os.makedirs(directory)
                    self.logger.info(f"Created directory: {directory}")
                else:
                    self.logger.debug(f"Directory already exists: {directory}")
            except PermissionError as e:
                raise FileManagerError(
                    f"Permission denied creating directory {directory}: {e}"
                )
            except Exception as e:
                raise FileManagerError(f"Error creating directory {directory}: {e}")

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
            directory = os.path.dirname(path)
            if not os.path.exists(directory):
                os.makedirs(directory)
                self.logger.info(f"Created directory: {directory}")
        except Exception as e:
            raise FileManagerError(f"Error creating directory for path {path}: {e}")

    def _create_date_directory(
        self, base_dir: str, year: str, month: str, day: str
    ) -> str:
        """Create and return a date-based directory structure."""
        date_dir = os.path.join(base_dir, year, month, day)
        try:
            os.makedirs(date_dir, exist_ok=True)
            self.logger.info(f"Created/verified directory structure: {date_dir}")
            return date_dir
        except Exception as e:
            raise FileManagerError(
                f"Failed to create directory structure {date_dir}: {e}"
            )

    def save_transcription(
        self,
        transcript,
        title_words: Optional[str] = None,
        themes: Optional[List[str]] = None,
    ) -> str:
        """Save transcription to a markdown file in year/month/day structure."""
        try:
            # Accept both string and object with .text
            if isinstance(transcript, str):
                transcript_text = transcript
            else:
                transcript_text = transcript.text

            if title_words is None:
                title_words = " ".join(transcript_text.split()[:3])

            current_date = datetime.now()
            timestamp = current_date.strftime("%Y_%m_%d__%H_%M")
            year = current_date.strftime("%Y")
            month = current_date.strftime("%m")
            day = current_date.strftime("%d")

            # Create the date-based directory structure
            date_dir = self._create_date_directory(
                self.text_output_dir, year, month, day
            )

            filename = f"{timestamp}_{title_words}.md"
            file_path = os.path.join(date_dir, filename)

            self.logger.info(f"Saving transcription to: {file_path}")

            # Format content with transcription and themes
            content = [f'"{transcript_text}"']

            # Add themes if provided, each on a new line
            if themes:
                content.extend([""] + themes)

            # Write content to file
            with open(file_path, "w", encoding="utf-8") as file:
                file.write("\n".join(content))

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

            # Create the date-based directory structure
            date_dir = self._create_date_directory(
                self.audio_output_dir, year, month, day
            )

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
