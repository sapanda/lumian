import { useEffect } from "react";
import { useGetProjectsQuery } from "../../api/projectApi";
import { sendAccessToken } from "../../api/meetingApi";

export default function useProjects() {
  const { data: allProjects, isLoading, isFetching } = useGetProjectsQuery();

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get("code");
    if (code) {
      sendAccessToken(code);
    }
  }, []);

  return { allProjects, isLoading, isFetching };
}
