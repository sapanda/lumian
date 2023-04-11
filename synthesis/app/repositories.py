from sqlalchemy.orm import Session

from . import domains, models
from .interfaces import TranscriptRepositoryInterface


class TranscriptRepository(TranscriptRepositoryInterface):
    """Repository instance providing methods for storing, retrieving
    and deleting transcript"""

    def __init__(self, session: Session):
        self.session = session

    def get(self, id: int) -> domains.Transcript:
        """Get a transcript from storage"""
        # TODO: handle database related errors
        tct = self.session.query(models.Transcript) \
            .filter(models.Transcript.id == id).first()
        if not tct:
            return None
        return domains.Transcript(id=tct.id, data=tct.data)

    def save(self, transcript: domains.Transcript):
        """Save transcript to storage"""
        # TODO: handle database related errors
        tct = models.Transcript(id=transcript.id, data=transcript.data)
        self.session.add(tct)
        self.session.commit()

    def replace(self, transcript: domains.Transcript):
        """Replace transcript in storage"""
        # TODO: handle database related errors
        self.delete(id=transcript.id)
        self.save(transcript=transcript)

    def delete(self, id: int):
        """Delete transcript of transcript"""
        # TODO: handle database related errors
        tct = self.session.query(models.Transcript) \
            .filter(models.Transcript.id == id).first()
        self.session.delete(tct)
        self.session.commit()
