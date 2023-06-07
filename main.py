import asyncio
import os

from os import path
from pptx_parser import read_pptx_file, get_pptx_file_path
from openai_integration import integrate_openai
from json_utils import save_to_json


async def main() -> None:
    """
    Main function to orchestrate the PowerPoint file processing and OpenAI integration.
    """

    while True:
        asyncio.sleep(10)
        # Scan the uploads folder
        files = os.listdir('uploads')

        # Process each file
        for file in files:
            pptx_file_path = os.path.join('uploads', file)

            # Call the read_pptx_file function to read the PowerPoint file
            slides_text = read_pptx_file(pptx_file_path)
            print(slides_text)

            # Integrate OpenAI asynchronously
            generate_text = await integrate_openai(slides_text)
            print(generate_text)

            # Get the output file name based on the PowerPoint file name
            file_name_without_extension = path.splitext(pptx_file_path)[0]
            output_file_name = file_name_without_extension + ".json"

            # Save the generated text to a JSON file with the same name as the original presentation
            save_to_json(generate_text, output_file_name)


if __name__ == "__main__":
    asyncio.run(main())
