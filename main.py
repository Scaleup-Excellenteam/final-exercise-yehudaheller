import asyncio
import os
import shutil
import time
from datetime import datetime

from os import path
from pptx_parser import read_pptx_file, get_pptx_file_path
from openai_integration import integrate_openai
from json_utils import save_to_json
from database import session, User, Upload


async def main() -> None:
    """
    Main function to orchestrate the PowerPoint file processing and OpenAI integration.
    """

    while True:
        time.sleep(10)
        # Scan the uploads folder
        files = os.listdir('uploads')

        # Process each file
        for file in files:
            pptx_file_path = os.path.join('uploads', file)

            # Call the read_pptx_file function to read the PowerPoint file
            slides_text = read_pptx_file(pptx_file_path)
            print(slides_text)

            handle_pending_status(pptx_file_path, "add")  # move from uploads and add to pending folder
            # get uid based on the PowerPoint file name
            uid = pptx_file_path.split('.')[0]
            upload_time = datetime.now()
            update_file_status_in_database_by_uid(uid, status="pending", upload_time=upload_time)
            # Integrate OpenAI asynchronously
            answer = []
            for slide in slides_text:
                generate_text = await integrate_openai(slide)
                answer.append(generate_text)
            print(answer)

            # Get the output file name based on the PowerPoint file name
            output_file_name = get_file_name(uid)

            save_to_json(answer, output_file_name)
            finish_time = datetime.now()
            update_file_status_in_database_by_uid(uid, status="done", finish_time=finish_time)

            # the file already created in done folder, so delete from pending folder
            handle_pending_status(pptx_file_path, "remove")


def get_file_name(uid):
    return uid + ".json"

def handle_pending_status(file_path, action):
    file_name = os.path.basename(file_path)
    pending_folder = 'pending'

    if action == "add":
        if not os.path.exists(pending_folder):
            os.makedirs(pending_folder)
        # Move the file from uploads to pending folder
        shutil.move(file_path, os.path.join(pending_folder, file_name))
    elif action == "remove":
        # Remove the file from the pending folder
        file_in_pending = os.path.join(pending_folder, file_name)
        if os.path.exists(file_in_pending):
            os.remove(file_in_pending)


def update_file_status_in_database_by_uid(uid, status, upload_time=None, finish_time=None):
    uid_without_path = uid.split('\\')[-1]
    upload = session.query(Upload).filter_by(uid=uid_without_path).first()
    if upload:
        upload.status = status
        if upload_time:
            upload.upload_time = upload_time
        if finish_time:
            upload.finish_time = finish_time
        session.commit()
    else:
        print(f"Upload with UID '{uid_without_path}' not found in the database.")

if __name__ == "__main__":
    asyncio.run(main())
