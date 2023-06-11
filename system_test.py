import subprocess
import time
import requests

web_api_process = None
explainer_process = None


def start_web_api():
    """
    Start the Web API process.
    """
    global web_api_process
    web_api_process = subprocess.Popen(["python", "app.py"])
    time.sleep(2)


def start_explainer():
    """
    Start the Explainer process.
    """
    global explainer_process
    explainer_process = subprocess.Popen(["python", "main.py"])
    time.sleep(2)


def upload_sample_presentation():
    """
    Upload a sample presentation using the Python Client.

    Returns:
        str: The UID (unique identifier) of the uploaded presentation.
    """
    upload_url = "http://localhost:5000/"
    file_path = "pres3.pptx"
    files = {"file": open(file_path, "rb")}
    response = requests.post(upload_url, files=files)

    assert response.status_code == 200, f"Failed to upload the sample presentation. Error: {response.json()['message']}"

    data = response.json()
    uid = data["uid"]
    print(f"Sample presentation uploaded successfully. UID: {uid}")
    return uid


def check_presentation_status(uid):
    """
    Check the status of the uploaded presentation using the Python Client.

    Args:
        uid (str): The UID (unique identifier) of the presentation.

    Returns:
        dict: Dictionary containing the presentation status, filename, timestamp, and explanation.
    """
    check_url = f"http://localhost:5000/check_file?uid={uid}"
    response = requests.get(check_url)

    assert response.status_code == 200, f"Failed to check the status of the presentation. Error: {response.json()['message']}"

    data = response.json()
    status = data["status"]
    filename = data["filename"]
    timestamp = data["timestamp"]
    explanation = data["explanation"]

    print(f"Status: {status}")
    print(f"Filename: {filename}")
    print(f"Timestamp: {timestamp}")
    print(f"Explanation: {explanation}")
    return data


def stop_processes():
    """
    Stop the Web API and Explainer processes.
    """
    global web_api_process, explainer_process
    web_api_process.terminate()
    explainer_process.terminate()

def main():
    """
    Main function to execute the workflow.
    """
    start_web_api()
    start_explainer()
    time.sleep(5)
    uid = upload_sample_presentation()
    check_presentation_status(uid)
    stop_processes()


if __name__ == "__main__":
    main()