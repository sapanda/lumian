import { useEffect } from "react";
import { baseApiUrl, meetingEndPoints } from "../../api/apiEndpoints";
import { useGetProjectsQuery } from "../../api/projectApi";
import { axiosInstance } from "../../api/api";

export default function useProjects() {
  // const clientID = import.meta.env.VITE_ZOOM_CLIENT_ID as string;
  // const scopes = "user:read";
  // const zoomRedirectURL = import.meta.env.VITE_ZOOM_REDIRECT_URL as string;

  // const responseType = "code";
  // const zoomAuthorizeURL = `https://zoom.us/oauth/authorize?response_type=${responseType}&client_id=${clientID}&redirect_uri=${zoomRedirectURL}&scope=${scopes}`;
  const { data: allProjects, isLoading, isFetching } = useGetProjectsQuery();

  const connectApp = async () => {
    const res = await axiosInstance.get(meetingEndPoints.oauthUrl);
    const redirectUrl = res.data;
    window.location.href = redirectUrl;
  };

  const sendAccessToken = async (code: string) => {
    await fetch(baseApiUrl + meetingEndPoints.accessToken, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Token " + localStorage.getItem("token"),
      },
      body: JSON.stringify({
        code: code,
      }),
    });
  };

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get("code");
    console.log(code);
    if (code) {
      sendAccessToken(code);
    }
  }, []);

  return { allProjects, connectApp, isLoading, isFetching };
}
