import os
import fnmatch
import shutil


class FileManager:
    def __init__(self, vault_path):
        self.audio_input_dir = os.path.join(vault_path, "Audios/Translate")
        self.audio_output_dir = os.path.join(vault_path, "Audios/Translated")
        self.text_output_dir = os.path.join(vault_path, "Audios/SpeechToText")

        # Ensure directories exist
        for directory in [
            self.audio_input_dir,
            self.audio_output_dir,
            self.text_output_dir,
        ]:
            os.makedirs(directory, exist_ok=True)

    def find_audio_files(self):
        """Find all audio files in the input directory."""
        audio_files = []
        for dirpath, dirnames, filenames in os.walk(self.audio_input_dir):
            for extension in ["m4a", "webm", "wav"]:
                for filename in fnmatch.filter(filenames, "*." + extension):
                    audio_files.append(os.path.join(dirpath, filename))
        return audio_files

    def save_transcription(self, transcript, title_words=None):
        """Save transcription to a markdown file."""
        if title_words is None:
            # Use first three words of transcript as filename
            title_words = " ".join(transcript.text.split()[:3])

        filename = f"{title_words}.md"
        file_path = os.path.join(self.text_output_dir, filename)

        print(f"Saving transcription to: {file_path}")
        with open(file_path, "w") as file:
            file.write('"' + transcript.text + '"')
        print("Saving completed!")
        return file_path

    def move_audio_file(self, source_path, title_words=None):
        """Move processed audio file to output directory."""
        if title_words is None:
            # Use original filename without extension
            title_words = os.path.splitext(os.path.basename(source_path))[0]

        # Keep original extension
        extension = os.path.splitext(source_path)[1]
        new_filename = f"{title_words}{extension}"
        destination_path = os.path.join(self.audio_output_dir, new_filename)

        # Ensure output directory exists
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)

        print(f"Moving audio file:\nFrom: {source_path}\nTo: {destination_path}")
        shutil.move(source_path, destination_path)
        return destination_path
