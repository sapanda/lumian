"""
Tests for the synthesis of LLM inputs.
"""
from django.test import TestCase
from unittest import skip
from unittest.mock import patch
from transcript.models import AISynthesis
from transcript.tasks import (
    _get_summarized_chunk,
    _get_summarized_all,
    _process_chunks,
    _generate_summary,
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

    def test_get_summarized_chunk(self):
        """Test retrieving a summary for a chunk of the transcript."""
        transcript = ("Jason: \"Hello, my name is Jason. I am a student.\"\n\n"
                      "Bob: \"What is your favorite color?\"\n\n"
                      "Jason: \"My favorite color is blue.\"\n\n")

        chunk_summary = _get_summarized_chunk(transcript)
        self.assertTrue("Jason" in chunk_summary)
        self.assertTrue("Bob" in chunk_summary)

    def test_get_summarized_all(self):
        """Test retrieving a summary from a concatenated summary string."""
        text = ("In this interview, Jason introduces himself as a "
                "student. Bob then asks him what his favorite color "
                "is, to which Jason responds that it is blue.")

        summary = _get_summarized_all(text)
        self.assertTrue("Jason" in summary)
        self.assertTrue("Bob" in summary)

    @patch('transcript.signals._run_generate_synthesis')
    def test_generate_summary(self, patched_signal):
        """Test transcript summary generation."""
        tct = create_transcript(user=self.user)
        with open('transcript/tests/data/transcript_short.txt', 'r') as f:
            tct.transcript = f.read()

        tct = _process_chunks(tct)
        self.assertTrue(len(tct.chunks.para_groups) > 1,
                        "Not enough chunks generated")
        self.assertEqual(len(tct.chunks.para_group_summaries),
                         len(tct.chunks.para_groups),
                         "Unequal number of groups and summaries")

        tct = _generate_summary(tct)

        self.assertTrue(len(tct.summary.output) > 0, "Empty summary generated")
        self.assertEquals(tct.summary.output_type,
                          AISynthesis.SynthesisType.SUMMARY)
