import { useEffect, useState, useCallback } from "react";
import {
  baseApiUrl,
  interviewEndPoints,
  meetingEndPoints,
  projectEndpoints,
} from "../../../../api/apiEndpoints";
import { useParams } from "react-router-dom";

interface rowProps {
  [key: string]: string | number;
}

const columns = [
  {
    headerName: "Title",
    field: "title",
  },
  {
    headerName: "Date",
    field: "date",
  },
  {
    headerName: "Length",
    field: "length",
  },
];
export default function useInterviewsList() {
  const [rows, setRows] = useState<rowProps[]>([]);
  const { projectId } = useParams();
  const [projectTitle, setProjectTitle] = useState("");

  const getInterviewsList = useCallback(async () => {
    const res = await fetch(
      baseApiUrl +
        interviewEndPoints.interviewList.replace(":projectId", `${projectId}`),
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Token " + localStorage.getItem("token"),
        },
      }
    );

    const data = await res.json();
    const rows = data.map((row: rowProps, index: number) => {
      return {
        id: row["id"],
        title: row["title"],
        date: `Feb ${index + 1}`,
        length: `${index + 1 * 10 + 1} mins`,
      };
    });
    setRows(rows);
  }, [projectId]);

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

  const startTranscribe = useCallback(async () => {
    if (!projectId) return;
    const project_id = +projectId;
    const res = await fetch(
      baseApiUrl + meetingEndPoints.initiateTranscription,

      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Token " + localStorage.getItem("token"),
        },
        body: JSON.stringify({
          project_id,
        }),
      }
    );

    const data = await res.json();
    console.log(data);
  }, [projectId]);

  useEffect(() => {
    getInterviewsList();
    getProjectDetail();
  }, [getInterviewsList, getProjectDetail]);

  return {
    rows,
    columns,
    projectTitle,
    startTranscribe,
  };
}
