import os
import time
import random

from dotenv import load_dotenv
from google import genai
from google.genai.errors import ClientError, ServerError


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def generate_answer(prompt, max_retries=4):
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt
            )

            return response.text

        except (ClientError, ServerError) as error:
            status = getattr(error, "code", None)

            if status is None:
                status = getattr(error, "status_code", None)

            if status not in (429, 503):
                raise

            if attempt == max_retries - 1:
                raise

            wait_time = min(
                30,
                (2 ** attempt) * 5 + random.uniform(0, 1)
            )

            print(
                f"Gemini returned {status}. "
                f"Retrying in {wait_time:.1f}s..."
            )

            time.sleep(wait_time)

    raise RuntimeError("Gemini request failed")