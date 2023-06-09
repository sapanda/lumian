from app.server import (
    app, get_openai_client, get_embeds_client,
    get_transcript_repo, get_settings
)
from app.config import Settings
from app.domains import Transcript
from app.interfaces import (
    OpenAIClientInterface, EmbedsClientInterface, TranscriptRepositoryInterface
)
from fastapi.testclient import TestClient
from fastapi import status
import json
import pytest


client = TestClient(app)

transcripts = {}
TRANSCRIPT_ID = 1000000
transcript_file = 'tests/samples/transcript_dummy.txt'
with open(transcript_file, 'r') as f:
    transcript_text = f.read()


class MockOpenAIClient(OpenAIClientInterface):
    """Mock class for OpenAI client"""

    def execute_completion(self, prompt: str,
                           model: str = '',
                           temperature: int = 0,
                           max_tokens: int = 100,
                           ) -> dict:
        tokens_used = len(prompt.split()) * 2
        cost = tokens_used * 0.000001
        return {
            'prompt': 'Have some fun',
            'output': 'Some text (0). Some other text (1)',
            'cost': cost,
            'tokens_used': tokens_used
        }

    def execute_embeds(self, text: str) -> dict:
        return {
            "embedding": [0.1, 0.2],
            "tokens_used": 10,
            "cost": 0.1
        }

    def execute_embeds_batch(self, request_list: 'list[str]',
                             object_id: int = None,
                             object_desc: str = None,
                             start_index: int = 0,
                             ) -> dict:
        return {
            "upsert_list": [],
            "request_ids": [],
            "tokens_used": 10,
            "cost": 0.1
        }


class MockEmbedsClient(EmbedsClientInterface):
    """Mock class for Embeddings Client"""

    def upsert(self, vectors: 'list[dict]'):
        pass

    def search(self, id: int, embedding: 'list[int]', limit: int = 5) -> dict:
        return {
            "matches": [{
                "id": "example-vector-1",
                "score": 0.08,
                "values": [0.1, 0.2, 0.3, 0.4],
                "sparseValues": {
                    "indices": [1, 312, 822, 14],
                    "values": [0.1, 0.2, 0.3]
                },
                "metadata": {
                    "text": "this is a transcript",
                    "object-id": 1,
                    "object-title": "Transcript Title",
                }
            }],
            "namespace": "string"
        }

    def delete(self, id: int):
        pass


class MockTranscriptRepo(TranscriptRepositoryInterface):
    """Mock class for Transcript Repository"""

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
    """Mock OpenAI client provider"""
    return MockOpenAIClient()


def get_mock_embeds_client():
    """Mock Embeddings client provider"""
    return MockEmbedsClient()


def get_mock_transcript_repo():
    """Mock Transcript Repository provider"""
    return MockTranscriptRepo()


def get_mock_settings():
    """Mock Settings provider"""
    settings = Settings(
        db_name='',
        db_host='',
        db_password='',
        db_port=1000,
        db_user='',
        openai_completions_api_key='',
        openai_embeddings_api_key='',
        line_min_size=5,
        chunk_min_words=20
    )
    return settings


def setup():
    """Setup before tests"""
    app.dependency_overrides[get_openai_client] = get_mock_openai_client
    app.dependency_overrides[get_embeds_client] = get_mock_embeds_client
    app.dependency_overrides[get_settings] = get_mock_settings
    app.dependency_overrides[get_transcript_repo] = get_mock_transcript_repo


def teardown():
    """Restore the state before setup was run"""
    transcripts.clear()
    app.dependency_overrides.clear()


@pytest.fixture()
def setup_teardown():
    """Fixture to run tests between setup and teardown"""
    setup()
    yield "Do Testing"
    teardown()


def test_get_transcript(setup_teardown):
    """Test get transcript method"""
    response = client.get(f"/transcript/{TRANSCRIPT_ID}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    response = client.post(
        f"/transcript/{TRANSCRIPT_ID}",
        content=transcript_text,
        headers={
            'Content-Type': 'text/plain'
        })
    assert response.status_code == status.HTTP_201_CREATED
    response = client.get(f"/transcript/{TRANSCRIPT_ID}")
    assert response.status_code == status.HTTP_200_OK
    data = json.loads(response.content)
    assert len(data) > 0
    response = client.delete(f"/transcript/{TRANSCRIPT_ID}")
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_save_transcript(setup_teardown):
    """Test save transcript method"""
    response = client.post(
        f"/transcript/{TRANSCRIPT_ID}",
        content=transcript_text,
        headers={
            'Content-Type': 'text/plain'
        })
    assert response.status_code == status.HTTP_201_CREATED
    response = client.post(
        f"/transcript/{TRANSCRIPT_ID}",
        content=transcript_text,
        headers={
            'Content-Type': 'text/plain'
        })
    assert response.status_code == status.HTTP_409_CONFLICT
    response = client.delete(f"/transcript/{TRANSCRIPT_ID}")
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_transcript(setup_teardown):
    """Test delete transcript method"""
    response = client.delete(f"/transcript/{TRANSCRIPT_ID}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    response = client.post(
        f"/transcript/{TRANSCRIPT_ID}",
        content=transcript_text,
        headers={
            'Content-Type': 'text/plain'
        })
    assert response.status_code == status.HTTP_201_CREATED
    response = client.delete(f"/transcript/{TRANSCRIPT_ID}")
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_get_metadata(setup_teardown):
    """Test get transcript metadata method."""
    response = client.get(
        f'/transcript/{TRANSCRIPT_ID}/metadata')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    response = client.post(
        f"/transcript/{TRANSCRIPT_ID}",
        content=transcript_text,
        headers={
            'Content-Type': 'text/plain'
        })
    assert response.status_code == status.HTTP_201_CREATED
    response = client.get(
        f'/transcript/{TRANSCRIPT_ID}/metadata')
    body = json.loads(response.content)
    assert 'title' in body
    assert 'interviewees' in body
    assert 'interviewers' in body
    response = client.delete(f"/transcript/{TRANSCRIPT_ID}")
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_get_summary(setup_teardown):
    """Test get transcript summary method"""
    response = client.get(
        f'/transcript/{TRANSCRIPT_ID}/summary?interviewee=Jason')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    response = client.post(
        f"/transcript/{TRANSCRIPT_ID}",
        content=transcript_text,
        headers={
            'Content-Type': 'text/plain'
        })
    assert response.status_code == status.HTTP_201_CREATED
    response = client.get(
        f'/transcript/{TRANSCRIPT_ID}/summary?interviewee=Jason')
    body = json.loads(response.content)
    assert body['cost'] > 0
    assert len(body['output']) > 0
    response = client.delete(f"/transcript/{TRANSCRIPT_ID}")
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_get_concise(setup_teardown):
    """Test get concise transcript method"""
    response = client.get(
        f'/transcript/{TRANSCRIPT_ID}/concise?interviewee=Jason')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    response = client.post(
        f"/transcript/{TRANSCRIPT_ID}",
        content=transcript_text,
        headers={
            'Content-Type': 'text/plain'
        })
    assert response.status_code == status.HTTP_201_CREATED
    response = client.get(
        f'/transcript/{TRANSCRIPT_ID}/concise?interviewee=Jason')
    body = json.loads(response.content)
    assert body['cost'] > 0
    assert len(body['output']) > 0
    response = client.delete(f"/transcript/{TRANSCRIPT_ID}")
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_create_embeds(setup_teardown):
    """Test create embeds method"""
    response = client.post(
        f"/transcript/{TRANSCRIPT_ID}/embeds?interviewee=Jason&title=Test")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    response = client.post(
        f"/transcript/{TRANSCRIPT_ID}",
        content=transcript_text,
        headers={
            'Content-Type': 'text/plain'
        })
    assert response.status_code == status.HTTP_201_CREATED
    response = client.post(
        f"/transcript/{TRANSCRIPT_ID}/embeds?interviewee=Jason&title=Test")
    assert response.status_code == status.HTTP_200_OK
    body = json.loads(response.content)
    assert body['cost'] > 0
    response = client.delete(f"/transcript/{TRANSCRIPT_ID}")
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_run_query(setup_teardown):
    """Test run query method"""
    response = client.post(
        f"/transcript/{TRANSCRIPT_ID}/query?ask=test")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    response = client.post(
        f"/transcript/{TRANSCRIPT_ID}",
        content=transcript_text,
        headers={
            'Content-Type': 'text/plain'
        })
    assert response.status_code == status.HTTP_201_CREATED
    response = client.post(
        f"/transcript/{TRANSCRIPT_ID}/query?ask=test")
    assert response.status_code == status.HTTP_200_OK
    body = json.loads(response.content)
    assert body['cost'] > 0
    assert len(body['output']) > 0
    response = client.delete(f"/transcript/{TRANSCRIPT_ID}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
