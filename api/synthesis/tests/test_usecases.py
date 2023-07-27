from django.test import TestCase
from typing import List, Dict

from transcript.tests.utils import (
    create_transcript, create_project, create_user
)
from synthesis.interfaces import (
    OpenAIClientInterface, EmbedsClientInterface
)
from synthesis.errors import (
    ObjectNotFoundException, ObjectAlreadyPresentException
)
from synthesis.models import ProcessedTranscript
from synthesis import usecases
from synthesis.synthesis import Synthesis


class MockOpenAIClient(OpenAIClientInterface):
    """Mock class for OpenAI client"""

    def execute_chat_completion(self, prompt: str,
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

    def execute_chat(self, messages: List[Dict[str, str]] = None,
                     model: str = '',
                     temperature: int = 0,
                     max_tokens: int = 100,
                     ) -> dict:
        tokens_used = len("Have some fun".split()) * 2
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

    def execute_embeds_batch(self, request_list: List[str],
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

    def upsert(self, vectors: List[dict]):
        pass

    def search(self, id: int, embedding: List[int], limit: int = 5) -> dict:
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


with open('synthesis/tests/samples/transcript_dummy.txt', 'r') as f:
    SAMPLE_TRANSCRIPT = f.read()


class SynthesisMockTests(TestCase):
    """Test class for Synthesis API with mocks"""

    def setUp(self):
        """Set up test"""
        self.synthesis = Synthesis(
            openai_client=MockOpenAIClient(),
            embeds_client=MockEmbedsClient()
        )
        self.user = create_user(
            email='test@example.com',
            password='testpass123',
            name='Test Name',
        )
        self.project = create_project(self.user)
        self.transcript = create_transcript(
            project=self.project,
            transcript=SAMPLE_TRANSCRIPT,
            interviewee_names=['Jason'],
        )

    def test_process_transcript(self):
        """Test process transcript method"""
        usecases.process_transcript(self.transcript)
        ptct = ProcessedTranscript.objects.get(transcript=self.transcript)
        with self.assertRaises(ObjectAlreadyPresentException):
            usecases.process_transcript(self.transcript)
        ptct.delete()

    def test_get_summary(self):
        """Test get transcript summary method"""
        with self.assertRaises(ObjectNotFoundException):
            usecases.get_transcript_summary(
                self.transcript, self.synthesis)
        usecases.process_transcript(self.transcript)
        summary = usecases.get_transcript_summary(
            self.transcript, self.synthesis)
        self.assertTrue(summary['cost'] > 0)
        self.assertTrue(len(summary['output']) > 0)

    def test_get_concise(self):
        """Test get transcript concise method"""
        with self.assertRaises(ObjectNotFoundException):
            usecases.get_transcript_concise(
                self.transcript, self.synthesis)
        usecases.process_transcript(self.transcript)
        concise = usecases.get_transcript_concise(
            self.transcript, self.synthesis)
        self.assertTrue(concise['cost'] > 0)
        self.assertTrue(len(concise['output']) > 0)

    def test_create_embeds(self):
        """Test create embeds method"""
        with self.assertRaises(ObjectNotFoundException):
            usecases.create_transcript_embeds(
                self.transcript, self.synthesis)
        usecases.process_transcript(self.transcript)
        embeds = usecases.create_transcript_embeds(
            self.transcript, self.synthesis)
        self.assertTrue(embeds['cost'] > 0)

    def test_run_query(self):
        """Test run query method"""
        with self.assertRaises(ObjectNotFoundException):
            usecases.run_transcript_query(
                self.transcript, "test", self.synthesis)
        usecases.process_transcript(self.transcript)
        usecases.create_transcript_embeds(
            self.transcript, self.synthesis)
        result = usecases.run_transcript_query(
            self.transcript, "test", self.synthesis)
        self.assertTrue(result['cost'] > 0)
        self.assertTrue(len(result['output']) > 0)
