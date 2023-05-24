import { useCallback, useEffect, useState } from "react";
import { baseApiUrl, projectEndpoints } from "../../api/apiEndpoints";

interface projectType {
  id: number;
  goal: string;
  questions: string[];
  title: string;
}
export default function useProjects() {
  const [allProjects, setAllProjects] = useState([]);

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

  useEffect(() => {
    getProjectsList();
  }, []);

  return { allProjects };
}
