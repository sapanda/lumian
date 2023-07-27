import logging
logger = logging.getLogger(__name__)


def pre_process_transcript(text: str):
    text_after_removing_return_carriage = text.replace('\r', '\n')
    lines_after_removing_extra_newlines = [
        line.strip()
        for line in text_after_removing_return_carriage.split('\n')
        if line.strip()]
    new_text = '\n'.join(lines_after_removing_extra_newlines)
    return new_text


def is_valid_transcript_format(text: str):
    lines = text.split('\n')
    # Initialize a flag to keep track of the format validation
    valid_format = True

    # Check each line to ensure it matches the pattern
    for line in lines:
        if len(line.split(": ")) <= 1:
            valid_format = False
            break

    return valid_format
