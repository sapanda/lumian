import { useGetProjectsQuery } from "../../api/projectApi";

export default function useProjects() {
  const { data: allProjects, isLoading, isFetching } = useGetProjectsQuery();

  return { allProjects, isLoading, isFetching };
}
