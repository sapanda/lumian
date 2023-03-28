import psycopg2
import os
import time
from fastapi import FastAPI, Body, status
from fastapi.responses import Response
from app.usecases import (
    save_transcript, delete_transcript, get_transcript_summary)
from app.repositories import TranscriptRepository

retry_db_con = 0
while retry_db_con < 5:
    try:
        print("trying db connection")
        postgres_connection = psycopg2.connect(
            user=os.environ['SYNTHESIS_DB_USER'],
            password=os.environ['SYNTHESIS_DB_PASSWORD'],
            host=os.environ['SYNTHESIS_DB_HOST'],
            port=os.environ['SYNTHESIS_DB_PORT'],
            database=os.environ['SYNTHESIS_DB_NAME'])
        break
    except Exception as e:
        print(e)

        retry_db_con += 1
        time.sleep(2)

try:
    with postgres_connection:
        with postgres_connection.cursor() as conn:
            conn.execute(
                "select exists(select * from information_schema.tables where \
                    table_name=%s)", ('transcript_line',))
            if not conn.fetchone()[0]:
                conn.execute("""CREATE TABLE transcript_line(
                transcript_id int NOT NULL,
                line_no int NOT NULL,
                line_text TEXT NOT NULL,
                start_char_loc int NOT NULL,
                end_char_loc int NOT NULL,
                PRIMARY KEY(transcript_id, line_no)
                )""")
except psycopg2.errors.DuplicateTable as e:
    print(e)

app = FastAPI(
    title="Synthesis API",
    version="0.0.1"
)
repo = TranscriptRepository(conn=postgres_connection)


@app.post('/transcript/{transcript_id}')
def save_transcript_for_id(transcript_id: int, transcript: str = Body()):
    """API for saving a transcript"""
    save_transcript(transcript_id=transcript_id,
                    transcript=transcript, repo=repo)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put('/transcript/{transcript_id}')
def replace_transcript_for_id(transcript_id: int, transcript: str = Body()):
    """API for replacing a transcript"""
    delete_transcript(transcipt_id=transcript_id)
    save_transcript(transcript_id=transcript_id,
                    transcript=transcript, repo=repo)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.delete('/transcript/{transcript_id}')
def delete_transcript_for_id(transcript_id: int):
    """API for deleting a transcript"""
    delete_transcript(transcipt_id=transcript_id, repo=repo)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get('/transcript/{transcript_id}/summary')
def get_transcript_summary_for_id(transcript_id: int, interviewee: str):
    """API for getting a summary of a transcript"""
    results = get_transcript_summary(
        transcript_id=transcript_id, interviewee=interviewee, repo=repo)
    return results


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app=app, port=3001, log_level='info')
