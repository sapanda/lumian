from app.server import (app, get_openai_client,
                        get_transcript_repo, get_settings)
from app.config import Settings
from app.domains import Transcript
from app.interfaces import OpenAIClientInterface, TranscriptRepositoryInterface
from fastapi.testclient import TestClient
from fastapi import status
import json
import pytest

client = TestClient(app)

transcripts = {}


class MockOpenAIClient(OpenAIClientInterface):
    def execute_completion(self, prompt: str,
                           model: str = '',
                           temperature: int = 0,
                           max_tokens: int = 100,
                           ) -> dict:
        tokens_used = len(prompt.split()) * 2
        cost = tokens_used * 0.000001
        return {
            'output': 'Some text (0). Some other text (1)',
            'cost': cost,
            'tokens_used': tokens_used
        }


class MockTranscriptRepo(TranscriptRepositoryInterface):

    def get(self, id: int) -> Transcript:
        return transcripts.get(id)

    def save(self, transcript: Transcript):
        if transcript.id in transcripts:
            raise
        transcripts[transcript.id] = transcript

    def replace(self, transcript: Transcript):
        transcripts[transcript.id] = transcript

    def delete(self, id: int):
        if id in transcripts:
            del transcripts[id]


def get_mock_openai_client():
    return MockOpenAIClient()


def get_mock_transcript_repo():
    return MockTranscriptRepo()


def get_mock_settings():
    settings = Settings(
        db_name='',
        db_host='',
        db_password='',
        db_port=1000,
        db_user='',
        openai_api_key='',
        openai_org_id='',
        max_summary_size=8,
        line_min_size=5,
        chunk_min_words=20
    )
    return settings


def setup():
    transcript_file = 'tests/test_transcript-dummy.txt'
    app.dependency_overrides[get_openai_client] = get_mock_openai_client
    app.dependency_overrides[get_settings] = get_mock_settings
    app.dependency_overrides[get_transcript_repo] = get_mock_transcript_repo
    with open(transcript_file, 'r') as f:
        global transcript_text
        transcript_text = f.read()


def teardown():
    transcripts.clear()
    app.dependency_overrides.clear()


@pytest.fixture()
def setup_teardown():
    setup()
    yield "Do Testing"
    teardown()


def test_get_transcript(setup_teardown):
    response = client.get("/transcript/0")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    response = client.post(
        "/transcript/0",
        content=transcript_text,
        headers={
            'Content-Type': 'text/plain'
        })
    assert response.status_code == status.HTTP_204_NO_CONTENT
    response = client.get("/transcript/0")
    assert response.status_code == status.HTTP_200_OK
    data = json.loads(response.content)
    assert len(data) > 0


def test_save_transcript(setup_teardown):
    response = client.post(
        "/transcript/0",
        content=transcript_text,
        headers={
            'Content-Type': 'text/plain'
        })
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_transcript(setup_teardown):
    response = client.post(
        "/transcript/0",
        content=transcript_text,
        headers={
            'Content-Type': 'text/plain'
        })
    assert response.status_code == status.HTTP_204_NO_CONTENT
    response = client.delete("/transcript/0")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    response = client.delete("/transcript/0")
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_get_summary(setup_teardown):
    response = client.post(
        "/transcript/0",
        content=transcript_text,
        headers={
            'Content-Type': 'text/plain'
        })
    assert response.status_code == status.HTTP_204_NO_CONTENT
    response = client.get('/transcript/0/summary?interviewee=User1')
    assert response.status_code == status.HTTP_200_OK
    data = json.loads(response.content)
    print(data)
    assert 'cost' in data
    assert len(data['output']) > 0
