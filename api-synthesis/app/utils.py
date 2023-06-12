import re
import tiktoken
from typing import List, Tuple


def token_count(input: str) -> int:
    token_encoding = tiktoken.get_encoding("cl100k_base")
    return len(token_encoding.encode(input))


def split_text_into_multiple_lines_for_speaker(
        text: str,
        line_min_size: int
) -> List[dict]:
    """
    Takes in a string `text` and splits it into multiple lines where each
    line is at least `LINE_MIN_SIZE` characters long and ends with a period
    (.),question mark (?) or exclamation mark (!). Each line starts with the
    name of the speaker.

    Example input:
        text: "Speaker A: This is a long piece of text that needs \
              to be split into multiple lines. Speaker B: Yes, I agree."
        line_min_size: 25

    Example output:
        [{
            "text": "Speaker A: This is a long piece of text that needs \
                to be split into multiple lines.",
            "start": 0,
            "end": 82
        },
        {
            "text": "Speaker B: Yes, I agree.",
            "start": 83,
            "end": 104
        }]
    """
    paras = [txt for txt in re.split(r"\r?\n+|\r+", text.strip()) if txt]
    start_loc, results = 0, []
    for para in paras:
        if len(para.split(": ")) > 1:
            speech_parts = para.split(": ", 1)
        speaker = speech_parts[0]
        speech_text_words = re.split(r"(\W)", speech_parts[1].strip('"'))
        start_loc += len(speaker)
        temp_words, line_length = [], 0
        n = len(speech_text_words)
        for i in range(n):
            string = speech_text_words[i]
            temp_words.append(string)
            line_length += len(string)
            if (
                line_length >= line_min_size and temp_words[-1] in
                    [".", "?", "!"]
            ) or i == n - 1:
                sentence = ("".join(temp_words)).strip()
                if len(sentence):
                    start_loc = text.find(sentence, start_loc)
                    results.append(
                        {
                            "text": f"{speaker}: {sentence}",
                            "start": start_loc,
                            "end": start_loc + len(sentence),
                        }
                    )
                start_loc += line_length
                temp_words, line_length = [], 0
    return results


def split_indexed_lines_into_chunks(
        text: str,
        chunk_min_tokens: int) -> List[List[str]]:
    """Split indexed lines into chunks"""
    results, cur_results, lines, chunk_size = [], [], text.split("\n"), 0
    n = len(lines)
    for i in range(n):
        line = lines[i]
        cur_results.append(line)
        chunk_size += token_count(line)
        if chunk_size > chunk_min_tokens or i == n - 1:
            results.append(cur_results)
            cur_results, chunk_size = [], 0
    return results


def split_indexed_transcript_lines_into_chunks(
    text: str, interviewee: str, chunk_min_tokens: int
) -> List[List[str]]:
    """Split indexed lines into chunks. No chunk (except the first) should
    start with 'interviewee' name"""
    interviewee = interviewee.lower()
    results, cur_results, lines, chunk_size = [], [], text.split("\n"), 0
    n = len(lines)
    for i in range(n):
        line = lines[i]
        cur_results.append(line)
        chunk_size += token_count(line)
        if i == n - 1 or (
            chunk_size > chunk_min_tokens
            and not (lines[i + 1].split(" ", 1))[1].
                lower().startswith(interviewee)
        ):
            results.append(cur_results)
            cur_results, chunk_size = [], 0
    return results


def split_and_extract_indices(
        input_string: str
) -> List[Tuple[str, List[int]]]:
    """Split the lines into sentences and extract indices
    from parenthesis mentioned at the end of indices
    input_string: "Some text (2-3), some more text (10,13).
                   Some more new text (1,4-5,15). And more."
    output: [{'text': "Some text", 'references': [2,3]},
             {'text': ", some more text", 'references': [10, 11, 12, 13]},
             {'text': ". Some more new text", 'references': [1, 4, 5, 15]},
             {'text': ". And more", 'references': []}]
    """
    pattern = re.compile(r"(.+?)\s*\(([\d\s,-]+)\)|(.+)")
    matches = pattern.findall(input_string)
    results = []
    for match in matches:
        if match[0]:
            results.append({'text': match[0],
                            'references': _parse_indices(match[1])})
        elif match[2]:
            results.append({'text': match[2],
                            'references': []})
    return results


def _parse_indices(input_string: str) -> List[int]:
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
