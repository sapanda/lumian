"""
Tests for the synthesis of LLM inputs.
"""
from django.conf import settings
from django.test import TestCase
import pinecone
from unittest import skipIf
from unittest.mock import patch
from transcript.models import SynthesisType
from transcript.tasks import (
    OPENAI_MODEL_COMPLETIONS,
    OPENAI_MODEL_CHAT,
    OPENAI_EMBEDDING_DIMENSIONS,
    _get_summarized_chunk,
    _get_summarized_all,
    _get_concise_chunk,
    _generate_chunks,
    _process_chunks_for_summaries,
    _process_chunks_for_concise,
    _generate_summary,
    _generate_concise,
    _create_batches_for_embeds,
    _execute_openai_embeds,
    _execute_openai_embeds_and_upsert,
    _create_index_name,
    _init_pinecone_index,
    _generate_embeds,
    _execute_pinecone_search,
    _execute_openai_query,
    run_openai_query,
)
from transcript.tests.utils import (
    TEST_INDEX_NAME,
    create_user,
    create_transcript
)


@skipIf(settings.TEST_ENV_IS_LOCAL,
        "OpenAI Costs: Run only when testing AI Synthesis changes")
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


class GenerateEmbedsTests(TestCase):
    """Test Embeds Generation."""

    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='testpass123',
            name='Test Name',
        )
        with open('transcript/tests/data/transcript_short.txt', 'r') as f:
            self.sample_transcript = f.read()

    def test_create_embeds_batches_empty(self):
        """Test batching with empty input."""
        content_list = []
        batches = _create_batches_for_embeds(content_list, 10)
        self.assertEqual(len(batches), 0)

    def test_create_embeds_batches_valid(self):
        """Test batching with valid input."""
        content_list = ['1234', '1234', '1234', '1234', '1234']
        expected_output = [['1234', '1234'], ['1234', '1234'], ['1234']]
        batches = _create_batches_for_embeds(content_list, 10)
        self.assertEqual(batches, expected_output)

    def test_create_embeds_batches_exact_length(self):
        """Test batching with input length matching character limit."""
        content_list = ['12345', '12345', '12345']
        expected_output = [['12345', '12345'], ['12345']]
        batches = _create_batches_for_embeds(content_list, 10)
        self.assertEqual(batches, expected_output)

    def test_execute_openai_embeds_empty(self):
        """Test embeds generation failure with empty input."""
        results = _execute_openai_embeds([], 0)
        self.assertIsNone(results)

    @skipIf(settings.TEST_ENV_IS_LOCAL,
            "OpenAI Costs: Run only when testing AI Synthesis changes")
    def test_execute_openai_embeds_valid(self):
        """Test embeds generation with valid input."""
        request = ["Jason: \"Hello, my name is Jason. I am a student.\"\n\n",
                   "Bob: \"What is your favorite color?\"\n\n",
                   "Jason: \"My favorite color is blue.\"\n\n"]
        results = _execute_openai_embeds(request, 0)
        upsert_list = results['upsert_list']

        index = 0
        for result in upsert_list:
            self.assertEqual(result[0], str(index),
                             "Index doesn't match input")
            self.assertEqual(len(result[1]), OPENAI_EMBEDDING_DIMENSIONS,
                             "Number of dimensions doesn't match")
            self.assertEqual(result[2]['text'], request[index],
                             "Request strings don't match input")
            index += 1

        self.assertGreater(results['token_count'], 0, "No tokens used")

    @patch('transcript.signals._run_generate_synthesis')
    def test_create_index_name(self, patched_signal):
        """Test index name generation."""
        tct = create_transcript(user=self.user)

        test_data_list = [
            {'title': '', 'name': f'{tct.id}--'},
            {'title': 'Test Title', 'name': f'{tct.id}--test-title'},
            {'title': '!@#$%^&*()', 'name': f'{tct.id}--'},
            {'title': '123 Test', 'name': f'{tct.id}--123-test'},
            {'title': 'Test 123', 'name': f'{tct.id}--test-123'},
            {'title': 'Test 123---', 'name': f'{tct.id}--test-123'},
            {'title': 'Test 123 (Short + Embeds)',
             'name': f'{tct.id}--test-123-short-embeds'},
        ]

        for test_data in test_data_list:
            tct.title = test_data['title']
            index_name = _create_index_name(tct)
            self.assertEqual(index_name, test_data['name'])

    @skipIf(settings.TEST_ENV_IS_LOCAL,
            "Pinecone Speed: Very slow due to time to create/delete index")
    def test_create_pinecone_index(self):
        """Test pinecone index creation."""
        index_name = 'synthesis-api-test-temp'
        _init_pinecone_index(index_name,
                             dimension=OPENAI_EMBEDDING_DIMENSIONS)
        description = pinecone.describe_index(index_name)

        self.assertEqual(description.name, index_name)
        self.assertEqual(description.dimension, OPENAI_EMBEDDING_DIMENSIONS)
        pinecone.delete_index(index_name)

    @skipIf(settings.TEST_ENV_IS_LOCAL,
            "OpenAI Costs: Run only when testing AI Synthesis changes")
    @patch('transcript.signals._run_generate_synthesis')
    def test_generate_embeds(self, patched_signal):
        """Test full embeds generation."""
        tct = create_transcript(
            user=self.user,
            transcript=self.sample_transcript
        )

        chunks = _generate_chunks(tct)
        embeds_obj = _generate_embeds(tct, chunks)

        self.assertGreater(embeds_obj.index_cost, 0, "No cost calculated")
        self.assertEqual(len(embeds_obj.chunks), len(chunks),
                         "Chunks length doesn't match")

        pinecone.delete_index(embeds_obj.index_name)


@patch('transcript.signals._run_generate_synthesis')
class QueryEmbedsTests(TestCase):
    """Test Querying a Transcript using Embeds."""

    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='testpass123',
            name='Test Name',
        )
        with open('transcript/tests/data/transcript_short.txt', 'r') as f:
            sample_transcript = f.read()

        self.tct = create_transcript(
            user=self.user,
            transcript=sample_transcript
        )

        # Create and populate the index if it doesn't exist
        # In the future just use this index for all tests in this class
        if TEST_INDEX_NAME not in pinecone.list_indexes():
            index = _init_pinecone_index(index_name=TEST_INDEX_NAME,
                                         dimension=OPENAI_EMBEDDING_DIMENSIONS)
            chunks = _generate_chunks(self.tct)
            _execute_openai_embeds_and_upsert(index, chunks)

    @skipIf(settings.TEST_ENV_IS_LOCAL,
            "OpenAI Costs: Run only when testing AI Synthesis changes")
    def test_execute_pinecone_search(self, patched_signal):
        """Test pinecone search execution."""
        query = "Where does Jason live?"
        search_result = _execute_pinecone_search(self.tct, query)

        self.assertGreater(len(search_result['matches']), 1,
                           "Not enough matches")
        for match in search_result['matches']:
            self.assertTrue('Jason' in match['metadata']['text'],
                            "Bad match string returned")

    @skipIf(settings.TEST_ENV_IS_LOCAL,
            "Pinecone Speed: Very slow due to time to query index")
    def test_execute_openai_query(self, patched_signal):
        """Test Open AI query execution."""
        query = "Who likes blue?"
        chosen_sections = ["Jason: \"Hello, I am a student.\"\n\n",
                           "Bob: \"What is your favorite color?\"\n\n",
                           "Jason: \"My favorite color is blue.\"\n\n"]
        model = OPENAI_MODEL_CHAT
        result = _execute_openai_query(query, model, chosen_sections)

        self.assertGreater(result['tokens_used'], 0, "No tokens used")
        self.assertTrue('Jason' in result['output'], "Poor response generated")

    @skipIf(settings.TEST_ENV_IS_LOCAL,
            "OpenAI Costs: Run only when testing AI Synthesis changes")
    def test_run_full_query(self, patched_signal):
        """Test a full query on a short transcript."""
        query = "Where does Jason live?"
        result = run_openai_query(self.tct, query)

        self.assertGreater(result['tokens_used'], 0, "No tokens used")
        self.assertTrue('Boise' in result['output'], "Poor response generated")
