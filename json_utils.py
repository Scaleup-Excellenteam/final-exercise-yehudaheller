import json


def save_to_json(generate_text: str, file_name: str) -> None:
    """
    Saves the generated text to a JSON file.

    Args:
        generate_text (str): The generated text to be saved.
        file_name (str): The name of the JSON file to save.

    Returns:
        None
    """
    with open(file_name, "w") as f:
        json.dump(generate_text, f)
