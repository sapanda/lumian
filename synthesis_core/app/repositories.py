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
