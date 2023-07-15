import datetime
from django.contrib.auth import get_user_model
from django.utils import timezone
import json
from typing import Dict

from .models import Project
from transcript.models import Transcript
from transcript.repository import create_synthesis_entry


User = get_user_model()


def load_content() -> Dict:
    """Load sample content from files"""
    path_metadata = "/api/project/samples/metadata.json"
    path_transcript = "/api/project/samples/transcript.txt"

    with open(path_metadata) as file:
        metadata = json.load(file)
    with open(path_transcript) as file:
        transcript = file.read()
    metadata['transcript']['transcript'] = transcript
    return metadata


def create_project(user: User) -> None:
    """Create sample project with sample content"""
    content = load_content()
    pjt = Project.objects.create(
        user=user,
        title=content['project']['title'],
        goal=content['project']['goal'],
        questions=content['project']['questions'])

    transcript_duration = content['transcript']['duration']
    start_time = timezone.now()
    end_time = start_time + datetime.timedelta(minutes=transcript_duration)

    tct = Transcript.objects.create(
        project=pjt,
        title=content['transcript']['title'],
        interviewee_names=content['transcript']['interviewee_names'],
        interviewer_names=content['transcript']['interviewer_names'],
        transcript=content['transcript']['transcript'],
        start_time=start_time,
        end_time=end_time
    )
    create_synthesis_entry(tct)
