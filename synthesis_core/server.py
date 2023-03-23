import psycopg2, os
from fastapi import FastAPI, Body, status
from fastapi.responses import Response
from usecases import save_transcript, delete_transcript, get_transcript_summary

postgres_connection = psycopg2.connect(user=os.environ['SYNTHESIS_DB_USER'],
                                  password=os.environ['SYNTHESIS_DB_PASSWORD'],
                                  host=os.environ['SYNTHESIS_DB_HOST'],
                                  port=os.environ['SYNTHESIS_DB_PORT'],
                                  database=os.environ['SYNTHESIS_DB_NAME'])

app = FastAPI()

@app.post('/transcript/{transcript_id}')
def save_transcript_for_id(transcript_id: int, transcript: str = Body()):
    save_transcript(transcript_id=transcript_id, transcript=transcript)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put('/transcript/{transcript_id}')
def save_transcript_for_id(transcript_id: int, transcript: str = Body()):
    delete_transcript(transcipt_id=transcript_id)
    save_transcript(transcript_id=transcript_id, transcript=transcript)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.delete('/transcript/{transcript_id}')
def delete_transcript_for_id(transcript_id: int):
    delete_transcript(transcipt_id=transcript_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.get('/transcript/{transcript_id}/summary')
def get_transcript_summary_for_id(transcript_id: int, interviewee: str):
    results = get_transcript_summary(transcript_id=transcript_id, interviewee=interviewee)
    return results

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app=app, port=3000, log_level='info')
