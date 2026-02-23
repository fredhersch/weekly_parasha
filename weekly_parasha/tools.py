import os
from google.cloud import texttospeech, storage

def process_daily_audio(day_name: str, script_content: str):
    """Generates audio for a specific day and uploads it to GCS."""

    # --- 1. Text-to-Speech ---
    # Initialize with the project ID from your .env
    tts_client = texttospeech.TextToSpeechClient(
        client_options={"quota_project_id": os.getenv("GOOGLE_CLOUD_PROJECT")}
    )
    synthesis_input = texttospeech.SynthesisInput(text=script_content)
    voice = (texttospeech.VoiceSelectionParams(
        language_code='en-US',
        name='en-US-Journey-F',
    ))
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
    response = tts_client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

    # --- 2. Upload to Cloud Storage ---
    storage_client = storage.Client()
    bucket_name = os.getenv("GCS_BUCKET_NAME")
    bucket = storage_client.bucket(bucket_name)

    blob_name = f"{day_name.lower()}_update.mp3"
    blob = bucket.blob(blob_name)
    blob.upload_from_string(response.audio_content, content_type="audio/mpeg")

    # Make it publicly readable (optional, or use signed URLs)
    blob.make_public()

    return f"Day: {day_name} | URL: {blob.public_url}"