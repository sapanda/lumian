DEFAULT_CHUNK_MIN_SIZE = 150


def chunk_by_paragraph_groups(
        text: str,
        interviewee: str,
        min_size: int = DEFAULT_CHUNK_MIN_SIZE):
    """
    Chunk the transcript by paragraph groups. A paragraph group is a collection
    of paragraphs that always starts with text spoken by the interviewee.
    """

    paragraphs = text.split("\n\n")
    paragraph_groups = []
    current_group = ""
    current_length = 0

    index = 0
    for paragraph in paragraphs:
        # Strip leading/trailing whitespace and add paragraph to current group
        new_para = paragraph.strip()
        current_group += new_para + " \n\n"
        current_length += len(new_para.split())

        # If the current group is over CHUNK_MIN_SIZE words, start a new group
        if current_length > min_size:

            # Only create a group if next para starts with an interviewer
            if (index == len(paragraphs) - 1) or \
                    not (paragraphs[index+1].startswith(interviewee)):
                paragraph_groups.append(current_group)
                current_group = ""
                current_length = 0

        index += 1

    # Check if current group is not empty and adding it to the paragraph group
    if current_group:
        paragraph_groups.append(current_group)

    return paragraph_groups
