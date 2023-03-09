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
    _get_concise_chunk,
    _generate_chunks,
    _process_chunks_for_summaries,
    _process_chunks_for_concise,
    _generate_summary,
    _generate_concise,
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
        chunk_summary = result['output']
        self.assertTrue('Jason' in chunk_summary)
        self.assertTrue('Bob' in chunk_summary)
        self.assertGreater(result['tokens_used'], 0)

    def test_get_summarized_all(self):
        """Test retrieving a summary from a concatenated summary string."""

        text = ("In this interview, Jason introduces himself as a "
                "student. Bob then asks him what his favorite color "
                "is, to which Jason responds that it is blue.")

        result = _get_summarized_all(text,
                                     model=OPENAI_MODEL_COMPLETIONS)
        summary = result['output']
        self.assertTrue('Jason' in summary)
        self.assertTrue('Bob' in summary)
        self.assertGreater(result['tokens_used'], 0)

    def test_get_concise_chunk(self):
        """Test retrieving a summary for a chunk of the transcript."""
        transcript = ("Jason: \"Hello, my name is Jason. I am a student.\"\n\n"
                      "Jason: \"Hello, I'm Jason. I'm a student.\"\n\n"
                      "Bob: \"Uhm Uhm yeah Uhm uhm whats your color?\"\n\n"
                      "Jason: \"My favorite color is blue.\"\n\n")

        result = _get_concise_chunk(transcript,
                                    model=OPENAI_MODEL_CHAT)
        summary = result['output']
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

        chunks = _generate_chunks(tct)

        summary_chunks = _process_chunks_for_summaries(tct, chunks)
        self.assertEqual(summary_chunks.chunk_type, SynthesisType.SUMMARY)
        self.assertGreater(len(summary_chunks.chunks), 1,
                           "Not enough chunks generated")
        self.assertEqual(len(summary_chunks.chunks_processed),
                         len(summary_chunks.chunks),
                         "Unequal number of chunks and summaries")
        self.assertEqual(len(summary_chunks.chunks_processed),
                         len(summary_chunks.tokens_used),
                         "Unequal number of tokens and summaries")
        self.assertGreater(summary_chunks.cost, 0, "No cost calculated")
        for tokens_used in summary_chunks.tokens_used:
            self.assertGreater(tokens_used, 0, "No tokens used")

        summary = _generate_summary(tct, summary_chunks)
        self.assertGreater(len(summary.output), 0, "Empty summary generated")
        self.assertEqual(summary.output_type, SynthesisType.SUMMARY)
        self.assertGreater(summary.tokens_used, 0, "No tokens used")
        self.assertGreater(summary.total_cost, 0, "No cost calculated")

    @patch('transcript.signals._run_generate_synthesis')
    def test_generate_concise(self, patched_signal):
        """Test concise transcript generation."""
        tct = create_transcript(
            user=self.user,
            transcript=self.sample_transcript
        )

        chunks = _generate_chunks(tct)

        concise_chunks = _process_chunks_for_concise(tct, chunks)
        self.assertEqual(concise_chunks.chunk_type, SynthesisType.CONCISE)
        self.assertGreater(len(concise_chunks.chunks), 1,
                           "Not enough chunks generated")
        self.assertEqual(len(concise_chunks.chunks_processed),
                         len(concise_chunks.chunks),
                         "Unequal number of chunks and concise chunks")
        self.assertEqual(len(concise_chunks.chunks_processed),
                         len(concise_chunks.tokens_used),
                         "Unequal number of tokens and concise chunks")
        self.assertGreater(concise_chunks.cost, 0, "No cost calculated")
        for tokens_used in concise_chunks.tokens_used:
            self.assertGreater(tokens_used, 0, "No tokens used")

        concise = _generate_concise(tct, concise_chunks)
        self.assertGreater(len(concise.output), 0, "Empty concise generated")
        self.assertEqual(concise.output_type, SynthesisType.CONCISE)
        self.assertEqual(concise.tokens_used, 0,
                         "Concise final step shouldn't use tokens")
        self.assertGreater(concise.total_cost, 0, "No cost calculated")
