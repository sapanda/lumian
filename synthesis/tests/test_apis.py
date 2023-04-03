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
TRANSCRIPT_ID = 1000000


def setup():
    """Setup before tests"""
    transcript_file = 'tests/test_transcript.txt'
    with open(transcript_file, 'r') as f:
        global transcript_text
        transcript_text = f.read()


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


@pytest.mark.skipif(TEST_ENV_IS_LOCAL, reason=OPENAI_COSTS_REASON)
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
    assert response.status_code == status.HTTP_204_NO_CONTENT
    response = client.get(f"/transcript/{TRANSCRIPT_ID}")
    assert response.status_code == status.HTTP_200_OK
    data = json.loads(response.content)
    assert len(data) > 0
    response = client.delete(f"/transcript/{TRANSCRIPT_ID}")
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.skipif(TEST_ENV_IS_LOCAL, reason=OPENAI_COSTS_REASON)
def test_save_transcript(setup_teardown):
    """Test save transcript method"""
    response = client.post(
        f"/transcript/{TRANSCRIPT_ID}",
        content=transcript_text,
        headers={
            'Content-Type': 'text/plain'
        })
    assert response.status_code == status.HTTP_204_NO_CONTENT
    response = client.delete(f"/transcript/{TRANSCRIPT_ID}")
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.skipif(TEST_ENV_IS_LOCAL, reason=OPENAI_COSTS_REASON)
def test_delete_transcript(setup_teardown):
    """Test delete transcript method"""
    response = client.post(
        f"/transcript/{TRANSCRIPT_ID}",
        content=transcript_text,
        headers={
            'Content-Type': 'text/plain'
        })
    assert response.status_code == status.HTTP_204_NO_CONTENT
    response = client.delete(f"/transcript/{TRANSCRIPT_ID}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    response = client.delete("/transcript/0")
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.skipif(TEST_ENV_IS_LOCAL, reason=OPENAI_COSTS_REASON)
def test_get_summary(setup_teardown):
    """Test get transcript summary method"""
    response = client.post(
        f"/transcript/{TRANSCRIPT_ID}",
        content=transcript_text,
        headers={
            'Content-Type': 'text/plain'
        })
    assert response.status_code == status.HTTP_204_NO_CONTENT
    response = client.get(
        f'/transcript/{TRANSCRIPT_ID}/summary?interviewee=Jason')
    body = json.loads(response.content)
    assert body['cost'] > 0
    assert len(body['output']) > 0
    summary = ''.join([item['text'] for item in body['output']])
    assert 'Jason' in summary
    assert len(summary.split()) > 0
    response = client.delete(f"/transcript/{TRANSCRIPT_ID}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
