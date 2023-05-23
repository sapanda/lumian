import { useEffect, useState } from "react";
import {
  baseApiUrl,
  meetingEndPoints,
  projectEndpoints,
} from "../../api/apiEndpoints";
import { Code } from "@mui/icons-material";

interface projectType {
  id: number;
  goal: string;
  questions: string[];
  title: string;
}
export default function useProjects() {
  const [allProjects, setAllProjects] = useState([]);
  const clientID = import.meta.env.VITE_ZOOM_CLIENT_ID as string;

  // const clientSecret = import.meta.env.VITE_ZOOM_SECRETS_BASE64 as string;
  const scopes = "user:read";
  const zoomRedirectURL = import.meta.env.VITE_ZOOM_REDIRECT_URL as string;
  // const zoomRedirectURL = "http://localhost:8002/all-projects";

  const responseType = "code";
  const zoomAuthorizeURL = `https://zoom.us/oauth/authorize?response_type=${responseType}&client_id=${clientID}&redirect_uri=${zoomRedirectURL}&scope=${scopes}`;

  const getProjectsList = async () => {
    const res = await fetch(baseApiUrl + projectEndpoints.projectList, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Token " + localStorage.getItem("token"),
      },
    });

    const data = await res.json();
    if (data) {
      const _data = data.map((project: projectType) => {
        return {
          id: project.id,
          name: project.title,
          date: "Feb 2 to Feb 10",
          participants: "10",
          owner: "John Doe",
        };
      });
      setAllProjects(_data);
    }
  };

  const connectApp = async () => {
    window.location.href = zoomAuthorizeURL;
  };

  const sendAccessToken = async (code: string) => {
    const res = await fetch(baseApiUrl + meetingEndPoints.accessToken, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Token " + localStorage.getItem("token"),
      },
      body: JSON.stringify({
        code: code,
      }),
    });

    const data = await res.json();
    if (data) {
      const _data = data.map((project: projectType) => {
        return {
          id: project.id,
          name: project.title,
          date: "Feb 2 to Feb 10",
          participants: "10",
          owner: "John Doe",
        };
      });
      setAllProjects(_data);
    }
  };

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get("code");
    if (code) {
      sendAccessToken(code);
    }
  }, []);

  useEffect(() => {
    getProjectsList();
  }, []);

  return { allProjects, connectApp };
}
