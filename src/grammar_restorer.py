from openai import OpenAI
import logging


class GrammarRestorer:
    """Restore punctuation and paragraph breaks using OpenAI."""

    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.logger = logging.getLogger(__name__)

    def restore(self, text: str) -> str:
        """
        Add punctuation and paragraph breaks to the given text using OpenAI.
        """
        try:
            prompt = (
                "You will receive a block of text with no punctuation or paragraph breaks. "
                "Return the text with correct punctuation and add new lines at paragraph breaks. "
                "Do not change the meaning or add extra content.\n\n"
                f"Text: {text}"
            )
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that restores punctuation and paragraph breaks.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                response_format={"type": "text"},
            )
            restored_text = response.choices[0].message.content.strip()
            self.logger.info("Successfully restored grammar and punctuation.")
            return restored_text
        except Exception as e:
            self.logger.error(f"Error restoring grammar: {str(e)}")
            raise
