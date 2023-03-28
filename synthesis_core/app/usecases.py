from app.domians import TranscriptLine
from app.repositories import TranscriptRepository
from app.utils import split_text_into_multiple_lines_for_speaker
from app.core import summarize_transcript


def save_transcript(
        transcript_id: int,
        transcript: str,
        repo: TranscriptRepository):
    results = []
    lines = split_text_into_multiple_lines_for_speaker(transcript)
    for i in range(len(lines)):
        line = lines[i]
        results.append(TranscriptLine(
            transcript_id=transcript_id,
            line_text=line[0],
            start_char_loc=line[1],
            end_char_loc=line[2],
            line_no=i
        ))

    repo.save_transcript(lines=results)


def delete_transcript(transcipt_id: int, repo: TranscriptRepository):
    repo.delete_transcript(transcript_id=transcipt_id)


def get_transcript_summary(
        transcript_id: int,
        interviewee: str,
        repo: TranscriptRepository
) -> dict:
    lines = repo.get_transcript(transcript_id=transcript_id)
    mapping, sentence_list = {}, []
    for i in range(len(lines)):
        line = lines[i]
        mapping[i] = (line.start_char_loc, line.end_char_loc)
        sentence_list.append(f"[{line.line_no}] {line.line_text}")
    new_text = '\n'.join(sentence_list)
    results, cost = summarize_transcript(new_text, interviewee)
    final_results = []
    for item in results:
        final_results.append({"text": item[0], "references": []})
        for num in item[1]:
            i, j = mapping[num]
            final_results[-1]["references"].append([i, j])
    return {"output": final_results, "cost": cost}
