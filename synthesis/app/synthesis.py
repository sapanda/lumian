import json
from .domains import SynthesisResult, SynthesisResultOutput
from .interfaces import OpenAIClientInterface, SynthesisInterface
from .utils import (
    split_indexed_lines_into_chunks,
    split_indexed_transcript_lines_into_chunks,
    split_and_extract_indices,
)


class Synthesis(SynthesisInterface):

    EG_SUMMARY = 'eg-summary.json'
    EG_CONCISE = 'eg-concise.json'

    def __init__(self,
                 openai_client: OpenAIClientInterface,
                 max_summary_size: int,
                 chunk_min_words: int,
                 examples_dir: str):
        self.openai_client = openai_client
        self.max_summary_size = max_summary_size
        self.chunk_min_words = chunk_min_words
        self.examples_dir = examples_dir

    def summarize_transcript(
            self, text: str, interviewee: str
    ) -> SynthesisResult:
        """
        Summarize an indexed transcript and return reference indices
        for phrases and sentences in the final summary

        Output Example:
            [{"text": "The quick brown fox jumps", "references": [(16, 19)]},
             {"text": "over the lazy dog", "references": [(4, 9), (14)]}]
        """
        chunks = split_indexed_transcript_lines_into_chunks(
            text, interviewee, self.chunk_min_words)
        results = []
        cost = 0
        for chunk in chunks:
            result = self._openai_summarize_chunk(chunk, interviewee)
            summary = result["output"]
            cost += result["cost"]
            summary_sentences_and_indices = split_and_extract_indices(summary)
            results.extend(summary_sentences_and_indices)
        n = len(results)
        text = "\n".join([f"[{i}] {results[i]['text']}" for i in range(n)])
        temp_result = self._summarize_text(text)
        summary_results, summary_cost = temp_result['output'],\
            temp_result['cost']
        cost += summary_cost
        final_results: list[SynthesisResultOutput] = []
        for i in range(len(summary_results)):
            item = summary_results[i]
            temp = set()
            for num in item['references']:
                temp.update(results[num]['references'])
            final_results.append({
                'text': item['text'],
                'references': list(temp)})
        data: SynthesisResult = {"output": final_results, "cost": cost}
        return data

    def _summarize_text(
        self, text: str
    ) -> SynthesisResult:
        """Summarize indexed notes and return reference indices
        for phrases and sentences in the final summary"""
        chunks = split_indexed_lines_into_chunks(text, self.chunk_min_words)
        results = []
        cost = 0
        for chunk in chunks:
            result = self._openai_summarize_full(chunk)
            summary = result["output"]
            cost += result["cost"]
            summary_sentences_and_indices = split_and_extract_indices(summary)
            results.extend(summary_sentences_and_indices)
        n = len(results)
        word_count = 0
        for item in results:
            word_count += len(item['text'].split())
        # Todo: figure out cutoff logic for recursion
        if word_count <= self.max_summary_size:
            return {"output": results, "cost": cost}

        text = "\n".join([f"[{i}] {results[i]['text']}" for i in range(n)])
        temp_result = self._summarize_text(text)
        summary_results, summary_cost = temp_result['output'],\
            temp_result['cost']
        cost += summary_cost
        final_results: list[SynthesisResultOutput] = []
        for i in range(len(summary_results)):
            item = summary_results[i]
            temp = set()
            for num in item['references']:
                temp.update(results[num]['references'])
            final_results.append({
                'text': item['text'],
                'references': list(temp)
            })
        data: SynthesisResult = {"output": final_results, "cost": cost}
        return data

    def _create_openai_prompt_summarize_chunk(
        self,
        text: str,
        interviewee: str = None,
    ) -> dict:
        """Create prompt to generate a summary for a chunk of the
          transcript."""
        if interviewee is not None:
            prompt_detail = "summary of only {interviewee}'s comments"
        else:
            prompt_detail = "summary"
        header = (
            f"The following is a section of an interview transcript. "
            f"Please provide a {prompt_detail}. "
        )
        return self._create_openai_prompt_reverse_lookup(text, header,
                                                         self.EG_SUMMARY)

    def _create_openai_prompt_summarize_full(self, text: str) -> dict:
        """Create prompt to generate a summary from a combined
        transcript summary."""
        header = (
            "Write a detailed synopsis based on the following notes."
            "Each sentence should be short and contain only one piece of data."
        )
        return self._create_openai_prompt_reverse_lookup(text, header,
                                                         self.EG_SUMMARY)

    def _openai_summarize_with_prompt_header(
        self,
        text: str,
        prompt_header: str = None,
    ) -> dict:
        """Generate a summary for a chunk of the transcript."""
        prompt = self._create_openai_prompt_reverse_lookup(text, prompt_header,
                                                           self.EG_SUMMARY)
        return self.openai_client.execute_completion(prompt)

    def _openai_summarize_chunk(
        self,
        text: str,
        interviewee: str = None,
    ) -> dict:
        """Generate a summary for a chunk of the transcript."""
        prompt = self._create_openai_prompt_summarize_chunk(text, interviewee)
        return self.openai_client.execute_completion(prompt)

    def _openai_summarize_full(
            self,
            text: str) -> dict:
        """Generate a summary from a combined transcript summary."""
        prompt = self._create_openai_prompt_summarize_full(text)
        return self.openai_client.execute_completion(prompt)

    def concise_transcript(
            self, text: str, interviewee: str
    ) -> SynthesisResult:
        """
        Convert transcript to concise version and return reference indices
        for phrases and sentences in the concise version

        Output Example:
            [{"text": "Andy: Life is good.", "references": [(16, 19)]},
             {"text": "John: It sure is!", "references": [(4, 9), (14)]}]
        """
        chunks = split_indexed_transcript_lines_into_chunks(
            text, interviewee, self.chunk_min_words)
        results = []
        cost = 0
        for chunk in chunks:
            result = self._openai_concise_chunk(chunk)
            concise = result["output"]
            cost += result["cost"]
            sentences_and_indices = split_and_extract_indices(concise)
            results.extend(sentences_and_indices)
        data: SynthesisResult = {"output": results, "cost": cost}
        return data

    def _create_openai_prompt_concise_chunk(self, text: str) -> dict:
        """Create prompt to generate a concise transcript from a chunk."""
        header = (
            "The following is a section of an interview transcript. "
            "Please clean it up but still in dialogue form. The speaker "
            "name should always be preserved. Do not add any details "
            "not present in the original transcript. "
        )
        return self._create_openai_prompt_reverse_lookup(text, header,
                                                         self.EG_CONCISE)

    def _openai_concise_chunk(self, text: str) -> dict:
        """Generate a concise transcript for a chunk of the transcript."""
        prompt = self._create_openai_prompt_concise_chunk(text)
        return self.openai_client.execute_completion(prompt)

    def _create_openai_prompt_reverse_lookup(
        self,
        text: str,
        prompt_header: str = None,
        example_filename: str = None,
    ) -> dict:
        """Create the prompt for the OpenAI API request."""

        prompt = (
            f"{prompt_header} For each phrase in the output, "
            f"also specify in parenthesis the exact index of where that "
            f"information comes from in the source. When listing indexes "
            f"in parentheses, mention all the locations the info is "
            f"mentioned, even if repeated. Only answer truthfully "
            f"and don't include anything not in the original input: "
        )

        with open(f'{self.examples_dir}/{example_filename}', "r") as f:
            examples = json.load(f)

        # Add examples to the prompt
        index = 1
        for example in examples:
            input_text = f"INPUT {index}: ###\n{example['input']}\n###\n"
            output_text = f"OUTPUT {index}: ###\n{example['output']}\n###\n"
            prompt = f"{prompt}\n\n{input_text}\n{output_text}"
            index += 1

        prompt = (
            f"{prompt}\nINPUT {index}: ###\n{text}\n###\n"
            f"OUTPUT {index}:###\n\n###"
        )

        return prompt
