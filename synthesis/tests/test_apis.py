from app.server import app, get_transcript_repo
from app.domains import Transcript
from app.interfaces import TranscriptRepositoryInterface
from fastapi.testclient import TestClient
from fastapi import status
import json
import pytest
import os

TEST_ENV_IS_LOCAL = os.getenv('TEST_ENV_IS_LOCAL') == '1'
OPENAI_COSTS_REASON = "OpenAI Costs: Run only when\
 testing AI Synthesis changes"
client = TestClient(app)

transcripts = {}


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


def get_mock_transcript_repo():
    return MockTranscriptRepo()


def setup():
    transcript_file = 'tests/test_transcript.txt'
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


@pytest.mark.skipif(TEST_ENV_IS_LOCAL, reason=OPENAI_COSTS_REASON)
def test_get_summary(setup_teardown):
    response = client.post(
        "/transcript/0",
        content=transcript_text,
        headers={
            'Content-Type': 'text/plain'
        })
    assert response.status_code == status.HTTP_204_NO_CONTENT
    response = client.get('/transcript/0/summary?interviewee=User1')
    body = json.loads(response.content)
    assert body['cost'] > 0
    assert len(body['output']) > 0
    summary = ''.join([item['text'] for item in body['output']])
    assert 'Jason' in summary
    assert len(summary.split()) > 0
