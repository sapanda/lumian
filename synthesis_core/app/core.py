from app.openai_wrapper import execute_openai_completion
from app.utils import (
    split_indexed_lines_into_chunks,
    split_indexed_transcript_lines_into_chunks,
    split_and_extract_indices,
)
import json


def summarize_transcript(
        text: str, interviewee: str
) -> tuple[list[tuple[str, list[int]]], float]:
    """Summarize an indexed transcript and return reference indices
    for phrases and sentences in the final summary"""
    chunks = split_indexed_transcript_lines_into_chunks(text, interviewee)
    results = []
    cost = 0
    for chunk in chunks:
        result = openai_summarize_chunk(chunk, interviewee)
        summary = result["output"]
        cost += result["cost"]
        summary_sentences_and_indices = split_and_extract_indices(summary)
        results.extend(summary_sentences_and_indices)
    n = len(results)
    mapping = {}
    for i in range(n):
        mapping[i] = results[i][1]

    text = "\n".join([f"[{i}] {results[i][0]}" for i in range(n)])
    summary_results, summary_cost = summarize_text(text)
    cost += summary_cost
    final_results = []
    for i in range(len(summary_results)):
        item = summary_results[i]
        temp = set()
        for num in item[1]:
            temp.update(mapping[num])
        final_results.append((item[0], list(temp)))
    return (final_results, cost)


def summarize_text(
    text: str, max_words: int = 400
) -> tuple[list[tuple[str, list[int]]], float]:
    """Summarize indexed notes and return reference indices
    for phrases and sentences in the final summary"""
    chunks = split_indexed_lines_into_chunks(text)
    results = []
    cost = 0
    for chunk in chunks:
        result = openai_summarize_full(chunk)
        summary = result["output"]
        cost += result["cost"]
        summary_sentences_and_indices = split_and_extract_indices(summary)
        results.extend(summary_sentences_and_indices)

    words_size = 0
    for item in results:
        words_size += len(item[0].split())

    # Todo: figure out cutoff logic for recursion
    if words_size < max_words:
        return results, cost

    n = len(results)
    mapping = {}
    for i in range(n):
        mapping[i] = results[i][1]

    text = "\n".join([f"[{i}] {results[i][0]}" for i in range(n)])
    summary_results, summary_cost = summarize_text(text)
    cost += summary_cost
    for i in len(summary_results):
        item = summary_results[i]
        temp = set()
        for num in item[1]:
            temp.update(mapping[num])
        item[1] = list(temp)
    return (summary_results, cost)


def create_openai_prompt_summarize(
    text: str,
    prompt_header: str = None,
) -> dict:
    """Create the prompt for the OpenAI API request."""

    prompt = (
        f"{prompt_header} For each phrase in the output, "
        f"also specify in parenthesis the exact index of where that "
        f"information comes from in the source. When listing indexes "
        f"in parentheses, mention all the locations the info is "
        f"mentioned, even if repeated. Only answer truthfully "
        f"and don't include anything not in the original transcript: "
    )

    with open("app/examples.json", "r") as f:
        examples = json.load(f)

    # Add examples to the prompt
    index = 1
    for example in examples:
        input_text = f"SOURCE {index}: ###\n{example['input']}\n###\n"
        output_text = f"SUMMARY {index}: ###\n{example['output']}\n###\n"
        prompt = f"{prompt}\n\n{input_text}\n{output_text}"
        index += 1

    prompt = (
        f"{prompt}\nSOURCE {index}: ###\n{text}\n###\n"
        f"SUMMARY {index}:###\n\n###"
    )

    return prompt


def create_openai_prompt_summarize_chunk(
    text: str,
    interviewee: str = None,
) -> dict:
    """Create prompt to generate a summary for a chunk of the transcript."""
    if interviewee is not None:
        prompt_detail = "summary of only {interviewee}'s comments"
    else:
        prompt_detail = "summary"
    header = (
        f"The following is a section of an interview transcript. "
        f"Please provide a {prompt_detail}. "
    )
    return create_openai_prompt_summarize(text, header)


def create_openai_prompt_summarize_full(text: str) -> dict:
    """Create prompt to generate a summary from a combined
    transcript summary."""
    header = (
        "Write a detailed synopsis based on the following notes. "
        "Each sentence should be short and contain only one piece of data. "
    )
    return create_openai_prompt_summarize(text, header)


def openai_summarize_with_prompt_header(
    text: str,
    prompt_header: str = None,
) -> dict:
    """Generate a summary for a chunk of the transcript."""
    prompt = create_openai_prompt_summarize(text, prompt_header)
    return execute_openai_completion(prompt)


def openai_summarize_chunk(
    text: str,
    interviewee: str = None,
) -> dict:
    """Generate a summary for a chunk of the transcript."""
    prompt = create_openai_prompt_summarize_chunk(text, interviewee)
    return execute_openai_completion(prompt)


def openai_summarize_full(text: str) -> dict:
    """Generate a summary from a combined transcript summary."""
    prompt = create_openai_prompt_summarize_full(text)
    return execute_openai_completion(prompt)