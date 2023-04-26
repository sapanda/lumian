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

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        # handle HTTP errors (status code not between 200 and 299)
        error_msg = f"HTTP error occurred: {e}"
        status_code = e.response.status_code
        return {"error": error_msg, "status_code": status_code}
    except requests.exceptions.RequestException as e:
        # handle other types of request exceptions (e.g. network errors)
        error_msg = f"An error occurred: {e}"
        status_code = None  # set status code to None for non-HTTP errors
        return {"error": error_msg, "status_code": status_code}
    

def get_meeting_transcript_list(bot_id: str):

    url = f"https://api.recall.ai/api/v1/bot/{bot_id}/transcript/"

    headers = {
        "accept": "application/json",
        "Authorization": "Token bd5c553e67b74c2d4759e1cbc71f5976b07704b9"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        # handle HTTP errors (status code not between 200 and 299)
        error_msg = f"HTTP error occurred: {e}"
        status_code = e.response.status_code
        return {"error": error_msg, "status_code": status_code}
    except requests.exceptions.RequestException as e:
        # handle other types of request exceptions (e.g. network errors)
        error_msg = f"An error occurred: {e}"
        status_code = None  # set status code to None for non-HTTP errors
        return {"error": error_msg, "status_code": status_code} 