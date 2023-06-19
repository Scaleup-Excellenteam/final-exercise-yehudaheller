import json
import os

def save_to_json(generated_text, output_file_name):
    """
    Save the generated text to a JSON file in the 'outputs' folder.
    """
    print(f"output_file_name is {output_file_name}")

    output_folder = os.path.abspath('outputs')  # Specify the absolute path to the output folder
    os.makedirs(output_folder, exist_ok=True)  # Create the output folder if it doesn't exist

    # Create the new file path by replacing the original folder with the 'outputs' folder
    new_file_path = os.path.join(output_folder, os.path.basename(output_file_name))
    print(f"new_file_path is {new_file_path}")
    with open(new_file_path, "w") as f:
        json.dump(generated_text, f)
