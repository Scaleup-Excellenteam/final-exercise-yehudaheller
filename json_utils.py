from json import dump
from os import path, makedirs


def save_to_json(generated_text, output_file_name):
    """
    Save the generated text to a JSON file in the 'outputs' folder.
    """

    output_folder = path.abspath('outputs')  # Specify the absolute path to the output folder
    makedirs(output_folder, exist_ok=True)  # Create the output folder if it doesn't exist

    # Create the new file path by replacing the original folder with the 'outputs' folder
    new_file_path = path.join(output_folder, path.basename(output_file_name))
    print(f"new_file_path is {new_file_path}")
    with open(new_file_path, "w") as f:
        dump(generated_text, f)
