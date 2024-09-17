import functions_framework
from google.cloud import speech
from google.cloud import storage

@functions_framework.cloud_event
def speech_to_text(cloud_event):
    # Get event data
    event_data = cloud_event.data
    file_name = event_data['name']
    bucket_name = event_data['bucket']

    # Google Cloud Storage URI for the audio file
    gcs_uri = f"gs://{bucket_name}/{file_name}"

    # Initialize Speech client
    client = speech.SpeechClient()

    # Config for the speech recognition
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US"
    )

    # Audio input
    audio = speech.RecognitionAudio(uri=gcs_uri)

    # Perform transcription
    response = client.long_running_recognize(config=config, audio=audio)
    result = response.result(timeout=90)

    # Collect transcription
    transcription = ""
    for r in result.results:
        transcription += f"{r.alternatives[0].transcript}\n"

    # Write the transcription to a new file in the same Cloud Storage bucket
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    output_file_name = f"{file_name.split('.')[0]}_transcription.txt"
    blob = bucket.blob(output_file_name)
    blob.upload_from_string(transcription)

    print(f"Transcription saved to: gs://{bucket_name}/{output_file_name}")
