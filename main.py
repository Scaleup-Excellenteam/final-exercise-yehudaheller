import json
import collections
import collections.abc
import time

import pptx
import openai

#API_KEY = "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"
API_KEY = "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"




def save_to_json(generate_text, file_name):
    with open(file_name, "w") as f:
        json.dump(generate_text, f)


def read_pptx_file():
    # Prompt the user to enter the path to the PowerPoint file
    filename = input("Enter the path to the PowerPoint file: ")

    # Open the PowerPoint file
    prs = pptx.Presentation(filename)

    # Initialize an empty list to hold the text from each slide
    slides_text = []

    # Loop through each slide in the presentation
    for slide in prs.slides:
        # Initialize an empty string to hold the text from the slide
        text = ""

        # Loop through each shape in the slide
        for shape in slide.shapes:
            # Check if the shape has text
            if shape.has_text_frame:
                # Loop through each paragraph in the text frame
                for paragraph in shape.text_frame.paragraphs:
                    # Add the text from the paragraph to the string
                    text += paragraph.text

        # Append the slide's text to the slide_text list
        slides_text.append(text)

    return slides_text


def integrate_openai(slides_text):
    # Set the OpenAI API key
    openai.api_key = API_KEY

    # Set the API endpoint for the free plan
    openai.api_base = "https://api.openai.com/v1/"

    # Choose an AI model
    model_engine = "gpt-3.5-turbo"

    # Create a prompt
    prompt = "Write a summary of the following slides: "
    for slide_text in slides_text:
        prompt += slide_text + "\n"


    print(prompt)
    # Generate text
    response = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=5
    )

    # Save the generated text
    generate_text = response.choices[0].text.strip()

    return generate_text


if __name__ == "__main__":
    # Call the read_pptx_file function to read the PowerPoint file
    slides_text = read_pptx_file()
    # print(slides_text)

    # Integrate OpenAI
    generate_text = integrate_openai(slides_text)
    print(generate_text)

    # Save the generated text to a JSON file
    save_to_json(generate_text, "generated_text.json")

