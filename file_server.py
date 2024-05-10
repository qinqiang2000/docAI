# Filename: flask_server.py
from flask import Flask, send_from_directory
import hashlib
import os
import os.path as osp
import shutil

app = Flask(__name__)

directory = os.path.join(os.getcwd(), 'tmp')
port = 8090

# _file: st.file_uploader's return value
def save_uploaded_file(_file):
    global directory
    os.makedirs(directory, exist_ok=True)

    hasher = hashlib.sha256()
    _file.seek(0)
    for chunk in iter(lambda: _file.read(4096), b''):
        hasher.update(chunk)
    file_hash = hasher.hexdigest()
    # Generate a temporary file name
    tmp_file_name = osp.join(directory, osp.splitext(_file.name)[0] + '_' + file_hash[:8] + osp.splitext(_file.name)[1])
    # Write the uploaded file's contents to the temporary file
    with open(tmp_file_name, 'wb') as tmp_file:
        _file.seek(0)
        shutil.copyfileobj(_file, tmp_file)
    return tmp_file_name


@app.route('/<filename>')
def serve_pdf(filename):
    """Serve a PDF file from the 'static/pdfs' directory."""
    return send_from_directory(directory, filename, as_attachment=False)


@app.route('/')
def index():
    return 'Hello, World!'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)
