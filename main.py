import asyncio
import os
import shutil
import time
from datetime import datetime
from pptx_parser import read_pptx_file
from openai_integration import integrate_openai
from json_utils import save_to_json
from database import session, Upload

async def main() -> None:
    """
    Main function to orchestrate the PowerPoint file processing and OpenAI integration.
    """
    while True:
        time.sleep(10)

        # Query the database for pending uploads
        pending_uploads = session.query(Upload).filter_by(status="pending").all()

        # Process each pending upload
        for upload in pending_uploads:
            uid = upload.uid
            pptx_file_path = "uploads\\" + uid + ".pptx"

            slides_text = read_pptx_file(pptx_file_path)

            upload_time = datetime.now()
            update_file_status_in_database_by_uid(uid, status="pending", upload_time=upload_time)

            # Integrate OpenAI asynchronously
            answer = []
            for slide in slides_text:
                generate_text = await integrate_openai(slide)
                answer.append(generate_text)
            list_answer_to_string = ' '.join(answer)

            # Get the output file name based on the PowerPoint file name
            output_file_name = get_file_name(uid)

            save_to_json(list_answer_to_string, output_file_name)
            finish_time = datetime.now()
            update_file_status_in_database_by_uid(uid, status="done", finish_time=finish_time)

            # Delete the PowerPoint file from the uploads folder
            file_to_move = uid + ".pptx"
            remove_file_from_uploads(file_to_move)



def remove_file_from_uploads(filename: str) -> None:
    """
    Removes a file from the uploads folder.

    Args:
        filename: The name of the file to remove.
    """
    # Define the path to the uploads folder
    uploads_folder = "uploads"
    print(f"filename: {filename}")

    # Check if the file exists in the uploads folder
    file_path = os.path.join(uploads_folder, filename)
    if not os.path.isfile(file_path):
        print(f"File '{filename}' does not exist in the uploads folder.")
        return

    # Remove the file
    try:
        os.remove(file_path)
        print(f"File '{filename}' removed successfully from the uploads folder.")

    except Exception as e:
        print(f"An error occurred while removing the file: {str(e)}")


def get_file_name(uid: str) -> str:
    """
    Returns the output file name based on the UID.

    Args:
        uid: The unique identifier.

    Returns:
        The output file name.
    """
    return uid + ".json"


def update_file_status_in_database_by_uid(uid: str, status: str, upload_time: datetime = None, finish_time: datetime = None) -> None:
    """
    Updates the file status in the database based on the UID.

    Args:
        uid: The unique identifier.
        status: The status to set.
        upload_time: The upload time (optional).
        finish_time: The finish time (optional).
    """
    upload = session.query(Upload).filter_by(uid=uid).first()
    if upload:
        upload.status = status
        if upload_time:
            upload.upload_time = upload_time
        if finish_time:
            upload.finish_time = finish_time
        session.commit()
    else:
        print(f"Upload with UID '{uid}' not found in the database.")


if __name__ == "__main__":
    asyncio.run(main())
