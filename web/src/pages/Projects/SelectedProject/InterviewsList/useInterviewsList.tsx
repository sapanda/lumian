import { useParams } from "react-router-dom";
import { useInterviewsListQuery } from "../../../../api/meetingApi";
import {
  useGetProjectQuery,
  useGetProjectsQuery,
} from "../../../../api/projectApi";

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
  const { projectId } = useParams();
  const { refetch: refreshProjectsList } = useGetProjectsQuery();
  const { data: rows } = useInterviewsListQuery(parseInt(projectId || "0"));
  const { data: project, refetch: getProject } = useGetProjectQuery(
    parseInt(projectId || "0")
  );

  return {
    rows,
    columns,
    projectTitle: project?.name,
    projectId,
    getProject,
    refreshProjectsList,
  };
}
