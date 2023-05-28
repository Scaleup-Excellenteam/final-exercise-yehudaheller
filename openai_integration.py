from dotenv import load_dotenv
from datetime import datetime, timedelta
import asyncio
import openai
import os


# Load the environment variables from the .env file
load_dotenv()


# Counter for the number of requests made
request_counter = 0

# Last request time
last_request_time = None

# Number of requests allowed per time interval
requests_per_interval = 3

# Time interval in minutes
interval_minutes = 1


def set_api_key(api_key: str) -> None:
    """
    Sets the OpenAI API key.

    Args:
        api_key (str): The OpenAI API key.

    Returns:
        None
    """
    openai.api_key = api_key


async def integrate_openai(slides_text: list[str]) -> str:
    """
    Integrates with the OpenAI API to generate summaries for each slide text.

    Args:
        slides_text (list[str]): A list of strings, where each string represents the text from each slide.

    Returns:
        str: The generated text summary.
    """
    global request_counter
    global last_request_time

    openai.api_key = os.environ.get("API_KEY")
    model_engine = "gpt-3.5-turbo"
    final_generated_text = ""

    for i, slide_text in enumerate(slides_text):
        prompt = "Write an explanation of the following:\n"
        prompt += slide_text + "\n"

        response = await asyncio.to_thread(
            openai.ChatCompletion.create,
            model=model_engine,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": "Please Explain This"},
            ],
        )

        request_counter += 1
        last_request_time = datetime.now()

        generated_text = response.choices[0].message.content.strip()
        final_generated_text += generated_text

        if (
            i < len(slides_text) - 1
            and request_counter % requests_per_interval == 0
        ):
            time_diff = datetime.now() - last_request_time
            remaining_time = timedelta(minutes=interval_minutes) - time_diff

            if remaining_time.total_seconds() > 0:
                print("Waiting for 60 seconds before the next request...")
                await asyncio.sleep(remaining_time.total_seconds())

    return final_generated_text
