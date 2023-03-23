import re

# Engineering Params
LINE_MIN_SIZE = 90
CHUNK_MIN_WORDS = 500

def split_text_into_multiple_lines_for_speaker(text:str) -> list[tuple[str, int, int]]:
    paras = text.strip().split('\n\n')
    start_loc, results = 0, []
    for para in paras:
        speech_parts = para.split(': ', 1)
        speaker = speech_parts[0]
        speech_text_words = re.split('(\W)',speech_parts[1].strip('"'))
        start_loc += (len(speaker) + 3)
        temp_words, line_length = [], 0
        n = len(speech_text_words)
        for i in range(n):
            string = speech_text_words[i]
            temp_words.append(string)
            line_length += len(string)
            if (line_length >= LINE_MIN_SIZE and temp_words[-1] in ['.', '?', '!']) or i == n-1:
                sentence = (''.join(temp_words)).strip()
                if len(sentence):
                    results.append((f"{speaker}: {''.join(temp_words)}", start_loc, start_loc + line_length))
                start_loc += line_length
                temp_words, line_length = [], 0
        start_loc += 3
    return results

def split_indexed_lines_into_chunks(text: str) -> list[list[str]]:
    results, cur_results, lines, chunk_size = [], [], text.split('\n'), 0
    n = len(lines)
    for i in range(n):
        line = lines[i]
        cur_results.append(line)
        chunk_size += len(line.split())
        if chunk_size > CHUNK_MIN_WORDS or i == n-1:
            results.append(cur_results)
            cur_results, chunk_size = [], 0
    return results

def split_indexed_transcript_lines_into_chunks(text: str, interviewee: str) -> list[list[str]]:
    results, cur_results, lines, chunk_size = [], [], text.split('\n'), 0
    n = len(lines)
    for i in range(n):
        line = lines[i]
        cur_results.append(line)
        words = line.split()
        chunk_size += len(words)
        if i == n-1 or (chunk_size > CHUNK_MIN_WORDS and (lines[i+1].split(' ', 1))[1].startswith(interviewee)):
            results.append(cur_results)
            cur_results, chunk_size = [], 0
    return results

def split_and_extract_indices(input_string: str):
    pattern = re.compile(r'(.+?)\s*\(([\d\s,-]+)\)')
    matches = pattern.findall(input_string)
    return [(match[0], parse_indices(match[1])) for match in matches]

def parse_indices(input_string: str):
    pattern1 = re.compile(r'(\d+)-(\d+)')
    pattern2 = re.compile(r'(\d+)(,\s*\d+)*')
    if pattern1.match(input_string):
        start, end = tuple(map(int,pattern1.findall(input_string)[0]))
        return list(int(i) for i in range(start, end+1))
    elif pattern2.match(input_string):
        return list(map(int,input_string.split(',')))
    return None


if __name__ == '__main__':
    with open('./synthesis_core/transcript.txt', 'r') as f:
        text = f.read()

    results = split_text_into_multiple_lines_for_speaker(text=text)
    for item in results:
        print(item[0])
        print(f"--> {text[item[1]:item[2]+1]}")
    # print(results)
    # n = len(results)
    # new_text = '\n'.join([f"[{i}] {results[i][0]}" for i in range(n)])
    # # print(new_text)
    # print(split_indexed_transcript_lines_into_chunks(new_text, "Jason"))
    