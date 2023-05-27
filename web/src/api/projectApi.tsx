import { useQuery } from "@tanstack/react-query";
import { axiosInstance } from "./api";
import { baseApiUrl, projectEndpoints } from "./apiEndpoints";

interface ProjectType {
  id: number;
  goal: string;
  questions: string[];
  title: string;
}
const getProjects = async () => {
  const res = await axiosInstance.get(
    `${baseApiUrl}${projectEndpoints.projectList}`
  );
  const transformedData = res.data.map((project: ProjectType) => {
    return {
      id: project.id,
      name: project.title,
      date: "Feb 2 to Feb 10",
      participants: "10",
      owner: "John Doe",
    };
  });
  return transformedData;
};

const useGetProjectsQuery = () => {
  return useQuery(["projects"], getProjects, {
    staleTime: 1000 * 60 * 30, // 30 minutes
  });
};

export { useGetProjectsQuery };
