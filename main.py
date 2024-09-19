import os
import functions_framework
from google.cloud import speech_v2
from google.cloud import storage
from google.cloud import logging
from google.cloud.speech_v2.types import cloud_speech

# ENTER YOUR PROJECT ID HERE and uncomment
# PROJECT_ID = 'MY_PROJECT_ID'

# Supported audio file extensions
SUPPORTED_EXTENSIONS = {'wav', 'mp3', 'm4a', 'mp4', 'flac', 'mov'}


@functions_framework.cloud_event
def speech_to_text(cloud_event):
    # Initialize Google Cloud Logging
    logging_client = logging.Client()
    logger = logging_client.logger("speech_to_text_logger")

    # Log function start
    logger.log_text("Starting speech_to_text function.", severity="INFO")

    # Get event data
    event_data = cloud_event.data
    file_name = event_data['name']
    bucket_name = event_data['bucket']

    # Check if the file has a supported extension
    file_extension = file_name.split('.')[-1].lower()
    if file_extension not in SUPPORTED_EXTENSIONS:
        # Abort execution for unsupported file types
        logger.log_text(f"Unsupported file type: {file_extension}. Supported types are: {', '.join(SUPPORTED_EXTENSIONS)}", severity="INFO")
        return
    

    # test file access to confirm no permissions issue
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        blob.exists()  # This will return True if the file exists and the service account can access it
        logger.log_text(f"Successfully accessed file: {file_name} in bucket: {bucket_name}", severity="INFO")
    except Exception as e:
        logger.log_text(f"Error accessing file: {str(e)}", severity="ERROR")
        raise


    # Google Cloud Storage URI for the audio file
    gcs_uri = f"gs://{bucket_name}/{file_name}"

    # Initialize Speech V2 client
    client = speech_v2.SpeechClient()

    # Configure the recognition request with AutoDetectDecodingConfig
    config = cloud_speech.RecognitionConfig(
        auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),  # Auto-detect the audio encoding
        language_codes=["en-US"],
        model="long",  # Use "long" for long-form audio
    )

    # Create recognition request using the GCS URI (no local download needed)
    request = cloud_speech.RecognizeRequest(
        recognizer=f"projects/{PROJECT_ID}/locations/global/recognizers/_",
        config=config,
        uri=gcs_uri  # Directly pass the GCS URI
    )

    logger.log_text(f"gcs_uri: {gcs_uri}", severity="INFO")


    # Perform transcription
    logger.log_text("Starting transcription process.", severity="INFO")
    response = client.recognize(request=request)

    # Collect transcription
    transcription = ""
    for result in response.results:
        transcription += f"{result.alternatives[0].transcript}\n"

    # Log the first 5 words of the transcription
    first_five_words = ' '.join(transcription.split()[:5])
    logger.log_text(f"Transcription complete: '{first_five_words}...'", severity="INFO")

    # Write the transcription to a new file in the same Cloud Storage bucket
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    output_file_name = f"{file_name.split('.')[0]}_transcription.txt"
    blob = bucket.blob(output_file_name)
    blob.upload_from_string(transcription)

    # Log transcription completion
    logger.log_text(f"Transcription complete. Saved to: gs://{bucket_name}/{output_file_name}", severity="INFO")
