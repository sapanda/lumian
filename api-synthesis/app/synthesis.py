import json
import logging
from .domains import (
    SynthesisResult,
    SynthesisResultOutput,
    EmbedsResult,
    MetadataResult
)
from .interfaces import (
    OpenAIClientInterface, EmbedsClientInterface, SynthesisInterface
)
from .utils import (
    split_indexed_lines_into_chunks,
    split_indexed_transcript_lines_into_chunks,
    split_and_extract_indices
)


logger = logging.getLogger(__name__)


# TODO: Split into separate components for Summary, Concise and Embeds
class Synthesis(SynthesisInterface):

    EG_SUMMARY = 'eg-summary.json'
    EG_CONCISE = 'eg-concise.json'
    EG_QUERY = 'eg-query.json'

    def __init__(self,
                 openai_client: OpenAIClientInterface,
                 embeds_client: EmbedsClientInterface,
                 chunk_min_words: int,
                 context_max_chars: int,
                 examples_dir: str):
        self.openai_client = openai_client
        self.embeds_client = embeds_client
        self.chunk_min_words = chunk_min_words
        self.context_max_chars = context_max_chars
        self.examples_dir = examples_dir

    def _get_empty_transcript_metadata(self):
        return {
            "title": "",
            "interviewer_names": [],
            "interviewee_names": [],
        }

    def metadata_transcript(
            self, indexed_transcript: str
    ) -> MetadataResult:
        '''
            Return metadata for transcript
            Example transcript :
                The interviewee, Sean, had some technical difficulties
                accessing the Zoom call but eventually joined.
                The interviewers, Saswat and Wilbert, are working on a startup
            Output : {
                        'title': "Sean's Retirement Savings Interview",
                        'interviewer_names': ['Saswat', 'Wilbert'],
                        'interviewee_names': ['Sean']
                    }
        '''
        cost = 0

        try:
            chunks = split_indexed_lines_into_chunks(
                indexed_transcript, self.chunk_min_words)
            results = []
            message = ""
            context_char = 0
            for chunk in chunks:
                result = self._openai_summarize_chunk(chunk)
                summary = split_and_extract_indices(result["output"])
                summary_text = "".join([f"{summary[i]['text']}"
                                        for i in range(len(summary))])
                if (context_char + len(summary_text) < self.context_max_chars):
                    context_char += len(summary_text)
                    cost += result["cost"]
                    results.append(summary_text)

            response = self._openai_transcript_metadata(results)
            cost += response["cost"]
            transcript_metadata = json.loads(response["output"])
        except json.decoder.JSONDecodeError as e:
            logger.exception("JSONDecodeError when generating metadata",
                             exc_info=e)
            transcript_metadata = self._get_empty_transcript_metadata()
            message = str(e)
        except Exception as e:
            logger.exception("Exception when generating metadata", exc_info=e)
            transcript_metadata = self._get_empty_transcript_metadata()
            message = str(e)

        data: MetadataResult = {
                "title": transcript_metadata["title"],
                "interviewees": transcript_metadata["interviewee_names"],
                "interviewers": transcript_metadata["interviewer_names"],
                "cost": cost,
                "message": message
            }
        return data

    def _openai_transcript_metadata(
        self,
        summary_list: 'list[str]'
    ) -> dict:
        '''
            Generate metadata for meeting transcript.
            Metadata : title, interviewees, interviewers
        '''
        prompt = self._create_openai_prompt_transcript_metadata(summary_list)
        return self.openai_client.execute_completion(prompt)

    def _create_openai_prompt_transcript_metadata(
            self,
            summary_list: 'list[str]'
    ) -> dict:
        '''
            Create prompt to generate metadata for the summary
        '''

        header = (
            "The following are summaries of various sections "
            "of an interview. Please fill out the Interview Title, "
            "Interviewee Names and Interviewer Names. Title should "
            "contain the Interviewee Name. Use a Json Format: "
            )

        format_dict = {
            "title": "",
            "interviewer_names": [""],
            "interviewee_names": [""],
        }

        summaries = "\n* ".join(summary_list)
        format_json = json.dumps(format_dict)
        prompt = (
            f"{header}\n\nOutput Format: ###\n{format_json}\n###"
            f"\n\nSummaries: ###\n* {summaries}\n###\n"
            )

        return prompt

    def summarize_transcript(
            self, indexed_transcript: str, interviewee: str
    ) -> SynthesisResult:
        """
        Summarize an indexed transcript and return reference indices
        for phrases and sentences in the final summary

        Output Example:
            [{"text": "The quick brown fox jumps", "references": [(16, 19)]},
             {"text": "over the lazy dog", "references": [(4, 9), (14)]}]
        """
        chunks = split_indexed_transcript_lines_into_chunks(
            indexed_transcript, interviewee, self.chunk_min_words)
        results = []
        cost = 0
        for chunk in chunks:
            result = self._openai_summarize_chunk(chunk, interviewee)
            summary = result["output"]
            cost += result["cost"]
            summary_sentences_and_indices = split_and_extract_indices(summary)
            results.extend(summary_sentences_and_indices)
        n = len(results)
        indexed_transcript = "\n".join([f"[{i}] {results[i]['text']}"
                                        for i in range(n)])
        temp_result = self._summarize_text(indexed_transcript)
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
        data: SynthesisResult = {
            "output": final_results,
            "prompt": temp_result["prompt"],
            "cost": cost
        }
        return data

    def _summarize_text(
        self, text: str
    ) -> SynthesisResult:
        """Summarize indexed notes and return reference indices
        for phrases and sentences in the final summary"""
        chunks = split_indexed_lines_into_chunks(text, self.chunk_min_words)
        last_prompt = ""
        results = []
        cost = 0
        for chunk in chunks:
            result = self._openai_summarize_full("\n".join(chunk))
            summary = result["output"]
            cost += result["cost"]
            last_prompt = result["prompt"]
            summary_sentences_and_indices = split_and_extract_indices(summary)
            results.extend(summary_sentences_and_indices)
        n = len(results)
        word_count = 0
        for item in results:
            word_count += len(item['text'].split())

        if len(chunks) == 1:
            # If we've only had to summarize a single chunk, we're done
            data: SynthesisResult = {
                "output": results,
                "prompt": last_prompt,
                "cost": cost
            }
        else:
            # Solve recursively
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
            data: SynthesisResult = {
                "output": final_results,
                "prompt": temp_result['prompt'],
                "cost": cost
            }
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
        return self._create_openai_prompt_citations(text, header,
                                                    self.EG_SUMMARY)

    def _create_openai_prompt_summarize_full(self, text: str) -> dict:
        """Create prompt to generate a summary from a combined
        transcript summary."""
        header = (
            "Write a detailed synopsis based on the following notes."
            "Each sentence should be short and contain only one piece of data."
        )
        return self._create_openai_prompt_citations(text, header,
                                                    self.EG_SUMMARY)

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
            self, indexed_transcript: str, interviewee: str
    ) -> SynthesisResult:
        """
        Convert transcript to concise version and return reference indices
        for phrases and sentences in the concise version

        Output Example:
            [{"text": "Andy: Life is good.", "references": [(16, 19)]},
             {"text": "John: It sure is!", "references": [(4, 9), (14)]}]
        """
        chunks = split_indexed_transcript_lines_into_chunks(
            indexed_transcript, interviewee, self.chunk_min_words)
        results = []
        prompts = []
        cost = 0
        for chunk in chunks:
            result = self._openai_concise_chunk("\n".join(chunk))
            concise = result["output"]
            cost += result["cost"]
            prompts.append(result["prompt"])
            sentences_and_indices = split_and_extract_indices(concise)
            results.extend(sentences_and_indices)

        separator = f"\n\n{'-' * 50}\n\n"
        data: SynthesisResult = {
            "output": results,
            "prompt": separator.join(prompts),
            "cost": cost
        }
        return data

    def _create_openai_prompt_concise_chunk(self, text: str) -> dict:
        """Create prompt to generate a concise transcript from a chunk."""
        header = (
            "The following is a section of an interview transcript. "
            "Please clean it up but still in dialogue form. The speaker "
            "name should always be preserved. Do not add any details "
            "not present in the original transcript. "
        )
        return self._create_openai_prompt_citations(text, header,
                                                    self.EG_CONCISE)

    def _openai_concise_chunk(self, text: str) -> dict:
        """Generate a concise transcript for a chunk of the transcript."""
        prompt = self._create_openai_prompt_concise_chunk(text)
        return self.openai_client.execute_completion(prompt)

    def embed_transcript(
            self,
            transcript_id: int,
            transcript_title: str,
            indexed_transcript: str,
            interviewee: str
    ) -> EmbedsResult:
        """Generate embeds for the transcript"""
        chunks = split_indexed_transcript_lines_into_chunks(
            indexed_transcript, interviewee, self.chunk_min_words)

        content_list = []
        for chunk in chunks:
            content_list.append('\n'.join(chunk))

        return self._openai_embed_and_upsert(
            transcript_id, transcript_title, content_list
        )

    def _openai_embed_and_upsert(self,
                                 transcript_id: int,
                                 transcript_title: str,
                                 content_list: 'list[str]') -> dict:
        """Generate embeds for the input strings using Open AI."""

        # TODO: OpenAI only allows max 8192 tokens per API call
        # For now we'll limit to 20000 characters per API call
        # But in the future use tiktoken to get exact token count
        MAX_CHAR_LENGTH = 20000

        batches = self._create_batches_for_embeds(
            content_list, MAX_CHAR_LENGTH
        )
        start_index = 0
        cost = 0
        for batch in batches:
            result = self.openai_client.execute_embeds_batch(
                request_list=batch,
                object_id=transcript_id,
                object_desc=transcript_title,
                start_index=start_index
            )
            upsert_list = result['upsert_list']
            cost += result['cost']
            start_index += len(batch)

            self.embeds_client.upsert(vectors=upsert_list)

        return {'cost': cost}

    def _create_batches_for_embeds(self,
                                   content_list: 'list[str]',
                                   max_length: int
                                   ) -> 'list[list[str]]':
        """
        Split the content_list into batches of the appropriate
        size for sending to the OpenAI Embeddings API.
        """
        batches = []
        request_list = []
        request_length = 0
        for content in content_list:

            # TODO: This assumes no 'content' string is longer than
            # max_length. Chunking algorithm needs to factor this limit in
            if len(content) + request_length > max_length:
                batches.append(request_list)
                request_list = []
                request_length = 0

            request_list.append(content)
            request_length += len(content)

        if request_list:
            batches.append(request_list)

        return batches

    def query_transcript(
            self,
            transcript_id: int,
            query: str
    ) -> SynthesisResult:
        """Run query against the transcript"""
        embed_result = self.openai_client.execute_embeds(query)
        search_results = self.embeds_client.search(
            transcript_id, embed_result['embedding']
        )
        chosen_sections = self._context_from_search_results(search_results)
        query_results = self._openai_query(query, chosen_sections)

        query_output = query_results["output"]
        sentences_and_indices = split_and_extract_indices(query_output)
        cost = embed_result["cost"] + query_results["cost"]
        results: SynthesisResult = {
            "output": sentences_and_indices,
            "prompt": query_results["prompt"],
            "cost": cost
        }
        return results

    def _context_from_search_results(self, search_results: dict
                                     ) -> 'list[str]':
        """
        Parse the search_results and return a context string
        list with total length under max_char_length
        """
        chosen_sections = []
        total_length = 0
        for match in search_results['matches']:
            item = match['metadata']['text']
            # TODO: Verify chunks are not larger than cutoff
            if total_length + len(item) > self.context_max_chars:
                break

            chosen_sections.append(item)
            total_length += len(item)

        return chosen_sections

    def _create_openai_prompt_query(
            self, query: str, chosen_sections: 'list[str]'
            ) -> dict:
        """Create prompt to generate a query result."""

        prompt_header = ('Answer the query using the provided context, '
                         'which consists of excerpts from interviews. ')

        text = f'{query}\n###\nCONTEXT:\n'
        for section in chosen_sections:
            section = section.replace('\n\n', '\n')
            text = f'{text}{section}'

        return self._create_openai_prompt_citations(
            text, prompt_header, self.EG_QUERY
        )

    def _openai_query(
            self, query: str, chosen_sections: 'list[str]'
            ) -> dict:
        """Run a query against chosen sections of a transcript."""
        prompt = self._create_openai_prompt_query(query, chosen_sections)
        return self.openai_client.execute_completion(prompt)

    def _create_openai_prompt_citations(
        self,
        text: str,
        prompt_header: str = None,
        example_filename: str = None,
        max_examples: int = 1,
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
            prompt = f"{prompt}\n\n{input_text}{output_text}"
            index += 1

            if index > max_examples:
                break

        prompt = (
            f"{prompt}\nINPUT {index}: ###\n{text}\n###\n"
            f"OUTPUT {index}:###\n\n###"
        )

        return prompt
