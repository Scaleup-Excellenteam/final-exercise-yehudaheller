from flask import Flask, request, render_template
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

            # Return the unique identifier (UID) for the file
            return 'File uploaded successfully. UID: ' + filename

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


if __name__ == '__main__':
    app.run()
