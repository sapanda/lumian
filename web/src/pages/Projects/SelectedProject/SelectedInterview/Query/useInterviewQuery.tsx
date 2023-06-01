import { useRef, useState, useEffect, useCallback } from "react";

import {
  baseApiUrl,
  interviewEndPoints,
} from "../../../../../api/apiEndpoints";
import { useParams } from "react-router-dom";
import { useGetMeetingQuery } from "../../../../../api/meetingApi";

export default function useInterviewQuery(interviewTranscipt: string) {
  const originalTranscriptRef = useRef<string>("");
  const transcriptRef = useRef<HTMLDivElement>(null);

  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);
  const [conversation, setConversation] = useState<string>("");
  const [citationsCount, setCitationsCount] = useState<number>(0);
  const [activeCitationIndex, setActiveCitationIndex] = useState<number>(0);

  const [userQueryText, setUserQueryText] = useState<string>("");
  const { interviewId } = useParams();

  const { data: query, refetch: updateQuery } = useGetMeetingQuery(
    parseInt(interviewId || "0")
  );
  const askQuery = async () => {
    const formData = new FormData();
    formData.append("query", userQueryText);

    const boundary = Math.random().toString().substr(2);

    const res = await fetch(
      baseApiUrl +
        interviewEndPoints.interviewQuery.replace(":interviewId", "1"),
      {
        method: "POST",
        headers: {
          "Content-Type": `multipart/form-data; boundary=${boundary}`,
          Authorization: "Token " + localStorage.getItem("token"),
          accept: "application/json",
        },
        body: formData,
      }
    );
    const data = await res.json();
    if (data.output) {
      setUserQueryText("");
      updateQuery();
    }
  };

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
    askQuery,
    userQueryText,
    setUserQueryText,
    query,
  };
}
