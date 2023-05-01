def generate_transcript_text(self, transcript):

    output = []
    for speaker_turn in transcript:
        speaker_name = speaker_turn['speaker']
        speaker_words = [word['text'] for word in speaker_turn['words']]
        speaker_turn_text = ' '.join(speaker_words)
        output.append(f'{speaker_name}: "{speaker_turn_text}"')
    return '\n\n'.join(output)
