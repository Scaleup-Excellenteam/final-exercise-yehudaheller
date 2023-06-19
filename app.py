import json
import re

from flask import Flask, request, render_template, jsonify
import os
from datetime import datetime
import uuid
from database import session, User, Upload

app = Flask(__name__)

# Set the path for uploaded files
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

PENDING_FOLDER = 'pending'
DONE_FOLDER = 'outputs'  # if file in outputs folder mean its done

# Create the uploads folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Create the db folder if it doesn't exist
folder_name = "db"
if not os.path.exists(folder_name):
    os.makedirs(folder_name)


@app.route('/', methods=['GET', 'POST'])
def index():
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

    return render_template('index.html')


def allowed_file(filename):
    # Specify the allowed file extensions
    allowed_extensions = {'pptx'}

    # Check if the file extension is allowed
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def generate_unique_filename(filename):
    # Generate a unique filename by combining the original filename, timestamp, and UID
    uid = str(uuid.uuid4().hex)  # Generate a random UID
    filename_without_extension, extension = os.path.splitext(filename)
    new_filename = f"{uid}{extension}"
    return new_filename


def get_file_status(filename):
    # Check if the file exists in outputs folder, pending, else return not found
    pptx_filename = os.path.splitext(filename)[0] + '.pptx'
    json_filename = filename.split(".")[0] + '.json'
    print(f"the json_filename  is {json_filename}")

    if os.path.exists(os.path.join(DONE_FOLDER, pptx_filename)):
        return 'done'
    elif os.path.exists(os.path.join(PENDING_FOLDER, pptx_filename)) \
            or os.path.exists(os.path.join(UPLOAD_FOLDER, pptx_filename)):
        return 'pending'
    elif os.path.exists(os.path.join(DONE_FOLDER, json_filename)):
        return 'done'
    else:
        return 'not found'


def get_file_details(uid):
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


def get_upload_by_uid(uid):
    upload = session.query(Upload).filter_by(uid=uid).first()
    return upload


def get_file_explanation(filename_uid):
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


def find_file_by_uid(uid):
    folders = ['uploads', 'pending', 'outputs']
    for folder in folders:
        for root, dirs, files in os.walk(folder):
            for file in files:
                if uid in file:
                    return os.path.basename(file)
    raise UIDNotFoundException("UID not found")


@app.route('/status', methods=['GET', 'POST'])
def status():
    if request.method == 'POST':
        uid = request.form.get('uid')
        if uid:
            try:
                file_details = get_file_details(uid)
                return render_template('status.html', data=file_details)
            except UIDNotFoundException:
                return render_template('index.html', error='UID not found'), 404

        return render_template('index.html', error='UID not provided'), 404


def save_to_database(email, uid_for_user, filename):
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
