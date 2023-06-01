import { useParams } from "react-router-dom";
import {
  useGetMeetingConciseQuery,
  useGetMeetingQuery,
  useGetMeetingSummaryQuery,
  useGetMeetingTranscriptQuery,
} from "../../../../api/meetingApi";
import { useGetProjectQuery } from "../../../../api/projectApi";
import { useCallback, useEffect, useRef, useState } from "react";
import { axiosInstance } from "../../../../api/api";
import { interviewEndPoints } from "../../../../api/apiEndpoints";

export default function useInterview() {
  const { interviewId, projectId } = useParams();

  const { data: projectData } = useGetProjectQuery(parseInt(projectId || "0"));
  const { data: interviewData } = useGetMeetingTranscriptQuery(
    parseInt(interviewId || "0")
  );
  const { data: summaryData } = useGetMeetingSummaryQuery(
    parseInt(interviewId || "0")
  );
  const { data: conciseData } = useGetMeetingConciseQuery(
    parseInt(interviewId || "0")
  );
  const { data: query, refetch: updateQuery } = useGetMeetingQuery(
    parseInt(interviewId || "0")
  );
  const originalTranscriptRef = useRef<string>("");
  const transcriptRef = useRef<HTMLDivElement>(null);

  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);
  const [conversation, setConversation] = useState<string>("");
  const [citationsCount, setCitationsCount] = useState<number>(0);
  const [activeCitationIndex, setActiveCitationIndex] = useState<number>(0);
  const [userQueryText, setUserQueryText] = useState<string>("");

  const askQuery = async () => {
    const formData = new FormData();
    formData.append("query", userQueryText);

    const boundary = Math.random().toString().substr(2);

    if (!interviewId) return;
    const res = await axiosInstance.post(
      interviewEndPoints.interviewQuery.replace(":interviewId", interviewId),
      formData,
      {
        headers: {
          "Content-Type": `multipart/form-data; boundary=${boundary}`,
          accept: "application/json",
        },
      }
    );
    const data = await res.data;

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

      setActiveCitationIndex(0);
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
        const selectedText = originalTranscriptRef?.current
          ?.slice(start, end)
          ?.replaceAll("\n\n", "<br/> <br/>");

        if (transcript && selectedText) {
          transcript = transcript
            ?.replace(
              selectedText,
              `<span style="background-color:#dbeafe;"id="highlight${index}"
            >${selectedText}</span>`
            )
            ?.replaceAll('"\n\n', '"<br/> <br/>');
        }
      });

      setConversation(transcript);
    },
    []
  );

  useEffect(() => {
    originalTranscriptRef.current = interviewData?.transcript;
    const _transcript = interviewData?.transcript.replaceAll(
      '"\n\n',
      '"<br/> <br/>'
    );
    setConversation(_transcript);
  }, [interviewData?.transcript]);

  useEffect(() => {
    scrollToNextHighlightedText(0);
  }, [conversation]);
  return {
    interviewTranscript: interviewData?.transcript ?? "",
    summary: summaryData?.output ?? [],
    concise: conciseData?.output ?? [],
    query,
    interviewTitle: interviewData?.title ?? "",
    projectTitle: projectData?.name ?? "",
    projectId,
    selectedIndex,
    citationsCount,
    activeCitationIndex,
    conversation,
    transcriptRef,
    handleSummaryItemClick,
    scrollToNextHighlightedText,
    askQuery,
    userQueryText,
    setUserQueryText,
  };
}
