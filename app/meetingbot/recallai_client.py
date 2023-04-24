import requests


def add_bot_to_meeting(bot_name: str, meeting_url: str):

    url = "https://api.recall.ai/api/v1/bot/"

    payload = {
        "bot_name": bot_name,
        "transcription_options": {"provider": "assembly_ai"},
        "meeting_url": meeting_url
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": "Token bd5c553e67b74c2d4759e1cbc71f5976b07704b9"
    }

    return requests.post(url, json=payload, headers=headers)
    

