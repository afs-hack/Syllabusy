from google import genai
from google.genai import types
from dotenv import load_dotenv
import pathlib
import os
import uuid
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

import firebase_admin
from firebase_admin import credentials, storage
# .env file contains the GEMINI_API_KEY
# and TEST_PDF_PATH environment variables.

load_dotenv()

# --- Flask Application Setup ---
app = Flask(__name__)
# Enable CORS for the frontend to communicate with this server
CORS(app) 
print("Flask backend initialized.")

#configure firebase
firebase_config = {
    "type": os.getenv("FIREBASE_TYPE"),
    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
    "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
    "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
    "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL"),
    "universe_domain": os.getenv("FIREBASE_UNIVERSE_DOMAIN")
}

storage_bucket_name = os.getenv("FIREBASE_STORAGE_BUCKET")

try:
    # Use the service account object (replace with path to .json file in real app)
    # If using a downloaded file: cred = credentials.Certificate("path/to/your/serviceAccountKey.json")
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred, {
        # This MUST be your bucket name (e.g., 'my-project-12345.appspot.com')
        'storageBucket': storage_bucket_name
    })
    print("Firebase Admin SDK initialized successfully.")
except Exception as e:
    print(f"ERROR: Could not initialize Firebase Admin SDK. Check credentials and bucket config. Error: {e}")
    # In a real app, you might exit or disable file storage features here.

@app.route('/api/upload-pdf', methods=['POST'])

# --- Reusable Core Upload Function ---
def _perform_upload(file_handle, original_filename, user_id):
    """
    Handles the core logic of saving a file handle to Firebase Storage.
    Returns (result_dict, error_message)
    """
    if not original_filename.lower().endswith('.pdf'):
        return None, 'Invalid file type. Only PDF files are accepted.'

    try:
        bucket = storage.bucket()

        # Create a unique filename using UUID to prevent naming conflicts
        file_extension = os.path.splitext(original_filename)[1] # Get .pdf
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Define the path in Firebase Storage: 'user_id/pdfs/unique_id.pdf'
        blob_path = f"{user_id}/pdfs/{unique_filename}"
        blob = bucket.blob(blob_path)

        # Upload the file directly from the file handle
        blob.upload_from_file(file_handle, content_type='application/pdf')

        # Make the file publicly accessible (based on your Firebase Storage Rules)
        blob.make_public()
        public_url = blob.public_url

        print(f"File uploaded successfully for user {user_id}: {public_url}")

        return {
            'message': 'PDF uploaded successfully to Firebase Storage.',
            'filename': original_filename,
            'storagePath': blob_path,
            'publicUrl': public_url
        }, None

    except Exception as e:
        print(f"Error during Firebase upload: {e}")
        return None, f'Failed to upload file to storage: {str(e)}'

# --- 2a. HTTP Request Upload Endpoint (Original functionality) ---
@app.route('/api/upload-pdf', methods=['POST'])
def upload_pdf_to_firebase():
    """
    Handles file upload streamed from an HTTP request.
    """
    
    # 1. Input Validation
    user_id = request.headers.get('X-User-ID', 'anonymous_user')
    if 'file' not in request.files:
        return jsonify({'error': 'No file part (expected key "file") in the request'}), 400
    
    uploaded_file = request.files['file']
    original_filename = uploaded_file.filename
    
    if original_filename == '':
        return jsonify({'error': 'No file selected.'}), 400
    
    # 2. Perform Upload using the reusable function
    upload_result, error_msg = _perform_upload(uploaded_file, original_filename, user_id)
    
    if upload_result:
        return jsonify(upload_result), 200
    else:
        return jsonify({'error': error_msg}), 500


# --- 2b. Local File Upload Endpoint (New functionality for local file) ---
@app.route('/api/upload-local-test', methods=['GET'])
def upload_local_test():
    """
    Demonstrates uploading a PDF located on the local server file system.
    Note: Requires a file named 'test_document.pdf' in the execution directory.
    """
    # Define the local path and user ID for testing
    filepath = pathlib.Path('~/Desktop/School/Fall25/syllabuses/BeginningKorean2-KORE-1442-002.pdf').expanduser()
    TEST_USER_ID = "local_test_user"

    if not pathlib.Path.exists(filepath):
        return jsonify({'error': f'Local test file not found at: {filepath}. Please ensure a file named "test_document.pdf" exists.'}), 500

    try:
        # Key Change: Open the file for reading in binary mode ('rb')
        with open(filepath, 'rb') as local_file_handle:
            original_filename = os.path.basename(filepath)
            
            # Use the reusable core function
            upload_result, error_msg = _perform_upload(local_file_handle, original_filename, TEST_USER_ID)

            if upload_result:
                upload_result['message'] = f"SUCCESS: Local file '{filepath}' uploaded for testing."
                return jsonify(upload_result), 200
            else:
                return jsonify({'error': error_msg}), 500
    except Exception as e:
        print(f"Error opening local file: {e}")
        return jsonify({'error': f'Error processing local file: {str(e)}'}), 500

@app.route('/')
def status():
    """Basic status endpoint."""
    return "PDF Upload API is running."

if __name__ == '__main__':
    app.run(debug=True)