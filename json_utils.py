import json
import os
import re


def save_to_json(generated_text, output_file_name):
    """
    Save the generated text to a JSON file.
    """
    output_folder = os.path.abspath('outputs')  # Specify the absolute path to the output folder
    os.makedirs(output_folder, exist_ok=True)  # Create the output folder if it doesn't exist
    print(output_file_name)
    print(output_folder)
    #output_file_path = os.path.join(output_folder, output_file_name)

    new_file_path = re.sub(r"uploads\\", r"outputs\\", output_file_name)

    with open(new_file_path, "w") as f:
        json.dump(generated_text, f)

