import { useParams } from "react-router-dom";
import {
  useGetMeetingConciseQuery,
  useGetMeetingSummaryQuery,
  useGetMeetingTranscriptQuery,
} from "../../../../api/meetingApi";
import { useGetProjectQuery } from "../../../../api/projectApi";

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

  return {
    interviewTranscript: interviewData?.transcript ?? "",
    summary: summaryData?.output ?? [],
    concise: conciseData?.output ?? [],
    interviewTitle: interviewData?.title ?? "",
    projectTitle: projectData?.name ?? "",
    projectId,
  };
}
