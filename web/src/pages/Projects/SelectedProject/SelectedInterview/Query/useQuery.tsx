import { useRef, useState, useEffect, useCallback } from "react";

export default function useQuery(interviewTranscipt: string) {
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

      let transcript = originalTranscriptRef.current;

      // merge ranges that are adjacent and have a difference of 100 or less
      ranges.sort((a, b) => a[0] - b[0]);
      const mergedRanges: [number, number][] = [];
      let currentRange = ranges[0];

      for (let i = 1; i < ranges.length; i++) {
        const nextRange = ranges[i];

        if (nextRange[0] - currentRange[1] <= 100) {
          currentRange[1] = nextRange[1];
        } else {
          mergedRanges.push(currentRange);
          currentRange = nextRange;
        }
      }

      mergedRanges.push(currentRange);
      console.log({ ranges, mergedRanges });
      // set the citations count
      setCitationsCount(mergedRanges.length);
      mergedRanges.forEach((range, index) => {
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

          console.log(transcript.includes(selectedText));
        }
      });

      setConversation(transcript);
    },
    []
  );

  useEffect(() => {
    originalTranscriptRef.current = interviewTranscipt;
    const _transcript = interviewTranscipt?.replaceAll('"\n\n', '"<br/> <br/>');
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
