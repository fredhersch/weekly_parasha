import os
from google import genai
from dotenv import load_dotenv

# Load the variables from the .env file
load_dotenv()

project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
print(f"Connected to Project: {project_id}")

# Ensure these match your .env
location = "us-central1"

client = genai.Client(
    vertexai=True,
    project=project_id,
    location=location
)

try:
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents="Say 'System Online' if you can hear me."
    )
    print(f"Success: {response.text}")
except Exception as e:
    print(f"Still blocked: {e}")