"""
Tests for the AI Utils file.
"""
from django.test import TestCase
from transcript.ai.utils import (
    chunk_by_paragraph_groups,
)


class ParagraphGroupChunkingTests(TestCase):
    """Test paragraph-group chunking function."""

    def setUp(self):
        self.interviewee = 'Jason'
        self.min_size = 150

    def test_function_success(self):
        """Test that the function returns the correct paragraph groups."""
        with open('transcript/tests/data/transcript_short.txt', 'r') as f:
            para_groups = chunk_by_paragraph_groups(
                text=f.read(),
                interviewee=self.interviewee,
                min_size=self.min_size,
            )

        index = 0
        for para_group in para_groups:
            if index > 0:
                # Except for first paragroup, the rest
                # shouldn't start with interviewee
                self.assertFalse(para_group.startswith(self.interviewee))
            if index < len(para_groups) - 1:
                # Except for last paragroup, the rest
                # shouldn't be shorter than self.min_size
                self.assertTrue(len(para_group) > self.min_size)
            index += 1
