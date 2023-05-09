import { useRef, useState, useEffect, useCallback } from "react";

export default function useConcise(interviewTranscipt: string) {
  const originalTranscriptRef = useRef<string>("");
  const transcriptRef = useRef<HTMLDivElement>(null);

  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);
  const [conversation, setConversation] = useState<string>("");
  const [citationsCount, setCitationsCount] = useState<number>(0);
  const [activeCitationIndex, setActiveCitationIndex] = useState<number>(0);

  function scrollToNextHighlightedText(index: number) {
    const nextHightlightedText = transcriptRef.current?.querySelector(
      `#highlight${index}`
    );

    if (nextHightlightedText) {
      nextHightlightedText.scrollIntoView();
      setActiveCitationIndex(index + 1);
    }
  }

  const handleSummaryItemClick = useCallback(
    (ranges: [number, number][], index: number) => {
      setSelectedIndex(index);
      setCitationsCount(ranges.length);
      setActiveCitationIndex(0);
      console.log(ranges);
      let transcript = originalTranscriptRef.current;

      ranges.forEach((range, index) => {
        const [start, end] = range;
        const selectedText = originalTranscriptRef?.current?.slice(start, end);

        if (transcript && selectedText) {
          transcript = transcript
            ?.replace(
              selectedText,
              `<span style="background-color:#dbeafe;"id="highlight${index}"
            >${selectedText}</span>
            `
            )
            ?.replaceAll('"\n\n', '"<br/> <br/>');
        }
      });

      setConversation(transcript);
    },
    []
  );

  useEffect(() => {
    originalTranscriptRef.current = interviewTranscipt;
    const _transcript = interviewTranscipt.replaceAll('"\n\n', '"<br/> <br/>');
    setConversation(_transcript);
  }, [interviewTranscipt]);

  useEffect(() => {
    scrollToNextHighlightedText(0);
  }, [conversation]);
  return {
    conversation,
    handleSummaryItemClick,
    transcriptRef,
    scrollToNextHighlightedText,
    selectedIndex,
    citationsCount,
    activeCitationIndex,
  };
}
