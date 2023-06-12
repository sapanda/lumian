import { useParams } from "react-router-dom";
import {
  useAskQueryMutation,
  useGetMeetingConciseQuery,
  useGetMeetingQuery,
  useGetMeetingSummaryQuery,
  useGetMeetingTranscriptQuery,
  useInterviewsListQuery,
} from "../../../../api/meetingApi";
import { useGetProjectQuery } from "../../../../api/projectApi";
import { useCallback, useEffect, useRef, useState } from "react";

export default function useInterview() {
  const { interviewId, projectId } = useParams();

  const { data: projectData } = useGetProjectQuery(parseInt(projectId || "0"));
  const { refetch: refreshInterviewList } = useInterviewsListQuery(
    parseInt(projectId || "0")
  );
  const { data: interviewData, refetch: refreshInterviewData } =
    useGetMeetingTranscriptQuery(parseInt(interviewId || "0"));
  const { data: summaryData } = useGetMeetingSummaryQuery(
    parseInt(interviewId || "0")
  );
  const { data: conciseData } = useGetMeetingConciseQuery(
    parseInt(interviewId || "0")
  );
  const { data: query } = useGetMeetingQuery(parseInt(interviewId || "0"));

  const originalTranscriptRef = useRef<string>("");
  const transcriptRef = useRef<HTMLDivElement>(null);

  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);
  const [conversation, setConversation] = useState<string>("");
  const [citationsCount, setCitationsCount] = useState<number>(0);
  const [activeCitationIndex, setActiveCitationIndex] = useState<number>(0);
  const [userQueryText, setUserQueryText] = useState<string>("");
  const currentRangeLength = useRef<number>(0);
  const { mutateAsync: onAskQuery } = useAskQueryMutation(
    parseInt(interviewId || "0"),
    userQueryText
  );
  const askQuery = async () => {
    if (!userQueryText) return;
    await onAskQuery();
    setUserQueryText("");
  };

  function scrollToNextHighlightedText(index: number) {
    let circularIndex = index % currentRangeLength.current;
    if (circularIndex < 0)
      circularIndex = currentRangeLength.current + circularIndex;
    const nextHightlightedText = transcriptRef.current?.querySelector(
      `#highlight${circularIndex}`
    );

    if (nextHightlightedText) {
      nextHightlightedText.scrollIntoView({
        behavior: "smooth",
        block: "center",
        inline: "center",
      });
      setActiveCitationIndex(circularIndex + 1);
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
          transcript = transcript?.replaceAll('"\n\n', '"<br/> <br/>')?.replace(
            selectedText,
            `<span style="background-color:#dbeafe;"id="highlight${index}"
          >${selectedText}</span>`
          );
        }
      });

      currentRangeLength.current = mergedRanges.length;

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
    summary: summaryData?.output ?? [],
    concise: conciseData?.output ?? [],
    query,
    interviewTitle: interviewData?.title ?? "",
    projectTitle: projectData?.name ?? "",
    projectId,
    interviewId,
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
    refreshInterviewData,
    refreshInterviewList,
  };
}
