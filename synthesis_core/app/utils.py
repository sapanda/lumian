import re

# Engineering Params
LINE_MIN_SIZE = 90
CHUNK_MIN_WORDS = 500


def split_text_into_multiple_lines_for_speaker(
        text: str
) -> list[tuple[str, int, int]]:
    """Takes in a string `text` and splits it into multiple lines where each
    line is at least `LINE_MIN_SIZE` characters long and ends with a period
    (.),question mark (?) or exclamation mark (!). Each line starts with the
    name of the speaker."""
    paras = text.strip().split("\n\n")
    start_loc, results = 0, []
    for para in paras:
        speech_parts = para.split(": ", 1)
        speaker = speech_parts[0]
        speech_text_words = re.split("(\W)", speech_parts[1].strip('"'))
        start_loc += len(speaker) + 3
        temp_words, line_length = [], 0
        n = len(speech_text_words)
        for i in range(n):
            string = speech_text_words[i]
            temp_words.append(string)
            line_length += len(string)
            if (
                line_length >= LINE_MIN_SIZE and temp_words[-1] in
                    [".", "?", "!"]
            ) or i == n - 1:
                sentence = ("".join(temp_words)).strip()
                if len(sentence):
                    results.append(
                        (
                            f"{speaker}: {''.join(temp_words)}",
                            start_loc,
                            start_loc + line_length,
                        )
                    )
                start_loc += line_length
                temp_words, line_length = [], 0
        start_loc += 3
    return results


def split_indexed_lines_into_chunks(text: str) -> list[list[str]]:
    """Split indexed lines into chunks"""
    results, cur_results, lines, chunk_size = [], [], text.split("\n"), 0
    n = len(lines)
    for i in range(n):
        line = lines[i]
        cur_results.append(line)
        chunk_size += len(line.split())
        if chunk_size > CHUNK_MIN_WORDS or i == n - 1:
            results.append(cur_results)
            cur_results, chunk_size = [], 0
    return results


def split_indexed_transcript_lines_into_chunks(
    text: str, interviewee: str
) -> list[list[str]]:
    """Split indexed lines into chunks. No chunk (except the first) should
    start with 'interviewee' name"""
    results, cur_results, lines, chunk_size = [], [], text.split("\n"), 0
    n = len(lines)
    for i in range(n):
        line = lines[i]
        cur_results.append(line)
        words = line.split()
        chunk_size += len(words)
        if i == n - 1 or (
            chunk_size > CHUNK_MIN_WORDS
            and (lines[i + 1].split(" ", 1))[1].startswith(interviewee)
        ):
            results.append(cur_results)
            cur_results, chunk_size = [], 0
    return results


def split_and_extract_indices(
        input_string: str
) -> list[tuple[str, list[int]]]:
    """Split the lines into sentences and extract indices
    from parenthesis mentioned at the end of indices
    input_string: "Some text (2-3), some more text (10,13).
                Some more new text (1,4-5,15)"
    output: [("Some text",[2,3]),
            (", some more text", [10, 11, 12, 13)]),
            (".Some more new text", [1, 4, 5, 15])]
    """
    pattern = re.compile(r"(.+?)\s*\(([\d\s,-]+)\)")
    matches = pattern.findall(input_string)
    return [(match[0], parse_indices(match[1])) for match in matches]


def parse_indices(input_string: str) -> list[int]:
    """Parse the indices string and generate an equivalent
    integer list representation
    input_string: 1,3-5,9
    output: [1,3,4,5,9]
    """
    pattern = re.compile(
        r"(\s*(\d+)-(\d+)|\s*(\d+))(,(\s*(\d+)-(\d+)|\s*(\d+)))*")
    if not pattern.match(input_string):
        return None
    results = set()
    indices = input_string.split(",")
    for index in indices:
        if "-" in index:
            start, end = tuple(map(int, index.split("-")))
            for i in range(start, end + 1):
                results.add(i)
        else:
            results.add(int(index))
    results = sorted(list(results))
    return results
