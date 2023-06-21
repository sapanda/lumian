import {
  QueryKey,
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";
import { axiosInstance } from "./api";
import { interviewEndPoints, meetingEndPoints } from "./apiEndpoints";
import { useNavigate } from "react-router-dom";
import { PROJECTS } from "../router/routes.constant";

export const QUERY_LEVEL = {
  PROJECT_LEVEL: "project",
  TRANSCRIPT_LEVEL: "transcript",
};

interface rowProps {
  [key: string]: string | number;
}

interface MeetingTranscriptPayloadType {
  project: number | undefined;
  title?: string;
  interviewee_names?: string[];
  interviewer_names?: string[];
  transcript?: string;
}

interface MeetingDataType {
  project_id: string | number | null | undefined;
  bot_name: string | undefined;
  meeting_url: string | undefined;
  start_time: string | undefined;
  end_time: string | undefined;
  title: string | undefined;
}

const connectApp = async () => {
  const res = await axiosInstance.get(`${meetingEndPoints.oauthUrl}`);
  const redirectUrl = res.data;
  window.location.href = redirectUrl;
};

const sendAccessToken = async (code: string | null | undefined) => {
  if (!code) return;
  return await axiosInstance.post(meetingEndPoints.accessToken, {
    code: code,
  });
};

const getInterviewsList = async (project_id: number | undefined) => {
  if (!project_id) return;
  const res = await axiosInstance.get(
    interviewEndPoints.interviewList.replace(
      ":projectId",
      project_id.toString()
    )
  );

  const transformedData = res.data.map((row: rowProps, index: number) => {
    return {
      id: row["id"],
      title: row["title"],
      date: `Feb ${index + 1}`,
      length: `${index + 1 * 10 + 1} mins`,
    };
  });
  return transformedData;
};

const startTranscribe = async (projectId: number | undefined) => {
  if (!projectId) return;
  await axiosInstance.post(meetingEndPoints.initiateTranscription, {
    project_id: projectId,
  });
};

const createInterviewWithTranscript = async (
  projectId: number | undefined,
  transcript: string
) => {
  if (!projectId) return;
  await axiosInstance.post(interviewEndPoints.transcript, {
    project: projectId,
    transcript: transcript,
    title: "Interview 1",
    interviewer_names: ["Interviewer 1"],
    interviewee_names: ["Interviewee 1"],
  });
};

const deleteInterview = async (interviewId: number | undefined) => {
  if (!interviewId) return;
  await axiosInstance.delete(
    interviewEndPoints.interviewTranscipt.replace(
      ":interviewId",
      interviewId.toString()
    )
  );
};

const getMeetingTranscript = async (meetingId: number | undefined) => {
  if (!meetingId) return;
  const res = await axiosInstance.get(
    interviewEndPoints.interviewTranscipt.replace(
      ":interviewId",
      meetingId.toString()
    )
  );
  return res.data;
};

const updateMeetingTranscript = async (
  payload: MeetingTranscriptPayloadType,
  meetingId: number | undefined
) => {
  if (!meetingId || !payload.project) return;
  return await axiosInstance.patch(
    interviewEndPoints.interviewTranscipt.replace(
      ":interviewId",
      meetingId.toString()
    ),
    payload
  );
};

const getMeetingConcise = async (meetingId: number | undefined) => {
  if (!meetingId) return;
  const res = await axiosInstance.get(
    interviewEndPoints.interviewConcise.replace(
      ":interviewId",
      meetingId.toString()
    )
  );
  return res.data;
};

const getMeetingSummary = async (meetingId: number | undefined) => {
  if (!meetingId) return;
  const res = await axiosInstance.get(
    interviewEndPoints.interviewSummary.replace(
      ":interviewId",
      meetingId.toString()
    )
  );
  return res.data;
};

const getMeetingQuery = async (
  meetingId: number | undefined,
  queryLevel: "project" | "transcript"
) => {
  if (!meetingId) return;
  const res = await axiosInstance.get(
    interviewEndPoints.interviewQuery
      .replace(":interviewId", meetingId.toString())
      .replace(":query_level", queryLevel)
  );
  return res.data;
};

const askQuery = async (
  interviewId: number | undefined,
  userQueryText: string,
  queryLevel: "project" | "transcript"
) => {
  if (!interviewId) return;

  const formData = new FormData();
  formData.append("query", userQueryText);
  formData.append("query_level", queryLevel);

  const boundary = Math.random().toString().substr(2);

  const res = await axiosInstance.post(
    interviewEndPoints.interviewQuery
      .replace(":interviewId", `${interviewId}`)
      .replace(":query_level", queryLevel),
    formData,
    {
      headers: {
        "Content-Type": `multipart/form-data; boundary=${boundary}`,
        accept: "application/json",
        showToast: false,
      },
    }
  );
  const data = await res.data;
  return data;
};

const getCalendarStatus = async () => {
  const res = await axiosInstance.get(meetingEndPoints.calendarStatus);
  return res.data;
};

const getMeetingsList = async () => {
  const res = await axiosInstance.get(meetingEndPoints.meetingsList);
  return res.data;
};

const addBotToMeeting = async (meetingDetails: MeetingDataType) => {
  if (
    !meetingDetails.meeting_url ||
    !meetingDetails.start_time ||
    !meetingDetails.end_time ||
    !meetingDetails.bot_name ||
    !meetingDetails.title
  )
    return;
  const res = await axiosInstance.post(
    meetingEndPoints.addBotToMeeting,
    meetingDetails
  );
  return res.data;
};

// hooks

const useInterviewsListQuery = (projectId: number | undefined) => {
  const queryKey: QueryKey = ["interviews", projectId];
  return useQuery(queryKey, () => getInterviewsList(projectId), {
    staleTime: 1000 * 60 * 30, // 30 minutes
    enabled: !!projectId,
  });
};

const useCreateInterviewWithTranscriptMutation = (
  projectId: number | undefined,
  transcript: string
) => {
  const queryClient = useQueryClient();
  return useMutation(
    () => createInterviewWithTranscript(projectId, transcript),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(["interviews", projectId]);
      },
    }
  );
};

const useDeleteInterviewMutation = (
  interviewId: number | undefined,
  projectId: number | undefined
) => {
  const queryClient = useQueryClient();
  return useMutation(() => deleteInterview(interviewId), {
    onSuccess: () => {
      queryClient.invalidateQueries(["interviews", projectId]);
    },
  });
};

const useGetMeetingTranscriptQuery = (meetingId: number | undefined) => {
  const queryKey: QueryKey = ["meetingTranscript", meetingId];
  return useQuery(queryKey, () => getMeetingTranscript(meetingId), {
    staleTime: 1000 * 60 * 30, // 30 minutes
    enabled: !!meetingId,
  });
};

const useGetMeetingConciseQuery = (meetingId: number | undefined) => {
  const queryKey: QueryKey = ["meetingConcise", meetingId];
  return useQuery(queryKey, () => getMeetingConcise(meetingId), {
    staleTime: 1000 * 60 * 30, // 30 minutes
    enabled: !!meetingId,
    refetchInterval(data) {
      return data ? 1000 * 60 * 30 : 5000;
    },
  });
};

const useGetMeetingSummaryQuery = (meetingId: number | undefined) => {
  const queryKey: QueryKey = ["meetingSummary", meetingId];
  return useQuery(queryKey, () => getMeetingSummary(meetingId), {
    staleTime: 1000 * 60 * 30, // 30 minutes
    enabled: !!meetingId,
    refetchInterval(data) {
      return data ? 1000 * 60 * 30 : 5000;
    },
  });
};

const useGetMeetingQuery = (
  meetingId: number | undefined,
  queryLevel: "project" | "transcript"
) => {
  const queryKey: QueryKey = ["meetingQuery", meetingId, queryLevel];
  return useQuery(queryKey, () => getMeetingQuery(meetingId, queryLevel), {
    staleTime: 1000 * 60 * 30, // 30 minutes
    enabled: !!meetingId,
    // refetchInterval(data) {
    //   return data ? 1000 * 60 * 30 : 5000;
    // },
  });
};

const useAskQueryMutation = (
  interviewId: number | undefined,
  query: string,
  queryLevel: "project" | "transcript"
) => {
  const queryClient = useQueryClient();
  return useMutation(() => askQuery(interviewId, query, queryLevel), {
    onSuccess: (data) => {
      if (data.output) {
        queryClient.invalidateQueries(["meetingQuery", interviewId]);
      }
    },
  });
};

const useCalendarStatusQuery = () => {
  const queryKey: QueryKey = ["calendarStatus"];
  return useQuery(queryKey, () => getCalendarStatus(), {
    staleTime: 1000 * 60 * 30, // 30 minutes
    retry: false,
    refetchOnWindowFocus: false,
  });
};

const useSendAccessTokenMutation = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  return useMutation(
    (code: string | null | undefined) => sendAccessToken(code),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(["calendarStatus"]);
        navigate(PROJECTS.default);
      },
    }
  );
};

const useMeetingListQuery = () => {
  const queryKey: QueryKey = ["meetingList"];
  return useQuery(queryKey, () => getMeetingsList(), {
    staleTime: 1000 * 60 * 30, // 30 minutes
    refetchOnMount: true,
  });
};

const useAddBotToMeetingMutation = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (meetingDetails: MeetingDataType) => addBotToMeeting(meetingDetails),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(["meetingList"]);
      },
    }
  );
};
export {
  connectApp,
  sendAccessToken,
  updateMeetingTranscript,
  useInterviewsListQuery,
  startTranscribe,
  useGetMeetingTranscriptQuery,
  useCreateInterviewWithTranscriptMutation,
  useDeleteInterviewMutation,
  useGetMeetingConciseQuery,
  useGetMeetingSummaryQuery,
  useGetMeetingQuery,
  useAskQueryMutation,
  useCalendarStatusQuery,
  useSendAccessTokenMutation,
  useMeetingListQuery,
  useAddBotToMeetingMutation,
};
