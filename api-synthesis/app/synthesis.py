import copy
import json
import logging
from typing import List
from .domains import (
    SynthesisResult,
    SynthesisResultOutput,
    EmbedsResult,
    MetadataResult
)
from .interfaces import (
    OpenAIClientInterface, EmbedsClientInterface, SynthesisInterface
)
from .prompts import (
    METADATA_PROMPT_TEMPLATE,
    METADATA_SCHEMA,
    SUMMARY_CHUNK_PROMPT_TEMPLATE,
    SUMMARY_PROMPT_TEMPLATE,
    CONCISE_PROMPT_TEMPLATE,
    QUERY_MESSAGE_TEMPLATE,
)
from .utils import (
    token_count,
    split_indexed_lines_into_chunks,
    split_indexed_transcript_lines_into_chunks,
    split_and_extract_indices
)


logger = logging.getLogger(__name__)


# TODO: Split into separate components for Summary, Concise and Embeds
class Synthesis(SynthesisInterface):

    def __init__(self,
                 openai_client: OpenAIClientInterface,
                 embeds_client: EmbedsClientInterface,
                 ** kwargs):
        self.openai_client = openai_client
        self.embeds_client = embeds_client
        self.__dict__.update(kwargs)

    def _get_empty_transcript_metadata(self):
        return {
            "title": "",
            "interviewer_names": [],
            "interviewee_names": [],
        }

    def metadata_transcript(
            self, indexed_transcript: str
    ) -> MetadataResult:
        """
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
        """
        cost = 0

        try:
            chunks = split_indexed_lines_into_chunks(
                indexed_transcript, self.chunk_min_tokens_summary)

            base_prompt = METADATA_PROMPT_TEMPLATE.format(
                schema=METADATA_SCHEMA, summaries="")

            results = []
            message = ""
            input_tokens = token_count(base_prompt)
            for chunk in chunks:
                chunk_str = "\n".join(chunk)
                result = self._openai_summarize_chunk(chunk_str)
                summary = split_and_extract_indices(result["output"])
                summary_text = "".join([f"{summary[i]['text']}"
                                        for i in range(len(summary))])
                cost += result["cost"]
                input_tokens += token_count(summary_text)

                if input_tokens < self.max_input_tokens_metadata:
                    results.append(summary_text)
                else:
                    break

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

    def _openai_transcript_metadata(self, summary_list: List[str]) -> dict:
        """
            Generate metadata for meeting transcript.
            Metadata : title, interviewees, interviewers
        """
        summaries = "\n* ".join(summary_list)
        prompt = METADATA_PROMPT_TEMPLATE.format(schema=METADATA_SCHEMA,
                                                 summaries=summaries.strip())
        return self.openai_client.execute_completion(prompt)

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
            indexed_transcript, interviewee, self.chunk_min_tokens_summary)
        results = []
        cost = 0
        for chunk in chunks:
            chunk_str = "\n".join(chunk)
            result = self._openai_summarize_chunk(chunk_str)
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
        chunks = split_indexed_lines_into_chunks(
            text, self.chunk_min_tokens_summary)
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

    def _openai_summarize_chunk(self, text: str) -> dict:
        """Generate a summary for a chunk of the transcript."""
        prompt = SUMMARY_CHUNK_PROMPT_TEMPLATE.format(text=text.strip())
        return self.openai_client.execute_completion(prompt)

    def _openai_summarize_full(self, text: str) -> dict:
        """Generate a summary from a combined transcript summary."""
        prompt = SUMMARY_PROMPT_TEMPLATE.format(text=text.strip())
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
            indexed_transcript, interviewee, self.chunk_min_tokens_concise)
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

    def _openai_concise_chunk(self, text: str) -> dict:
        """Generate a concise transcript for a chunk of the transcript."""
        prompt = CONCISE_PROMPT_TEMPLATE.format(text=text.strip())
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
            indexed_transcript, interviewee, self.chunk_min_tokens_query)

        content_list = []
        for chunk in chunks:
            content_list.append('\n'.join(chunk))

        return self._openai_embed_and_upsert(
            transcript_id, transcript_title, content_list
        )

    def _openai_embed_and_upsert(self,
                                 transcript_id: int,
                                 transcript_title: str,
                                 content_list: List[str]) -> dict:
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
                                   content_list: List[str],
                                   max_length: int
                                   ) -> List[List[str]]:
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
            self, transcript_id: int, query: str) -> SynthesisResult:
        """Run query against the transcript"""
        embed_result = self.openai_client.execute_embeds(query)
        search_results = self.embeds_client.search(
            transcript_id, embed_result['embedding']
        )
        query_results = self._openai_query(query, search_results)

        query_output = query_results["output"]
        sentences_and_indices = split_and_extract_indices(query_output)
        cost = embed_result["cost"] + query_results["cost"]
        results: SynthesisResult = {
            "output": sentences_and_indices,
            "prompt": query_results["prompt"],
            "cost": cost
        }
        return results

    def _openai_query(self, query: str, search_results: dict) -> dict:
        """Run a query against chosen sections of a transcript."""
        base_prompt = "".join(message["content"]
                              for message in QUERY_MESSAGE_TEMPLATE)
        total_tokens = token_count(base_prompt)
        total_tokens += token_count(query.strip())

        # Build the context string, but ensure OpenAI Completion
        # input token count doesn't exceed self.max_input_tokens_query
        context = ""
        separator = "-" * 4
        for match in search_results['matches']:
            section = match['metadata']['text']
            total_tokens += token_count(section)
            if total_tokens < self.max_input_tokens_query:
                context = f"{context}\n{separator}\n{section.strip()}"
        context = f"{context}\n{separator}"

        messages = copy.deepcopy(QUERY_MESSAGE_TEMPLATE)
        messages[-1]["content"] = messages[-1]["content"].format(
            query=query.strip(),
            context=context)

        return self.openai_client.execute_chat(messages)
