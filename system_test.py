import asyncio
import requests

SAMPLE_FILE = 'pres3.pptx'

async def system_test():
    # Starts the Web API
    global explainer_process
    api_process = await asyncio.create_subprocess_exec('python', 'app.py')

    # Wait for the Web API to start
    await asyncio.sleep(5)

    try:
        # Starts the Explainer
        explainer_process = await asyncio.create_subprocess_exec('python', 'openai_integration.py')

        # Wait for the Explainer to start
        await asyncio.sleep(5)

        # Use the Python Client to upload a sample presentation
        upload_url = 'http://localhost:5000/'
        files = {'file': open(SAMPLE_FILE, 'rb')}
        response = requests.post(upload_url, files=files)
        if response.status_code != 200:
            print('Failed to upload the presentation.')
            return


        status_url = f'http://localhost:5000/status'
        response = requests.get(status_url)
        if response.status_code != 200:
            print('Failed to get the status of the presentation.')
            return

        # Print the status
        print(response.text)

    finally:
        # Terminate the processes
        await asyncio.sleep(5)  # Wait for the subprocesses to complete their execution
        api_process.terminate()
        explainer_process.terminate()

# Run the system test
asyncio.run(system_test())
