class TranscriptUtils:

    def text_from_list(self,data):

        speaker_dict = {}
        for item in data:
            speaker = item["speaker"]
            text = ""
            for word in item["words"]:
                text += word["text"] + " "
            if speaker in speaker_dict:
                speaker_dict[speaker] += text
            else:
                speaker_dict[speaker] = text
            
        transcript = ""
        for speaker in speaker_dict.keys():
            transcript += f"{speaker} : " + speaker_dict.get(speaker) + "\n"
        
        return transcript