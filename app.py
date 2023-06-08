import json

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

            # Return the success message with the UID
            return render_template('index.html', message='File uploaded successfully.', uid=filename)

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
    elif os.path.exists(os.path.join(PENDING_FOLDER, pptx_filename)):
        return 'pending'
    elif os.path.exists(os.path.join(DONE_FOLDER, json_filename)):
        return 'done'
    else:
        return 'not found'


def get_file_details(filename):
    filename_without_extension, _ = os.path.splitext(filename)
    timestamp, uid = filename_without_extension.rsplit('_', 2)[-2:]

    original_filename = filename_without_extension.split('_', 1)[0]

    return {
        'status': get_file_status(filename),
        'filename': original_filename,
        'timestamp': timestamp,
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


@app.route('/status', methods=['GET'])
def status():
    filename = request.args.get('filename')
    if filename:
        file_details = get_file_details(filename)
        return render_template('status.html', data=file_details)

    return 'Invalid request'


if __name__ == '__main__':
    app.run()
