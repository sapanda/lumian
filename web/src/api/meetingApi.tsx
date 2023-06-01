import { QueryKey, useQuery } from "@tanstack/react-query";
import { axiosInstance } from "./api";
import {
  baseApiUrl,
  interviewEndPoints,
  meetingEndPoints,
} from "./apiEndpoints";

interface rowProps {
  [key: string]: string | number;
}
const connectApp = async () => {
  const res = await axiosInstance.get(
    `${baseApiUrl}${meetingEndPoints.oauthUrl}`
  );
  const redirectUrl = res.data;
  window.location.href = redirectUrl;
};

const sendAccessToken = async (code: string) => {
  await axiosInstance.post(meetingEndPoints.accessToken, {
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

const getMeetingQuery = async (meetingId: number | undefined) => {
  if (!meetingId) return;
  const res = await axiosInstance.get(
    interviewEndPoints.interviewQuery.replace(
      ":interviewId",
      meetingId.toString()
    )
  );
  return res.data;
};

const useInterviewsListQuery = (projectId: number | undefined) => {
  const queryKey: QueryKey = ["interviews", projectId];
  return useQuery(queryKey, () => getInterviewsList(projectId), {
    staleTime: 1000 * 60 * 30, // 30 minutes
    enabled: !!projectId,
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
  });
};

const useGetMeetingSummaryQuery = (meetingId: number | undefined) => {
  const queryKey: QueryKey = ["meetingSummary", meetingId];
  return useQuery(queryKey, () => getMeetingSummary(meetingId), {
    staleTime: 1000 * 60 * 30, // 30 minutes
    enabled: !!meetingId,
  });
};

const useGetMeetingQuery = (meetingId: number | undefined) => {
  const queryKey: QueryKey = ["meetingQuery", meetingId];
  return useQuery(queryKey, () => getMeetingQuery(meetingId), {
    staleTime: 1000 * 60 * 30, // 30 minutes
    enabled: !!meetingId,
  });
};

export {
  connectApp,
  sendAccessToken,
  useInterviewsListQuery,
  startTranscribe,
  useGetMeetingTranscriptQuery,
  useGetMeetingConciseQuery,
  useGetMeetingSummaryQuery,
  useGetMeetingQuery,
};
