import os
import fnmatch
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI

_ = load_dotenv(find_dotenv())


OBSIDIAN_VAULT_PATH = os.environ.get("OBSIDIAN_VAULT_PATH")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

audio_file_directory = f"{OBSIDIAN_VAULT_PATH}/Audios/Translate"
output_directory = f"{OBSIDIAN_VAULT_PATH}/Audios/SpeechToText"


def find_audio_files():
    webm_files = []
    for dirpath, dirnames, filenames in os.walk(audio_file_directory):
        for extension in ["m4a", "webm"]:
            for filename in fnmatch.filter(filenames, "*." + extension):
                webm_files.append(os.path.join(dirpath, filename))

    return webm_files


def save_transcription(transcript, file_path):
    print(f"Saving transcription to: \n {file_path}")
    with open(file_path, "w") as file:
        file.write('"' + transcript.text + '"')
        print("Saving completed!")


def move_transcripted_file_to_done(file_path, file_name):
    file_path_transformed = file_path.replace("Translate", "Translated")
    dir_path = os.path.dirname(file_path_transformed)

    output_path = f"{dir_path}/{file_name}"

    print(f"Moving and transforming file: {file_path} \n To {output_path}")

    with open(file_path, "rb") as source_file, open(output_path, "wb") as dest_file:
        dest_file.write(source_file.read())

    os.remove(file_path)


def speech_to_text(fileToTranslate):
    audio_file = open(fileToTranslate, "rb")
    print("audio_file")
    print(audio_file)
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        language="en",
    )
    return transcript


def main():

    audio_files = find_audio_files()

    if audio_files == []:
        print("No audio files found")
        return

    for audio_file_to_traslate in audio_files:
        print(f"File to translate: \n", audio_file_to_traslate)

        transcript = speech_to_text(audio_file_to_traslate)
        print(f"Transcript: \n", transcript.text)

        first_three_words_of_transcript_list = transcript.text.split(" ")[:3]
        first_three_words_of_transcript = " ".join(first_three_words_of_transcript_list)

        output_md_file_name = f"{first_three_words_of_transcript}.md"
        output_webm_file_name = f"{first_three_words_of_transcript}.webm"
        output_file_path = os.path.join(output_directory, output_md_file_name)

        save_transcription(transcript, output_file_path)
        move_transcripted_file_to_done(audio_file_to_traslate, output_webm_file_name)


if __name__ == "__main__":
    main()
