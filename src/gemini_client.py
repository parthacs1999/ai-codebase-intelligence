import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai.errors import ServerError

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def generate_answer(prompt, max_retries=3):

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
            )

            return response.text

        except ServerError as error:

            if error.code == 503:
                if attempt < max_retries - 1:
                    wait_time = 2**attempt
                    print(f"Gemini unavailable. " f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    return (
                        "Gemini is temporarily unavailable. " "Please try again later."
                    )

            else:
                raise
