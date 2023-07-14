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
  meeting_url: string | undefined;
  start_time?: string | undefined;
  end_time?: string | undefined;
  title?: string | undefined;
}

const connectApp = async (appName: "google" | "microsoft") => {
  const res = await axiosInstance.get(`${meetingEndPoints.oauthUrl}`, {
    params: {
      app: appName,
    },
  });
  if (!res.data.data) return;

  const redirectUrl = res.data.data;
  window.location.href = redirectUrl;
};

const disconnectApp = async (appName: "google" | "microsoft") => {
  axiosInstance.delete(meetingEndPoints.removeCalendar, {
    params: {
      app: appName,
    },
  });
};

const sendAccessToken = async (
  code: string | null | undefined,
  app: "google" | "microsoft"
) => {
  if (!code) return;
  return await axiosInstance.post(meetingEndPoints.accessToken, {
    code: code,
    app,
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
  const start_time_min = res.data.data.start_time_min;
  const end_time_max = res.data.data.end_time_max;

  const startTime = start_time_min
    ? new Date(start_time_min).toLocaleDateString([], {
        month: "short",
        day: "numeric",
      })
    : "";

  const endTime = end_time_max
    ? new Date(end_time_max).toLocaleDateString([], {
        month: "short",
        day: "numeric",
      })
    : "";

  const formattedDate = startTime ? `${startTime} to ${endTime}` : "";

  const transformedData = res.data.data.transcripts
    ? res?.data?.data?.transcripts?.map((row: rowProps) => {
        const formattedDate = row["start_time"]
          ? new Date(row["start_time"]).toLocaleDateString([], {
              month: "short",
              day: "numeric",
            })
          : "-";
        const start_time = row["start_time"]
          ? new Date(row["start_time"]).toLocaleTimeString()
          : "";

        const end_time = row["end_time"]
          ? new Date(row["end_time"]).toLocaleTimeString()
          : "";

        let length = "-";

        const timeDifference =
          !!start_time && !!end_time
            ? new Date(row["end_time"]).getTime() -
              new Date(row["start_time"]).getTime()
            : 0;

        if (timeDifference !== 0) {
          const timeLengthInMins = Math.floor(timeDifference / 60000);
          length = `${timeLengthInMins} ${
            timeLengthInMins > 1 ? "mins" : "min"
          }`;
        }
        return {
          id: row["id"],
          title: row["title"],
          date: formattedDate,
          length,
        };
      })
    : [];
  return { interviewArr: transformedData, date: formattedDate };
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
  return res.data.data;
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
  return res.data.data;
};

const getMeetingSummary = async (meetingId: number | undefined) => {
  if (!meetingId) return;
  const res = await axiosInstance.get(
    interviewEndPoints.interviewSummary.replace(
      ":interviewId",
      meetingId.toString()
    )
  );
  return res.data.data;
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

  return { data: res.data.data, queryLevel: queryLevel, status: res.status };
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
      },
    }
  );
  const data = await res.data.data;
  return data;
};

const getCalendarStatus = async (appName: "google" | "microsoft") => {
  const res = await axiosInstance.get(meetingEndPoints.calendarStatus, {
    params: {
      app: appName,
    },
  });
  return res.data;
};

const getMeetingsList = async () => {
  const res = await axiosInstance.get(meetingEndPoints.meetingsList);
  return res.data.data;
};

const addBotToMeeting = async (meetingDetails: MeetingDataType) => {
  if (!meetingDetails.meeting_url || !meetingDetails.project_id) return;
  const res = await axiosInstance.post(
    meetingEndPoints.addBotToMeeting,
    meetingDetails
  );
  return res.data.data;
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
  const result = useQuery(
    queryKey,
    () => getMeetingQuery(meetingId, queryLevel),
    {
      staleTime: 1000 * 60 * 30, // 30 minutes
      enabled: !!meetingId,
    }
  );

  const { data, refetch } = result;
  data?.status === 202 && refetch();

  return result;
};

const useAskQueryMutation = (
  interviewId: number | undefined,
  queryLevel: "project" | "transcript"
) => {
  const queryClient = useQueryClient();
  return useMutation(
    (query: string) => askQuery(interviewId, query, queryLevel),
    {
      onSuccess: (data) => {
        if (data.output) {
          queryClient.invalidateQueries(["meetingQuery", interviewId]);
        }
      },
    }
  );
};

const useCalendarStatusQuery = (appName: "google" | "microsoft") => {
  const queryKey: QueryKey = ["calendarStatus", appName];

  return useQuery(queryKey, () => getCalendarStatus(appName), {
    staleTime: 1000 * 60 * 30, // 30 minutes
    retry: false,
    refetchOnWindowFocus: false,
  });
};

const useSendAccessTokenMutation = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  return useMutation(
    ({
      code,
      app,
    }: {
      code: string | null | undefined;
      app: "google" | "microsoft";
    }) => sendAccessToken(code, app),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(["calendarStatus"]);
        navigate(PROJECTS.default);
      },
    }
  );
};

const useMeetingListQuery = (modalOpen: boolean) => {
  const queryKey: QueryKey = ["meetingList"];
  return useQuery(queryKey, () => getMeetingsList(), {
    staleTime: 1000 * 60 * 30, // 30 minutes
    retry: false,
    enabled: modalOpen,
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

const useDisconnectAppMutation = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (appName: "google" | "microsoft") => disconnectApp(appName),
    {
      onSuccess: () => {
        setTimeout(() => {
          queryClient.invalidateQueries(["calendarStatus"]);
        }, 1000);
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
  useDisconnectAppMutation,
};
