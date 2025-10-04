from google import genai
from google.genai import types
from dotenv import load_dotenv
import pathlib
import os

# .env file contains the GEMINI_API_KEY
# and TEST_PDF_PATH environment variables.

load_dotenv()

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client()

TEST_PDF_PATH = os.getenv("TEST_PDF_PATH")

print("Beginning PDF read test...")

filepath = pathlib.Path(TEST_PDF_PATH).expanduser()

prompt = "who is the professor and where (and when) is the class held?"
response = client.models.generate_content(
    model="gemini-2.5-flash", contents=[
      types.Part.from_bytes(
        data=filepath.read_bytes(),
        mime_type='application/pdf',
      ),
      prompt])
print(response.text)