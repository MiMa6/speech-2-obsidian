from openai import OpenAI
from typing import List
import logging


class ThemeExtractor:
    """Extract main themes from transcribed text using OpenAI."""

    def __init__(self, api_key: str):
        """Initialize ThemeExtractor with OpenAI API key."""
        self.client = OpenAI(api_key=api_key)
        self.logger = logging.getLogger(__name__)

    def extract_themes(self, text: str, num_themes: int = 3) -> List[str]:
        """
        Extract main themes from the given text using OpenAI.

        Args:
            text (str): The transcribed text to analyze
            num_themes (int): Number of themes to extract (default: 3)

        Returns:
            List[str]: List of extracted themes
        """
        try:
            # Prepare the prompt for GPT
            prompt = f"""Extract exactly {num_themes} main themes from this text. 
            Each theme should be a single word or short phrase that captures a key topic or concept.
            Format each theme as a hashtag on its own line.
            Use camelCase or hyphens for multi-word themes (no spaces).
            Do not number the themes or add any extra text.
            
            Text: {text}
            
            Example format:
            #ArtificialIntelligence
            #DataScience
            #MachineLearning"""

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Using GPT-4 for better theme extraction
                messages=[
                    {
                        "role": "system",
                        "content": "You are a theme extraction assistant. Extract key themes and format them as hashtags, one per line. Be concise and accurate.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,  # Lower temperature for more consistent output
                max_tokens=100,
                response_format={"type": "text"},  # Ensure plain text response
            )

            # Extract themes from response
            themes = [
                line.strip()
                for line in response.choices[0].message.content.split("\n")
                if line.strip() and line.strip().startswith("#")
            ]

            self.logger.info(f"Successfully extracted {len(themes)} themes")
            return themes

        except Exception as e:
            self.logger.error(f"Error extracting themes: {str(e)}")
            raise
