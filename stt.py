import requests
import time
from requests_toolbelt.multipart.encoder import MultipartEncoder

# Configuration
url = "https://uzbekvoice.ai/api/v1/stt"
api_key = "7a3dea09-8d9d-45cd-b204-6ebb79ed9bb3:50f201d8-dc5d-4c4f-8635-d1dec68ab0fc"  # Replace with actual API key
file_path = r"D:/Programming/call_analysis/audios/name(13).mp3"  # File path

# Telegram bot details
telegram_bot_token = "7561833317:AAErJUMSThTBuAfJ2PxwoBbU40tCkneWuGw"  # Replace with your bot token
chat_id = "7561833317"  # Replace with the chat ID

def send_message_to_telegram(text):
    """Send a message to a specified Telegram chat."""
    telegram_url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(telegram_url, data=data)

try:
    with open(file_path, "rb") as f:
        # Create a multipart encoder for the file upload
        encoder = MultipartEncoder(
            fields={
                "file": (file_path, f, "audio/mp3"),
                "return_offsets": "false",
                "run_diarization": "false",
                "language": "uz",
                "blocking": "false",
                "webhook_notification_url": "http://localhost:8080"
            }
        )

        # Headers for initial request
        headers = {
            "Authorization": api_key,
            "Content-Type": encoder.content_type
        }

        # Start the transcription request
        response = requests.post(url, headers=headers, data=encoder)

        # Check if the transcription request was accepted
        if response.status_code == 200:
            response_data = response.json()
            transcription_id = response_data.get("id")
            print("Transcription request accepted:", transcription_id)

            # Notify the user via Telegram
            send_message_to_telegram("Transcription request accepted. Waiting for completion...")

            # Poll the transcription status until it's complete
            while True:
                status_url = f"https://uzbekvoice.ai/api/v1/tasks?id={transcription_id}"
                status_headers = {
                    "Authorization": api_key,
                    "Content-Type": "application/json"
                }
                status_response = requests.get(status_url, headers=status_headers)

                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get("status")

                    if status == "COMPLETED":
                        transcription_text = status_data.get("text", "No transcription text found.")
                        print("Transcription completed:", transcription_text)

                        # Send the transcription text to Telegram
                        send_message_to_telegram(f"Transcription completed: {transcription_text}")
                        break
                    elif status == "FAILED":
                        send_message_to_telegram("Transcription failed.")
                        print("Transcription failed.")
                        break
                    else:
                        # Wait before checking status again
                        print("Waiting for transcription to complete...")
                        time.sleep(10)
                else:
                    print("Failed to fetch status:", status_response.status_code, status_response.text)
                    send_message_to_telegram("Failed to fetch transcription status.")
                    break
        else:
            print("Failed to start transcription:", response.status_code, response.text)
            send_message_to_telegram(f"Failed to start transcription: {response.text}")

except FileNotFoundError:
    print(f"File not found at: {file_path}")
except Exception as e:
    print(f"An error occurred: {e}")
