import requests
import time
from requests_toolbelt.multipart.encoder import MultipartEncoder

def start_transcription():
    # Configuration
    url = "https://uzbekvoice.ai/api/v1/stt"
    api_key = ""  # Replace with actual API key
    file_path = r"D:/Programming/call_analysis/name(26).mp3"  # File path

    # Telegram bot details
    telegram_bot_token = ""  # Replace with your bot token
    chat_id = ""  # Replace with the chat ID

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
                    "file": (file_path, f, "audio/mp3"),  # Use "audio/mpeg" as MIME type
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
                        try:
                            status_data = status_response.json()
                            status = status_data.get("status")

                            if status == "COMPLETED":
                                transcription_text = status_data.get("text", "No transcription text found.")
                                print("Transcription completed:", transcription_text)
                                send_message_to_telegram(f"Transcription completed: {transcription_text}")
                                break
                            elif status == "FAILED":
                                send_message_to_telegram("Transcription failed.")
                                print("Transcription failed.")
                                break
                            else:
                                print("Waiting for transcription to complete...")
                                time.sleep(20)
                        except ValueError:
                            print("Received non-JSON response while checking status.")
                            send_message_to_telegram("Error: Received non-JSON response from server.")
                            break
                    else:
                        print("Failed to fetch status:", status_response.status_code, status_response.text)
                        send_message_to_telegram("Failed to fetch transcription status.")
                        break
            else:
                print("Failed to start transcription:", response.status_code, response.text)
                send_message_to_telegram(f"Failed to start transcription: {response.text}")

    except FileNotFoundError:
        print(f"File not found at: {file_path}")
        send_message_to_telegram(f"File not found at: {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")
        send_message_to_telegram(f"An error occurred: {e}")
