from app import db
from models import Files

def update_file_processing_status(filename, filepath):
    file = Files.query.filter(Files.file_name == filename).first()
    if file:
        print(f"Found file in database: {file.file_name}")
        file.processed = True
        file.extracted_filepath = filepath
        db.session.add(file)
        db.session.commit()
        print(f"Updated successfully - processed: {file.processed}, extracted_filepath: {file.extracted_filepath}")
    else:
        print(f"ERROR: File '{filename}' not found in database!")
        # Let's see what files exist
        all_files = Files.query.all()
        print("Available files in database:")
        for f in all_files:
            print(f"  - {f.file_name}")

def list_all_unprocessed_files():
    # Only get files that are processed (have extracted text) but not yet chunked
    files = Files.query.filter(
        Files.processed == True,
        Files.chunked == False,
    ).all()
    return files

def update_file_chunked_status(filename):
    file = Files.query.filter(Files.file_name == filename).first()
    if file:
        file.chunked = True
        db.session.add(file)
        db.session.commit()

def clean_files_data(files):
    return [file.to_dict() for file in files]