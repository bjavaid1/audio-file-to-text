# Google Cloud Function: Audio Transcription

This repository contains a Python-based Google Cloud Function designed to automatically transcribe audio files stored in a Google Cloud Storage bucket. The transcription is processed using the Google Cloud Speech-to-Text API, and the resulting text file is saved in the same Cloud Storage bucket.

## Features
- **Transcribes audio files** uploaded to a designated Google Cloud Storage bucket.
- **Automatic encoding detection** using Google Cloud Speech-to-Text API's AutoDetect feature.
- **Creates a transcription text file** and uploads it to the same bucket as the original audio file.

## How It Works
1. Upload an audio file to the Cloud Storage bucket associated with the Google Cloud Function trigger.
2. The function is triggered by the **finalized** event (indicating a new file has been uploaded).
3. The function transcribes the audio using Google Cloud Speech-to-Text API.
4. The transcription is saved as a `.txt` file in the same Cloud Storage bucket.

## Requirements
- **Python Version**: 3.9
- **Google Cloud Services**:
  - Google Cloud Functions
  - Google Cloud Storage
  - Google Cloud Speech-to-Text API

## Setup and Deployment

### 1. Enable APIs
Ensure that the following APIs are enabled for your Google Cloud project:
- Cloud Functions API
- Cloud Storage API
- Cloud Speech-to-Text API

### 2. Deploy the Function Using the Google Cloud Console

#### Option 1: Using the Google Cloud Console (GUI)
As an alternative to using the command-line interface (CLI), you can deploy the function using the **Google Cloud Console**:
1. Go to the **Cloud Functions** section in the Google Cloud Console: [Cloud Functions Console](https://console.cloud.google.com/functions).
2. Click on **Create Function**.
3. In the GUI, specify the function name, region, and other settings.
4. Choose the trigger type as **Cloud Storage** and set the event to **Finalize/Create**.
5. For the source code, either:
   - Enter the source code manually in the **inline editor**.
   - Upload a ZIP file containing the source code.
6. Configure the entry point (e.g., `speech_to_text`), runtime (Python 3.9), and environment variables.
7. Click **Deploy** to launch your function.

#### Option 2: Using the CLI
Alternatively, you can deploy the function using the Google Cloud CLI:
```bash
gcloud functions deploy speech-to-text \
--runtime python39 \
--trigger-resource [BUCKET_NAME] \
--trigger-event google.storage.object.finalize \
--entry-point speech_to_text \
--region [REGION]
```
Replace:
- `[BUCKET_NAME]` with the name of your Cloud Storage bucket.
- `[REGION]` with the region where you want to deploy your function (e.g., `us-central1`).

### 3. Upload Audio Files
Once the function is deployed:
- Upload an audio file to the Cloud Storage bucket.
- The function will be triggered by the **finalized** event, transcribe the audio file, and write a `.txt` file with the transcription to the same bucket.

### 4. Verify the Output
- Check the Cloud Storage bucket for the newly created transcription file, which will have the same name as the original audio file but with a `.txt` extension.

## Important Notes
- **File Type Support**: For a complete list of supported file types, refer to the [Google Cloud Speech-to-Text documentation](https://cloud.google.com/speech-to-text/v2/docs/reference/rpc/google.cloud.speech.v2#autodetectdecodingconfig).

- **Note**: Although Google states it supports AAC, I was unable to transcribe AAC files in M4A and MP4 containers; it kept giving an `InvalidArgument` error.

- **Note**: Your Cloud Storage bucket region **must match** the region where your Cloud Function is deployed. This ensures proper communication and minimizes latency issues.
