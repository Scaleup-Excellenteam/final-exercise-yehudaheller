import asyncio
import os
from time import time
import openai
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")

RATE_LIMIT = 3

request_count = 0
last_request_time = 0


async def integrate_openai(prompt: str) -> str:
    global request_count, last_request_time

    current_time = time()
    time_elapsed = current_time - last_request_time

    prompt_request = "please explain me this slide: " + prompt
    if time_elapsed < 60 and request_count >= RATE_LIMIT:
        await asyncio.sleep(60 - time_elapsed)
        request_count = 0
        last_request_time = current_time

    openai.api_key = API_KEY
    response = await asyncio.to_thread(openai.ChatCompletion.create,
                                       model="gpt-3.5-turbo",
                                       messages=[
                                           {"role": "user", "content": prompt_request}
                                       ],
                                       )

    request_count += 1
    last_request_time = time()

    return response['choices'][0]['message']['content'].strip() if 'choices' in response else "(Empty slide)"
