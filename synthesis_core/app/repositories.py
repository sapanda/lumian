from psycopg2._psycopg import connection
from app.domians import TranscriptLine

class TranscriptRepository:
    def __init__(self, conn:connection):
        self.conn = conn
    
    def get_transcript(self, transcript_id: int) -> list[TranscriptLine]:
        with self.conn:
            with self.conn.cursor() as cur:
                cur.execute(f"select transcript_id, line_text, start_char_loc, end_char_loc, line_no from transcript_line \
                             where transcript_id = {transcript_id} order by line_no")
                results = cur.fetchall()
        return [TranscriptLine(
                    transcript_id=item[0], 
                    line_text=item[1],
                    start_char_loc=item[2],
                    end_char_loc=item[3],
                    line_no=item[4]) for item in results]
    
    def save_transcript(self, lines: list[TranscriptLine]):
        MAX_LINES = 100
        with self.conn:
            with self.conn.cursor() as cur:
                i, n = 0, len(lines)
                for i in range(0,n, MAX_LINES):
                    temp = [ (line.transcript_id, line.line_text, line.start_char_loc, line.end_char_loc, line.line_no)
                        for line in lines[i:min(i+MAX_LINES, n)]
                        ]
                    strs_format = ',\n'.join(f"(%s,%s,%s,%s,%s)" for _ in temp)
                    values = []
                    for item in temp:
                        values.extend(item)
                    statement = "Insert into transcript_line(transcript_id, line_text, start_char_loc, end_char_loc, line_no) \nvalues\n" + strs_format         
                    cur.execute(statement, values)

    def delete_transcript(self, transcript_id : int):
        with self.conn:
            with self.conn.cursor() as cur:
                cur.execute(f"Delete from transcript_line where transcript_id = {transcript_id}")

if __name__ == "__main__":
    import psycopg2, os

    postgres_connection = psycopg2.connect(user=os.environ['SYNTHESIS_DB_USER'],
                                    password=os.environ['SYNTHESIS_DB_PASSWORD'],
                                    host=os.environ['SYNTHESIS_DB_HOST'],
                                    port=os.environ['SYNTHESIS_DB_PORT'],
                                    database=os.environ['SYNTHESIS_DB_NAME'])
    
    tr = TranscriptRepository(conn=postgres_connection)
    # items = [
    #     TranscriptLine(transcript_id=0, line_text="aas", chunk_no=0, start_char_loc=0, end_char_loc=21, line_no=0),
    #     TranscriptLine(transcript_id=0, line_text="aas ddk", chunk_no=0, start_char_loc=22, end_char_loc=100, line_no=1),
    #     TranscriptLine(transcript_id=0, line_text="aas", chunk_no=0, start_char_loc=101, end_char_loc=151, line_no=2),
    #     TranscriptLine(transcript_id=0, line_text="aas ddk", chunk_no=0, start_char_loc=152, end_char_loc=201, line_no=3),
    #     TranscriptLine(transcript_id=0, line_text="aas", chunk_no=0, start_char_loc=202, end_char_loc=293, line_no=4),
    #     TranscriptLine(transcript_id=0, line_text="aas ddk", chunk_no=1, start_char_loc=294, end_char_loc=335, line_no=5),
    #     TranscriptLine(transcript_id=0, line_text="aas", chunk_no=1, start_char_loc=336, end_char_loc=394, line_no=6),
    #     TranscriptLine(transcript_id=0, line_text="aas ddk", chunk_no=1, start_char_loc=395, end_char_loc=460, line_no=7)
    #     ]
    # tlr.save_transcript(items)
    # tlr.delete_transcript(transcript_id=0)
    print(tr.get_line(transcript_id=0, line_no=1))
    
