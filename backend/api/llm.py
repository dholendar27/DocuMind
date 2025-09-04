import os
from index import call_qwen_vision_api, convert_img_to_base64, convert_pdf_to_img, list_files
from util import list_all_unprocessed_files, update_file_chunked_status, clean_files_data, update_file_processing_status
from embeddings import document_embeddings
from retriever import response
from flask import Blueprint, jsonify, request
from app import socketio
import json

UPLOAD_FOLDER = "data"
llm_router = Blueprint(name="llm_task",import_name=__name__,url_prefix="/llm/")

@socketio.on("indexing")
def index_files(data):
    try:
        files = list_files(UPLOAD_FOLDER)
        if not files:
            socketio.emit('response',{"message":"No files to perform indexing"})
            return 
        socketio.emit('response',{"data":files})
        for file in files:
            images = convert_pdf_to_img(file)
            base64_images = convert_img_to_base64(images)
            response = call_qwen_vision_api(base64_images)
            if response:
                output_filename = os.path.basename(file).replace(".pdf", ".md")
                if not os.path.exists("extracted"):
                    os.mkdir("extracted")
                output_path = os.path.join("extracted", output_filename)
                
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(response)
                filename = os.path.basename(file)
                update_file_processing_status(filename, output_path)
                socketio.emit('response',{"message": f"{file} converted successfully"})

    except Exception as e:
        socketio.emit('error', {"error": str(e)})

@socketio.on("embeddings")
def process_embeddings(text):
    try:
        files = list_all_unprocessed_files()
        if not files:
            socketio.emit('response',{"message":"No files to perform chunking,"})
            return 
        cleaned_files = clean_files_data(files)
        socketio.emit('response',{"data":cleaned_files})
        for file in files:
            index = document_embeddings(file.extracted_filepath)
            if index:
                update_file_chunked_status(file.file_name)
            socketio.emit('response',{f"message": "{file.file_name} converted successfully"})
        socketio.emit('response',{"message":"all converted successfully,"})
    except Exception as e:
        socketio.emit('error', {"error": str(e)})

            

@socketio.on('message')
def rag_response(data):
    
    try:
        # Parse data if it's a string
        if isinstance(data, str):
            data = json.loads(data)
            print(f"Parsed JSON: {data}")
        
        query = data.get("query")
        print(f"Extracted query: '{query}'")
        
        if not query:
            socketio.emit('error', {"error": "Please enter query"})
            return
        
        res = response(query=query)
    
        socketio.emit('response', {"message": res.response})
        
    except Exception as e:
        socketio.emit('error', {"error": str(e)})

@socketio.on('connect')
def handle_connect():
    print("Client connected to WebSocket")

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected from WebSocket")
