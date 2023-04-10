from app.server import app
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
transcript_file = 'tests/samples/transcript_short.txt'
with open(transcript_file, 'r') as f:
    global transcript_text
    transcript_text = f.read()


def setup():
    """Setup before tests"""
    # nothing to be done
    pass


def teardown():
    """Restore the state before setup was run"""
    # nothing to be done
    pass


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
    response = client.post(
        f"/transcript/{TRANSCRIPT_ID}",
        content=transcript_text,
        headers={
            'Content-Type': 'text/plain'
        })
    assert response.status_code == status.HTTP_409_CONFLICT
    response = client.delete(f"/transcript/{TRANSCRIPT_ID}")
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.skipif(TEST_ENV_IS_LOCAL, reason=OPENAI_COSTS_REASON)
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
    assert response.status_code == status.HTTP_204_NO_CONTENT
    response = client.delete(f"/transcript/{TRANSCRIPT_ID}")
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.skipif(TEST_ENV_IS_LOCAL, reason=OPENAI_COSTS_REASON)
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


@pytest.mark.skipif(TEST_ENV_IS_LOCAL, reason=OPENAI_COSTS_REASON)
def test_get_concise(setup_teardown):
    """Test get concise transcript"""
    response = client.get(
        f'/transcript/{TRANSCRIPT_ID}/concise?interviewee=Jason')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    response = client.post(
        f"/transcript/{TRANSCRIPT_ID}",
        content=transcript_text,
        headers={
            'Content-Type': 'text/plain'
        })
    assert response.status_code == status.HTTP_204_NO_CONTENT
    response = client.get(
        f'/transcript/{TRANSCRIPT_ID}/concise?interviewee=Jason')
    body = json.loads(response.content)
    assert body['cost'] > 0
    assert len(body['output']) > 0
    concise = ''.join([item['text'] for item in body['output']])
    assert 'Jason' in concise
    assert len(concise.split()) > 0
    response = client.delete(f"/transcript/{TRANSCRIPT_ID}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
