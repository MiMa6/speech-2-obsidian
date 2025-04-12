from dataclasses import dataclass
from typing import List
import os


@dataclass
class AudioConfig:
    SILENCE_THRESHOLD: float = 0.02
    SILENCE_DURATION: float = 2.0
    MAX_DURATION: int = 300
    DEFAULT_MIC_NAME: str = "MacBook Pro Microphone"
    SUPPORTED_FORMATS: List[str] = ("m4a", "webm", "wav")


@dataclass
class FileConfig:
    TIMESTAMP_FORMAT: str = "%Y_%m_%d__%H_%M_%S"
    DATE_FORMAT: str = "%Y/%m/%d"
    AUDIO_DIRS: List[str] = ("Translate", "Translated", "SpeechToText")


@dataclass
class LogConfig:
    LOG_DIR: str = "logs"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE_FORMAT: str = "%Y_%m_%d.log"  # Will create daily log files
    LOG_LEVEL: str = "INFO"

    def get_log_path(self) -> str:
        """Get the full path for the log file with today's date."""
        from datetime import datetime

        # Create logs directory if it doesn't exist
        os.makedirs(self.LOG_DIR, exist_ok=True)

        # Generate log filename with today's date
        log_filename = datetime.now().strftime(self.LOG_FILE_FORMAT)
        return os.path.join(self.LOG_DIR, log_filename)


@dataclass
class Config:
    audio: AudioConfig = AudioConfig()
    file: FileConfig = FileConfig()
    log: LogConfig = LogConfig()

    @classmethod
    def get_instance(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance
