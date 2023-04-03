import json
from psycopg2._psycopg import connection
from .interfaces import TranscriptRepositoryInterface
from .domains import Transcript


class TranscriptRepository(TranscriptRepositoryInterface):
    """Repository instance providing methods for storing, retrieving
    and deleting transcript"""

    def __init__(self, conn: connection):
        self.conn = conn

    def get(self, id: int) -> Transcript:
        """Get a transcript from storage"""
        # TODO: handle database related errors
        with self.conn:
            with self.conn.cursor() as cur:
                cur.execute(
                    "SELECT data FROM synthesis.transcript WHERE id = %s",
                    (id,))
                data = cur.fetchone()
                if not data:
                    return None
        return Transcript(
            id=id,
            data=data[0]
        )

    def save(self, transcript: Transcript):
        """Save transcript to storage"""
        # TODO: handle database related errors
        with self.conn:
            with self.conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO synthesis.transcript(id,data) VALUES (%s,%s)",
                    (transcript.id, json.dumps(transcript.data)))

    def replace(self, transcript: Transcript):
        """Replace transcript in storage"""
        # TODO: handle database related errors
        self.delete(id=transcript.id)
        self.save(transcript=transcript)

    def delete(self, id: int):
        """Delete transcript of transcript"""
        # TODO: handle database related errors
        with self.conn:
            with self.conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM synthesis.transcript WHERE id = %s", (id,))
