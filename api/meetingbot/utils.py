class TranscriptUtils:

    def generate_transcript_text(self,transcript_list):
        transcript = {}

        for response in transcript_list:
            speaker = response['speaker']

            for word in response['words']:
                start = word['start_timestamp']
                end = word['end_timestamp']

                text = word['text']

                if speaker in transcript:
                    transcript[speaker].append((start, end, text))
                else:
                    transcript[speaker] = [(start, end, text)]

        for speaker in transcript:
            transcript[speaker] = sorted(transcript[speaker], key=lambda x: x[0])

        transcript_str = ''
        for speaker in transcript:
            for i, word in enumerate(transcript[speaker]):
                if i == 0:
                    transcript_str += speaker + ' : '

                transcript_str += word[2]

                if i != len(transcript[speaker]) - 1:
                    transcript_str += ' '

            transcript_str += '\n'

        return transcript_str

    
transcript_utils = TranscriptUtils()