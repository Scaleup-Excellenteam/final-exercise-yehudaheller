import asyncio
import os
import shutil
import time

from os import path
from pptx_parser import read_pptx_file, get_pptx_file_path
from openai_integration import integrate_openai
from json_utils import save_to_json


async def main() -> None:
    """
    Main function to orchestrate the PowerPoint file processing and OpenAI integration.
    """

    while True:
        time.sleep(10)
        # Scan the uploads folder
        files = os.listdir('uploads')

        # Process each file
        for file in files:
            pptx_file_path = os.path.join('uploads', file)

            # Call the read_pptx_file function to read the PowerPoint file
            slides_text = read_pptx_file(pptx_file_path)
            print(slides_text)

            handle_pending_status(pptx_file_path, "add")  # move from uploads and add to pending folder
            # Integrate OpenAI asynchronously

            answer = []
            for slide in slides_text:
                generate_text = await integrate_openai(slide)
                answer.append(generate_text)
            print(answer)

            # Get the output file name based on the PowerPoint file name
            file_name_without_extension = path.splitext(pptx_file_path)[0]
            output_file_name = file_name_without_extension + ".json"

            # Save the generated text to a JSON file with the same name as the original presentation
            save_to_json(answer, output_file_name)

            # the file already created in done folder, so delete from pending folder
            handle_pending_status(pptx_file_path, "remove")




def handle_pending_status(file_path, action):
    file_name = os.path.basename(file_path)
    pending_folder = 'pending'

    if action == "add":
        if not os.path.exists(pending_folder):
            os.makedirs(pending_folder)
        # Move the file from uploads to pending folder
        shutil.move(file_path, os.path.join(pending_folder, file_name))
    elif action == "remove":
        # Remove the file from the pending folder
        file_in_pending = os.path.join(pending_folder, file_name)
        if os.path.exists(file_in_pending):
            os.remove(file_in_pending)


if __name__ == "__main__":
    asyncio.run(main())
