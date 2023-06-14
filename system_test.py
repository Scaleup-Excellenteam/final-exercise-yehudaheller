import subprocess
import time
import os
import requests
from bs4 import BeautifulSoup

from app import find_file_by_uid

SAMPLE_PPTX_TO_TEST = 'pres3.pptx'  # file in folder of the project


def run_system_test():
    # Step 1: Start the app.py file
    app_process = subprocess.Popen(['python', 'app.py'], cwd=os.getcwd())

    # Wait for the app to start
    time.sleep(2)

    # Step 2: Start the main.py file
    main_process = subprocess.Popen(['python', 'main.py'], cwd=os.getcwd())

    # Wait for the main process to start
    time.sleep(2)
    time.sleep(30)

    # Step 3: Upload the test file using the app's API endpoint
    upload_url = 'http://localhost:5000/'

    with open(SAMPLE_PPTX_TO_TEST, 'rb') as file:
        response = requests.post(upload_url, files={'file': file})

    if response.status_code != 200:
        print("Test failed: File upload failed")
        app_process.terminate()
        main_process.terminate()
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    uid_input = soup.find('input', attrs={'name': 'uid'})
    uid_for_user = uid_input['value']

    print(f"The uid is {uid_for_user}")

    # Find the output file based on the UID
    output_file = find_file_by_uid(uid_for_user)

    output_file_with_json_ending = output_file.split(".")[0] + ".json"
    print(f"The output file is {output_file_with_json_ending}")

    # Restart the main process
    main_process = subprocess.Popen(['python', 'main.py'], cwd=os.getcwd())

    # Wait for the main process to start
    time.sleep(2)
    time.sleep(30)  # Adjust the delay as needed

    # Verify the output file in the done folder
    expected_output_file = f'outputs/{output_file_with_json_ending}'
    if not os.path.exists(expected_output_file):
        print("Test failed: Output file not found")
        app_process.terminate()
        main_process.terminate()
        return

    print("System test completed successfully")

    # Stop the processes
    app_process.terminate()
    main_process.terminate()


run_system_test()
