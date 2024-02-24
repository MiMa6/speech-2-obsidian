# Obsidian automation

## Speech to text (OpenAI API)

<p> 
  speech-to-text.py saves speech (.webm audio file) as text (.md) to the specified obsidian vault directory. 
<p>

Steps:
* set OBSIDIAN_VAULT_PATH and [OPENAI_API_KEY](https://platform.openai.com/api-keys) env variables
* Code reads .webm file from Audios/translate
* Saves speech as .md file to Audios/SpeechToText
* Moves .webm file to Audios/translated
