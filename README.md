# Obsidian automation

## Speech to text (OpenAI API)

Speech-to-text.py script saves speech (.webm audio file) as text (.md) from Audios/Translate to Audios/SpeechToText inside your obsidian vault

</br>

### Preconfiguration:

* Set OBSIDIAN_VAULT_PATH and [OPENAI_API_KEY](https://platform.openai.com/api-keys) env variables before running speech-to-text.py
* Create Audios/Translate and Audios/SpeechToText directories to your obsidian vault

</br>

### Steps:

* Code reads .webm file from Audios/translate
* Saves speech as .md file to Audios/SpeechToText
* Moves .webm file to Audios/translated
