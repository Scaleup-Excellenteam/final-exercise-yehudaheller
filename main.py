import json
import collections.abc

from pptx import Presentation
import openai

#API_KEY = "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"



def save_to_json(generate_text, file_name):
    with open(file_name, "w") as f:
        json.dump(generate_text, f)


def read_pptx_file():
    # Prompt the user to enter the path to the PowerPoint file
    filename = input("Enter the path to the PowerPoint file: ")

    # Open the PowerPoint file
    prs = Presentation(filename)

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

    # Choose an AI model
    model_engine = "gpt-3.5-turbo"

    # Create a prompt (add the quotation to the text of the presentation)
    prompt = "Write a summary of the following slides:\n"
    for slide_text in slides_text:
        prompt += slide_text + "\n"

    # Generate text
    response = openai.ChatCompletion.create(
        model=model_engine,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": "summarize the slides"},
        ],
        max_tokens=512
    )

    # Save the generated text
    generate_text = response.choices[0].message.content.strip()
    generate_text = generate_text.replace(". ", ".\n")

    return generate_text




def main():
    # Call the read_pptx_file function to read the PowerPoint file
    slides_text = read_pptx_file()
    print(slides_text)

    # Integrate OpenAI
    generate_text = integrate_openai(slides_text)
    print(generate_text)

    # Save the generated text to a JSON file
    save_to_json(generate_text, "generated_text.json")


if __name__ == "__main__":
    main()
