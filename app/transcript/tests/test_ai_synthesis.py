"""
Tests for the synthesis of LLM inputs.
"""
from django.test import TestCase
from unittest import skip
from unittest.mock import patch
from transcript.models import SynthesisType
from transcript.tasks import (
    _get_summarized_chunk,
    _get_summarized_all,
    _process_chunks,
    _generate_summary,
    OPENAI_MODEL_COMPLETIONS,
    OPENAI_MODEL_CHAT,
)
from transcript.tests.utils import (
    create_user,
    create_transcript
)


@skip("Minimal testing due to OpenAI API costs")
class GenerateSummaryTests(TestCase):
    """Test Summary Generation."""

    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='testpass123',
            name='Test Name',
        )
        with open('transcript/tests/data/transcript_short.txt', 'r') as f:
            self.sample_transcript = f.read()

    def test_get_summarized_chunk(self):
        """Test retrieving a summary for a chunk of the transcript."""

        transcript = ("Jason: \"Hello, my name is Jason. I am a student.\"\n\n"
                      "Bob: \"What is your favorite color?\"\n\n"
                      "Jason: \"My favorite color is blue.\"\n\n")

        result = _get_summarized_chunk(transcript,
                                       model=OPENAI_MODEL_CHAT,
                                       interviewee='Jason')
        chunk_summary = result['summary']
        self.assertTrue('Jason' in chunk_summary)
        self.assertTrue('Bob' in chunk_summary)
        self.assertGreater(result['tokens_used'], 0)

    def test_get_summarized_all(self):
        """Test retrieving a summary from a concatenated summary string."""

        text = ("In this interview, Jason introduces himself as a "
                "student. Bob then asks him what his favorite color "
                "is, to which Jason responds that it is blue.")

        result = _get_summarized_all(text, model=OPENAI_MODEL_COMPLETIONS)
        summary = result['summary']
        self.assertTrue('Jason' in summary)
        self.assertTrue('Bob' in summary)
        self.assertGreater(result['tokens_used'], 0)

    @patch('transcript.signals._run_generate_synthesis')
    def test_generate_summary(self, patched_signal):
        """Test transcript summary generation."""
        tct = create_transcript(
            user=self.user,
            transcript=self.sample_transcript
        )

        chunks = _process_chunks(tct)
        self.assertEqual(chunks.chunk_type, SynthesisType.SUMMARY)
        self.assertGreater(len(chunks.chunks), 1,
                           "Not enough chunks generated")
        self.assertEqual(len(chunks.chunks_processed), len(chunks.chunks),
                         "Unequal number of chunks and summaries")
        self.assertEqual(len(chunks.chunks_processed), len(chunks.tokens_used),
                         "Unequal number of tokens and summaries")
        self.assertGreater(chunks.cost, 0, "No cost calculated")
        for tokens_used in chunks.tokens_used:
            self.assertGreater(tokens_used, 0, "No tokens used")

        summary = _generate_summary(tct, chunks)
        self.assertGreater(len(summary.output), 0, "Empty summary generated")
        self.assertEqual(summary.output_type, SynthesisType.SUMMARY)
        self.assertGreater(summary.tokens_used, 0, "No tokens used")
        self.assertGreater(summary.total_cost, 0, "No cost calculated")
