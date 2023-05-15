import { useEffect, useState, useCallback } from "react";
import {
  baseApiUrl,
  interviewEndPoints,
  projectEndpoints,
} from "../../../../api/apiEndpoints";
import { useParams } from "react-router-dom";

interface summaryProps {
  text: string;
  references: [number, number][];
  [key: string]: string | number | Array<Array<number>>;
}

export default function useInterview() {
  const [activeTab, setActiveTab] = useState(0);

  const [interviewTranscript, setInterviewTranscript] = useState<string>("");
  const [summary, setSummary] = useState<summaryProps[]>([]);
  const [concise, setConcise] = useState<summaryProps[]>([]);
  const [projectTitle, setProjectTitle] = useState<string>("");
  const [interviewTitle, setInterviewTitle] = useState<string>("");

  const { interviewId, projectId } = useParams();

  const getInterviewTranscript = useCallback(async () => {
    const res = await fetch(
      baseApiUrl +
        interviewEndPoints.interviewTranscipt.replace(
          ":interviewId",
          `${interviewId}`
        ),
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Token " + localStorage.getItem("token"),
        },
      }
    );

    const data = await res.json();
    if (data.transcript) setInterviewTranscript(data.transcript);
    if (data.title) setInterviewTitle(data.title);
  }, [interviewId]);

  const getInterviewSummary = useCallback(async () => {
    const res = await fetch(
      baseApiUrl +
        interviewEndPoints.interviewSummary.replace(
          ":interviewId",
          `${interviewId}`
        ),
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Token " + localStorage.getItem("token"),
        },
      }
    );

    const data = await res.json();
    if (data.output) setSummary(data.output);
  }, [interviewId]);

  const getInterviewConcise = useCallback(async () => {
    const res = await fetch(
      baseApiUrl +
        interviewEndPoints.interviewConcise.replace(
          ":interviewId",
          `${interviewId}`
        ),
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Token " + localStorage.getItem("token"),
        },
      }
    );

    const data = await res.json();
    if (data.output) setConcise(data.output);
  }, [interviewId]);


  const getProjectDetail = useCallback(async () => {
    const res = await fetch(
      baseApiUrl +
        projectEndpoints.projectDetail.replace(":projectId", `${projectId}`),
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Token " + localStorage.getItem("token"),
        },
      }
    );

    const data = await res.json();
    if (data.title) {
      setProjectTitle(data.title);
    }
  }, [projectId]);

  useEffect(() => {
    if (activeTab === 0) getInterviewSummary();
    else if (activeTab === 1) getInterviewConcise();
    
  }, [getInterviewSummary, getInterviewConcise, activeTab]);

  useEffect(() => {
    getInterviewTranscript();
  }, [getInterviewTranscript]);

  useEffect(() => {
    getProjectDetail();
  }, [getProjectDetail]);

  return {
    interviewTranscript,
    summary,
    concise,
    setActiveTab,
    interviewTitle,
    projectTitle,
    projectId,
  };
}