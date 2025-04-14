from pydantic import BaseModel, Field
from typing import List, ClassVar, Optional
import os
from datetime import datetime


class AudioConfig(BaseModel):
    SILENCE_THRESHOLD: float = Field(
        0.02, description="Threshold for detecting silence"
    )
    SILENCE_DURATION: float = Field(
        2.0, description="Duration of silence before stopping"
    )
    MAX_DURATION: int = Field(300, description="Maximum recording duration in seconds")
    DEFAULT_MIC_NAME: str = Field(
        "MacBook Pro Microphone", description="Default microphone name"
    )
    SUPPORTED_FORMATS: List[str] = Field(
        default=["m4a", "webm", "wav"], description="Supported audio formats"
    )


class FileConfig(BaseModel):
    TIMESTAMP_FORMAT: str = Field(
        "%Y_%m_%d__%H_%M_%S", description="Format for timestamps in filenames"
    )
    DATE_FORMAT: str = Field(
        "%Y/%m/%d", description="Format for date-based directory structure"
    )
    AUDIO_DIRS: List[str] = Field(
        default=["Translate", "Translated", "SpeechToText"],
        description="Audio directory names",
    )


class LogConfig(BaseModel):
    LOG_DIR: str = Field("logs", description="Directory for log files")
    LOG_FORMAT: str = Field(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format",
    )
    LOG_FILE_FORMAT: str = Field("%Y_%m_%d.log", description="Log filename format")
    LOG_LEVEL: str = Field("INFO", description="Logging level")

    def get_log_path(self) -> str:
        """Get the full path for the log file with today's date."""
        os.makedirs(self.LOG_DIR, exist_ok=True)
        log_filename = datetime.now().strftime(self.LOG_FILE_FORMAT)
        return os.path.join(self.LOG_DIR, log_filename)


class Config(BaseModel):
    """Application configuration singleton."""

    audio: AudioConfig = Field(default_factory=AudioConfig)
    file: FileConfig = Field(default_factory=FileConfig)
    log: LogConfig = Field(default_factory=LogConfig)

    # Class variable to store the singleton instance
    _instance: ClassVar[Optional["Config"]] = None

    class Config:
        validate_assignment = True  # Validate values when they're assigned
        extra = "forbid"  # Prevent extra attributes from being set

    @classmethod
    def get_instance(cls) -> "Config":
        """Get or create the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
