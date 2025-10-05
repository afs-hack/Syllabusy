from google import genai
from google.genai import types
from dotenv import load_dotenv
import pathlib
import os
import uuid
import json
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import List, Dict, Any, Optional
import requests 
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta

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
    
def create_calendar_events(events_data, access_token):
    """
    Takes the events dictionary and creates Google Calendar events.
    
    Args:
        events_data: Dict with 'events' list containing event details
        access_token: Google OAuth access token from frontend
    
    Returns:
        List of created event IDs or error messages
    """
    try:
        # Create credentials object from access token
        credentials = Credentials(token=access_token)
        
        # Build Calendar API service
        service = build('calendar', 'v3', credentials=credentials)
        
        created_events = []
        
        for event in events_data.get('events', []):
            # Format the event for Google Calendar API
            calendar_event = {
                'summary': event['summary'],
                'description': event.get('description', ''),
            }
            
            # Handle start time
            start_info = event['start']
            if 'time' in start_info:
                # Event has specific time
                start_datetime = f"{start_info['date']}T{start_info['time']}:00"
                calendar_event['start'] = {
                    'dateTime': start_datetime,
                    'timeZone': 'America/Chicago',  # Adjust to user's timezone
                }
                # Default 1-hour duration for exams
                end_datetime = (datetime.fromisoformat(start_datetime) + 
                               timedelta(hours=1)).isoformat()
                calendar_event['end'] = {
                    'dateTime': end_datetime,
                    'timeZone': 'America/Chicago',
                }
            else:
                # All-day event
                calendar_event['start'] = {'date': start_info['date']}
                calendar_event['end'] = {'date': start_info['date']}
            
            # Add reminders
            calendar_event['reminders'] = {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 24 * 60},  # 1 day before
                    {'method': 'popup', 'minutes': 60},        # 1 hour before
                ],
            }
            
            # Insert event into primary calendar
            created_event = service.events().insert(
                calendarId='primary',
                body=calendar_event
            ).execute()
            
            created_events.append({
                'id': created_event['id'],
                'summary': event['summary'],
                'link': created_event.get('htmlLink')
            })
            
        return {'success': True, 'events': created_events}
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

# Add this to your Flask route in server.py
@app.route('/api/create-calendar-events', methods=['POST'])
def create_calendar_events_endpoint():
    """
    Endpoint to create Google Calendar events from extracted syllabus dates
    """
    try:
        data = request.json
        google_token = request.headers.get('Google-Access-Token')
        
        if not google_token:
            return jsonify({'error': 'No Google access token provided'}), 401
        
        events_data = data.get('events')
        if not events_data:
            return jsonify({'error': 'No events data provided'}), 400
        
        # Create the calendar events
        result = create_calendar_events(
            {'events': events_data}, 
            google_token
        )
        
        if result['success']:
            return jsonify({
                'message': f"Successfully created {len(result['events'])} calendar events",
                'events': result['events']
            }), 200
        else:
            return jsonify({'error': result['error']}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# --- 2a. HTTP Request Upload Endpoint (Original functionality) ---
@app.route('/api/upload-pdf', methods=['POST'])
def upload_pdf_to_firebase():
    """Handles PDF file uploads from the frontend via POST request."""
    user_id = request.headers.get('User-ID')
    
    # 1. Validation & File retrieval
    if 'files' not in request.files:
        print("DEBUG ERROR: 'files' key missing in request.files. Returning 400.")
        return jsonify({'error': 'No file part(s) in the request. Ensure frontend FormData field is named "files".'}), 400
    
    uploaded_files = request.files.getlist('files')

    
    if not uploaded_files:
        return jsonify({'error': 'No selected files.'}), 400
    
    upload_results = []
    has_error = False

    for uploaded_file in uploaded_files:
        original_filename = uploaded_file.filename

        if original_filename == '':
            continue # Skip files with no name

        if not original_filename.lower().endswith('.pdf'):
            has_error = True
            upload_results.append({
                'filename': original_filename, 
                'error': 'Invalid file type. Only PDF files are allowed.'
            })
            continue # Skip non-PDF files

        # 2. Perform Upload using the reusable function
        result, error_msg = _perform_upload(uploaded_file, original_filename, user_id)

        # 3. Store result
        if error_msg:
            has_error = True
            upload_results.append({'filename': original_filename, 'error': error_msg})
        else:
            upload_results.append(result)
    
    # 4. Response handling
    if has_error:
        # If any file failed, return a 500 error with the list of results/errors
        # The frontend will need to parse this list.
        return jsonify({
            'message': 'Some files failed to upload or were invalid.',
            'results': upload_results
        }), 500
    else:
        # NOTE: Svelte frontend expects 'summary', we summarize all uploads here.
        uploaded_names = [r['filename'] for r in upload_results]
        summary_message = f"Successfully processed and uploaded {len(uploaded_files)} file(s): {', '.join(uploaded_names)}."

        return jsonify({
            'message': 'All files uploaded successfully.',
            'summary': summary_message, # Send a summary back for the textarea
            'results': upload_results
        }), 200


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

# --- NEW 2c. Status Endpoint ---
@app.route('/api/status', methods=['POST'])
def get_status():
    """Returns a simple JSON status to confirm the backend is running."""
    # Check if Firebase is initialized just to be thorough
    is_firebase_ready = bool(firebase_admin._apps)
    
    return jsonify({
        'status': 'OK',
        'message': 'Flask server and API endpoints are running.',
        'firebase_status': 'Connected' if is_firebase_ready else 'Uninitialized'
    }), 200

# --- 3. Gemini Integration Endpoint ---
@app.route('/api/get-dates', methods=['POST'])
def get_dates():
    client = genai.Client()
    user_id = request.headers.get('User-ID')
    google_token = request.headers.get('Google-Access-Token')
    directory_path = f"{user_id}/pdfs/"
    
    # Add debug logging
    print(f"DEBUG: User-ID = {user_id}")
    print(f"DEBUG: Has Google Token = {bool(google_token)}")
    print(f"DEBUG: Directory path = {directory_path}")
    
    """Download all PDFs from a Firebase Storage directory"""
    pdf_files = []
    
    try:
        bucket = storage.bucket()
        print(f"Accessing Firebase Storage bucket...")
        
        try:
            blobs = list(bucket.list_blobs(prefix=directory_path))
            
            if not blobs:
                print(f"⚠ No files found in directory: {directory_path}")
                return jsonify({
                    'status': 'BAD',
                    'error': 'No PDF files found for this user'
                }), 404  # Changed from 500 to 404
            
            print(f"Found {len(blobs)} file(s) in directory")
            
            for blob in blobs:
                if blob.name.endswith('.pdf'):
                    try:
                        print(f"Downloading: {blob.name}...")
                        pdf_data = blob.download_as_bytes()
                        
                        pdf_files.append({
                            'name': blob.name,
                            'data': pdf_data,
                            'size': len(pdf_data)
                        })
                        
                        size_mb = len(pdf_data) / (1024 * 1024)
                        print(f"✓ Downloaded: {blob.name} ({size_mb:.2f} MB)")
                        
                    except Exception as e:
                        print(f"✗ Error downloading {blob.name}: {e}")
                        continue
                        
        except Exception as e:
            print(f"✗ Error listing files in directory: {e}")
            return jsonify({
                'status': 'BAD',
                'error': f'Error listing files: {str(e)}'
            }), 500
            
    except Exception as e:
        print(f"✗ Error accessing Firebase Storage bucket: {e}")
        return jsonify({
            'status': 'BAD',
            'error': f'Firebase error: {str(e)}'
        }), 500
    
    """Upload PDFs to Gemini API and get response"""
    
    prompt = """Analyze these PDF syllabi and extract all exam dates. Return ONLY valid JSON with no additional text, explanations, or markdown formatting.

Format:
{"events":[{"summary":"Course Name - Exam Type","description":"details","start":{"date":"YYYY-MM-DD","time":"HH:MM"}}]}

For all-day events (submissions, etc), omit the "time" field.

Example:
{"events":[{"summary":"Biology 101 - Midterm Exam","description":"Chapters 1-5","start":{"date":"2025-03-15","time":"09:00"}}]}

Now extract the exam dates:"""

    if not pdf_files:
        print("⚠ No PDF files to upload")
        return jsonify({
            'status': 'BAD',
            'error': 'No valid PDF files found'
        }), 404
    
    try:
        model = "gemini-2.5-flash"
        print(f"✓ Gemini model loaded")
        
        content_parts = [prompt]
        
        for i, pdf in enumerate(pdf_files, 1):
            try:
                print(f"Uploading PDF {i}/{len(pdf_files)}: {pdf['name']}...")
                
                pdf_part = types.Part(
                    inline_data={
                        'mime_type': 'application/pdf',
                        'data': base64.b64encode(pdf['data']).decode('utf-8')
                    }
                )

                content_parts.append(pdf_part)
                print(f"✓ Uploaded: {pdf['name']}")
                
            except Exception as e:
                print(f"✗ Error uploading {pdf['name']}: {e}")
                continue
        
        if len(content_parts) == 1:
            print("✗ No PDFs were successfully uploaded to Gemini")
            return jsonify({
                'status': 'BAD',
                'error': 'Failed to upload PDFs to Gemini'
            }), 500
        
        print(f"\nSending request to Gemini with {len(content_parts)-1} PDF(s)...")
        
        try:
            response = client.models.generate_content(model=model, contents=[content_parts])
            print("✓ Response received from Gemini")
            
            # Parse the JSON response
            print("Raw Response:")
            print(response.text)
            
            # Clean up response text (remove markdown if present)
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif response_text.startswith('```'):
                response_text = response_text.split('```')[1].split('```')[0].strip()
            
            events_data = json.loads(response_text)
            print(f"✓ Parsed {len(events_data.get('events', []))} events")
            
            return jsonify({
                'summary': f"Found {len(events_data.get('events', []))} exam dates across your syllabi",
                'events': events_data.get('events', []),
                'has_google_token': bool(google_token)
            }), 200
            
        except json.JSONDecodeError as e:
            print(f"✗ JSON parsing error: {e}")
            print(f"Response text: {response.text}")
            return jsonify({
                'status': 'BAD',
                'error': 'Failed to parse Gemini response as JSON',
                'raw_response': response.text
            }), 500
        except Exception as e:
            print(f"✗ Error generating content with Gemini: {e}")
            return jsonify({
                'status': 'BAD',
                'error': f'Gemini API error: {str(e)}'
            }), 500
            
    except Exception as e:
        print(f"✗ Error in Gemini upload process: {e}")
        return jsonify({
            'status': 'BAD',
            'error': f'Upload process error: {str(e)}'
        }), 500            

@app.route('/')
def status():
    """Basic status endpoint."""
    return "PDF Upload API is running."

if __name__ == '__main__':
    app.run(debug=True)