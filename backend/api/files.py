import os
from flask import Blueprint, request, jsonify, Response
from models import Files
from app import db, socketio

# Define a variable for the upload folder
# IMPORTANT: Change this to a real, accessible path on your system.
UPLOAD_FOLDER = "data"
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'doc', 'xlsx', 'md'}

# Create the uploads directory if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

files_router = Blueprint(name="files", import_name=__name__, url_prefix="/files/")

def get_file_extension(filename):
    """Returns the file extension in lowercase."""
    return filename.rsplit(".", 1)[1].lower()

def allowed_file(filename):
    """Checks if the file's extension is in the allowed set."""
    return "." in filename and get_file_extension(filename) in ALLOWED_EXTENSIONS

# This function is not used in the current code and can be removed,
# or updated if you plan to use it later.
def check_files(file_name):
    # This query syntax is not standard for first_or_404.
    # A more common approach is to query by a unique field.
    file = Files.query.filter_by(file_name=file_name).first()
    return file

@files_router.route("/upload", methods=["POST"])
def file_upload():
    """Handles file uploads, saves the file, and records it in the database."""
    # Check 1: Ensure the 'file' key exists in the request
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["file"]

    # Check 2: Ensure a file was selected
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    # Check 3: Validate the file and save it
    if file and allowed_file(file.filename):
        try:
            # Use a secure filename to prevent directory traversal attacks
            from werkzeug.utils import secure_filename
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            if not os.path.exists(file_path) :
                file.save(file_path)
                # Save file metadata to the database
                if not  check_files(file.filename):
                    save_file = Files(
                        file_name=filename,
                        file_type=get_file_extension(filename),
                        uploaded=True,
                        filepath=file_path
                    )
                db.session.add(save_file)
                db.session.commit()

                return jsonify({"message": f"File '{filename}' uploaded successfully"}), 201
            else:
                return jsonify({"message": f"File '{filename}' already uploaded"}), 201

        except Exception as e:
            # Rollback the session in case of an error
            db.session.rollback()
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    else:
        # If the file extension is not allowed
        return jsonify({"error": "File type not allowed"}), 400
    

@socketio.on("list_files")
def list_files(data):
    try:
        files = Files.query.all()
        files_dict = [file.to_dict() for file in files]
        socketio.emit("success",{"files":files_dict})
    except Exception as e:
        socketio.emit("error",{"error":str(e)})

