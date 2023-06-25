import json
import os
from datetime import datetime
from typing import Any, Dict, Union
import uuid

from flask import Flask, request, render_template, redirect, url_for
from sqlalchemy import desc

from database import session, User, Upload

app = Flask(__name__)

# Set the path for uploaded files
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

PENDING_FOLDER = 'pending'
DONE_FOLDER = 'outputs'

# Create the uploads folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Create the done folder if it doesn't exist
if not os.path.exists(DONE_FOLDER):
    os.makedirs(DONE_FOLDER)


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


def get_file_status(uid: str) -> str:
    """
    Retrieve the file status from the database based on its UID.

    Args:
        uid: The UID of the file.

    Returns:
        The status of the file ('done', 'pending', or 'not found').
    """
    try:
        upload = session.query(Upload).filter_by(uid=uid).first()
        if upload:
            return upload.status
        else:
            return 'pending'
    except Exception as e:
        # Handle any exceptions that may occur during the database query
        print(f"An error occurred while retrieving file status: {str(e)}")
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

    return {
        'status': upload.status if upload else None,
        'filename': upload.filename.split('_', 1)[0] if upload else None,
        'timestamp': upload.upload_time if upload else None,
        'explanation': get_file_explanation(uid) if upload else None
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


def get_file_explanation(uid):
    """
    Get the explanation of a file based on its UID.

    Args:
        uid: The UID of the file.

    Returns:
        The explanation of the file.
    """
    file_path = os.path.join(DONE_FOLDER, uid) + '.json'
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            explanation = file.read()
        return explanation
    else:
        return "Processing...\n Try Refresh Status later "


class UIDNotFoundException(Exception):
    pass


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
        last_upload = session.query(Upload).filter_by(filename=filename, user=user).order_by(
            desc(Upload.upload_time)).first()

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
            upload = Upload(uid=uid_for_user, filename=filename, status=get_file_status(uid_for_user), user_id=user.id)
            upload.set_finish_time()  # Set finish_time for uploads without a user
        else:
            # User doesn't exist, create a new User
            user = User(email=email)
            session.add(user)
            session.commit()
            upload = Upload(uid=uid_for_user, filename=filename, status=get_file_status(uid_for_user), user_id=user.id)
            upload.set_finish_time()  # Set finish_time for uploads without a user

        session.add(upload)
        session.commit()
    else:
        # User did not provide an email, create Upload without User
        upload = Upload(uid=uid_for_user, filename=filename, status=get_file_status(uid_for_user))
        upload.set_finish_time()  # Set finish_time for uploads without a user
        session.add(upload)
        session.commit()


if __name__ == '__main__':
    app.run()
