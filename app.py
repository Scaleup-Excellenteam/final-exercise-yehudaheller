import json
import re

from flask import Flask, request, render_template, jsonify
import os
from datetime import datetime
import uuid

app = Flask(__name__)

# Set the path for uploaded files
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create the uploads folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

PENDING_FOLDER = 'pending'
DONE_FOLDER = 'outputs'  # if file in outputs folder mean its done


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

            # Save the file to the upload folder
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # get the uid from the file name
            uid_for_user = filename.split('_')[2].split('.')[0]

            return render_template('index.html', message='File uploaded successfully. ', uid=uid_for_user)

    return render_template('index.html')


def allowed_file(filename):
    # Specify the allowed file extensions
    allowed_extensions = {'pptx'}

    # Check if the file extension is allowed
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def generate_unique_filename(filename):
    # Generate a unique filename by combining the original filename, timestamp, and UID
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    uid = str(uuid.uuid4().hex)  # Generate a random UID
    filename_without_extension, extension = os.path.splitext(filename)
    new_filename = f"{filename_without_extension}_{timestamp}_{uid}{extension}"
    return new_filename


def get_file_status(filename):
    # Check if the file exists in outputs folder, pending, else return not found
    pptx_filename = os.path.splitext(filename)[0] + '.pptx'
    json_filename = os.path.splitext(filename)[0] + '.json'
    if os.path.exists(os.path.join(DONE_FOLDER, pptx_filename)):
        return 'done'
    elif os.path.exists(os.path.join(PENDING_FOLDER, pptx_filename)) \
            or os.path.exists(os.path.join(UPLOAD_FOLDER, pptx_filename)):
        return 'pending'
    elif os.path.exists(os.path.join(DONE_FOLDER, json_filename)):
        return 'done'
    else:
        return 'not found'


def get_file_details(filename):
    filename_without_extension, _ = os.path.splitext(filename)
    timestamp, uid = filename_without_extension.rsplit('_', 2)[-2:]

    original_filename = filename_without_extension.split('_', 1)[0]
    date_and_time = format_timestamp(timestamp)
    return {
        'status': get_file_status(filename),
        'filename': original_filename,
        'timestamp': date_and_time,
        'explanation': get_file_explanation(filename)
    }


def get_file_explanation(filename):
    # Retrieve the explanation from the processed output file if available
    output_file_path = os.path.join(DONE_FOLDER, os.path.splitext(filename)[0] + '.json')
    if os.path.exists(output_file_path):
        # Read the data from the JSON file
        with open(output_file_path, 'r') as file:
            json_data = file.read()
            data = json.loads(json_data)
            return data

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
                filename = find_file_by_uid(uid)
                file_details = get_file_details(filename)
                return render_template('status.html', data=file_details)
            except UIDNotFoundException:
                return render_template('index.html', error='UID not found')

        return render_template('index.html', error='UID not provided')

    filename = request.args.get('filename')
    if filename:
        file_details = get_file_details(filename)
        return render_template('status.html', data=file_details)

    return 'Invalid request'



def format_timestamp(timestamp):
    # Extract date and time components using regex groups
    match = re.match(r'(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})', timestamp)
    if match:
        year, month, day, hour, minute, second = match.groups()
        formatted_timestamp = f"Date: {year}.{month}.{day}, Time: {hour}:{minute}:{second}"
        return formatted_timestamp
    else:
        return None

if __name__ == '__main__':
    app.run()

