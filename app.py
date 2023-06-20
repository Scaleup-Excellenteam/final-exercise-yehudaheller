import json
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Union
import uuid

from flask import Flask, request, render_template, jsonify, redirect, url_for
from sqlalchemy import desc

from database import session, User, Upload

app = Flask(__name__)

# Set the path for uploaded files
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

PENDING_FOLDER = 'pending'
DONE_FOLDER = 'outputs'  # if file in outputs folder mean it's done

# Create the uploads folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Create the db folder if it doesn't exist
folder_name = "db"
if not os.path.exists(folder_name):
    os.makedirs(folder_name)


@app.route('/', methods=['GET', 'POST'])
def index() -> Union[str, Any]:
    """
    Main route for the web application.
    Handles file uploads and displays the index page.

    Returns:
        If a file is uploaded successfully, renders the index.html template with success message.
        If there's an error, renders the index.html template with error message.
        If the request method is GET, renders the index.html template.
    """
    error = request.args.get('error')

    if request.method == 'POST':
        # Check if a file was submitted
        if 'file' not in request.files:
            return 'No file uploaded'

        file = request.files['file']

        # Check if the file exists and has an allowed extension
        if file.filename == '':
            return 'No selected file'

        if file and allowed_file(file.filename):
            # Generate a unique filename
            filename = generate_unique_filename(file.filename)
            orginal_filename_for_save_to_db = os.path.basename(file.filename)
            # Save the file to the upload folder
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Get the uid from the file name
            uid_for_user = filename.split('.')[0]

            email = request.form.get('email')  # Get the email from the form
            save_to_database(email, uid_for_user, orginal_filename_for_save_to_db)

            return render_template('index.html', message='File uploaded successfully. ', uid=uid_for_user)

    return render_template('index.html', error=error)


def allowed_file(filename: str) -> bool:
    """
    Check if the given filename has an allowed extension.

    Args:
        filename: The name of the file.

    Returns:
        True if the file extension is allowed, False otherwise.
    """
    # Specify the allowed file extensions
    allowed_extensions = {'pptx'}

    # Check if the file extension is allowed
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def generate_unique_filename(filename: str) -> str:
    """
    Generate a unique filename by combining the original filename, timestamp, and UID.

    Args:
        filename: The original name of the file.

    Returns:
        A unique filename.
    """
    # Generate a unique filename by combining the original filename, timestamp, and UID
    uid = str(uuid.uuid4().hex)  # Generate a random UID
    filename_without_extension, extension = os.path.splitext(filename)
    new_filename = f"{uid}{extension}"
    return new_filename


def get_file_status(filename: str) -> str:
    """
    Check the status of the file based on its filename.

    Args:
        filename: The name of the file.

    Returns:
        The status of the file ('done', 'pending', or 'not found').
    """
    # Check if the file exists in outputs folder, pending, else return not found
    pptx_filename = os.path.splitext(filename)[0] + '.pptx'
    json_filename = filename.split(".")[0] + '.json'
    print(f"the json_filename is {json_filename}")

    if os.path.exists(os.path.join(DONE_FOLDER, pptx_filename)):
        return 'done'
    elif os.path.exists(os.path.join(PENDING_FOLDER, pptx_filename)) \
            or os.path.exists(os.path.join(UPLOAD_FOLDER, pptx_filename)):
        return 'pending'
    elif os.path.exists(os.path.join(DONE_FOLDER, json_filename)):
        return 'done'
    else:
        return 'not found'


def get_file_details(uid: str) -> Dict[str, Union[str, datetime, Any]]:
    """
    Get the details of a file based on its UID.

    Args:
        uid: The UID of the file.

    Returns:
        A dictionary containing the file details (status, filename, timestamp, explanation).
    """
    upload = get_upload_by_uid(uid)
    if upload:
        filename = upload.filename
        original_filename = filename.split('_', 1)[0]
        timestamp = upload.upload_time.strftime('%Y%m%d%H%M%S')
        date_and_time = upload.upload_time
        status = upload.status
        explanation = get_file_explanation(uid)
    else:
        filename = None
        original_filename = None
        timestamp = None
        date_and_time = None
        status = None
        explanation = None

    return {
        'status': status,
        'filename': original_filename,
        'timestamp': date_and_time,
        'explanation': explanation
    }


def get_upload_by_uid(uid: str) -> Union[Upload, None]:
    """
    Get the Upload object based on its UID.

    Args:
        uid: The UID of the file.

    Returns:
        The Upload object if found, None otherwise.
    """
    upload = session.query(Upload).filter_by(uid=uid).first()
    return upload


def get_file_explanation(filename_uid: str) -> Union[Dict[str, Any], None]:
    """
    Get the explanation data from the processed output file.

    Args:
        filename_uid: The filename or UID of the file.

    Returns:
        The explanation data as a dictionary if available, None otherwise.
    """
    # Retrieve the explanation from the processed output file if available
    output_file_path = os.path.join(DONE_FOLDER, os.path.splitext(filename_uid)[0] + '.json')

    print(f"the uid from the output file is {output_file_path}")

    # Iterate over all files in the directory
    for file in os.listdir(DONE_FOLDER):
        file_to_check = "outputs\\" + file
        if file_to_check == output_file_path:
            # Build the file path
            file_path = os.path.join(DONE_FOLDER, file)

            # Read the file
            with open(file_path, 'r') as f:
                # Parse the JSON data
                data = json.load(f)
                return data

    # File not found
    return None


class UIDNotFoundException(Exception):
    pass


def find_file_by_uid(uid: str) -> str:
    """
    Find the filename associated with the given UID.

    Args:
        uid: The UID of the file.

    Returns:
        The filename if found.

    Raises:
        UIDNotFoundException: If the UID is not found in any of the folders.
    """
    folders = ['uploads', 'pending', 'outputs']
    for folder in folders:
        for root, dirs, files in os.walk(folder):
            for file in files:
                if uid in file:
                    return os.path.basename(file)
    raise UIDNotFoundException("UID not found")


@app.route('/status', methods=['GET', 'POST'])
def status() -> Union[str, Any]:
    """
    Route for checking the status of a file.
    Handles both UID and email/filename based queries.

    Returns:
        If the request method is POST:
            - If UID is provided, renders the status.html template with file details.
            - If email and filename are provided, renders the status.html template with file details.
            - If UID or Email and Filename are not provided, redirects to the index page with an error message.
        If the request method is GET, renders the index.html template.
    """
    if request.method == 'POST':
        uid = request.form.get('uid')
        email = request.form.get('email')
        filename = request.form.get('filename')

        if uid:
            try:
                file_details = get_file_details(uid)
                return render_template('status.html', data=file_details)
            except UIDNotFoundException:
                return redirect(url_for('index', error='UID not found'))
        elif email and filename:
            try:
                uid = get_uid_by_email_and_filename(email, filename)
                file_details = get_file_details(uid)
                return render_template('status.html', data=file_details)
            except UIDNotFoundException:
                return redirect(url_for('index', error='No matching record found'))
        else:
            return redirect(url_for('index', error='UID or Email and Filename not provided'))
    else:
        return render_template('index.html')


def get_uid_by_email_and_filename(email: str, filename: str) -> str:
    """
    Get the UID based on the given email and filename.

    Args:
        email: The email of the user.
        filename: The name of the file.

    Returns:
        The UID of the file.

    Raises:
        UIDNotFoundException: If the UID is not found for the given email and filename.
    """
    user = session.query(User).filter_by(email=email).first()
    if user:
        last_upload = session.query(Upload).order_by(desc(Upload.upload_time)).first()

        if last_upload:
            return last_upload.uid
    raise UIDNotFoundException("UID not found")


def save_to_database(email: str, uid_for_user: str, filename: str) -> None:
    """
    Save the file information to the database.

    Args:
        email: The email of the user.
        uid_for_user: The UID associated with the user.
        filename: The name of the file.
    """
    if email:
        # User provided an email, check if it exists in Users table
        user = session.query(User).filter_by(email=email).first()

        # if email already registered
        if user:
            upload = Upload(uid=uid_for_user, filename=filename, status=get_file_status(filename), user_id=user.id)
            upload.set_finish_time()  # Set finish_time for uploads without a user
        else:
            # User doesn't exist, create a new User
            user = User(email=email)
            session.add(user)
            session.commit()
            upload = Upload(uid=uid_for_user, filename=filename, status=get_file_status(filename), user_id=user.id)
            upload.set_finish_time()  # Set finish_time for uploads without a user

        session.add(upload)
        session.commit()
    else:
        # User did not provide an email, create Upload without User
        upload = Upload(uid=uid_for_user, filename=filename, status=get_file_status(filename))
        upload.set_finish_time()  # Set finish_time for uploads without a user
        session.add(upload)
        session.commit()


if __name__ == '__main__':
    app.run()
