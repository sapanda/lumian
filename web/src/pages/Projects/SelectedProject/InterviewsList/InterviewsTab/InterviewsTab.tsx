import { Stack } from "@mui/material";
import { TableL } from "../../../../../components/molecules";
import { useNavigate, useParams } from "react-router-dom";
import { PROJECTS } from "../../../../../router/routes.constant";

interface rowType {
  [key: string]: string | number;
}
interface InterviewsTabProps {
  rows: rowType[];
  columns: {
    headerName: string;
    field: string;
  }[];
}

export default function InterviewsTab(props: InterviewsTabProps) {
  const { rows, columns } = props;
  const navigate = useNavigate();
  const { projectId } = useParams();

  function onCellClick(row: rowType) {
    const interviewId = row.id;

    if (!projectId || !interviewId) {
      return;
    }
    navigate(
      PROJECTS.SELECTED_PROJECT.SELECTED_INTERVIEW.replace(
        ":projectId",
        `${projectId}`
      ).replace(":interviewId", `${interviewId}`)
    );
  }
  return (
    <Stack
      sx={{
        padding: "40px 132px",
      }}
    >
      <TableL rows={rows} columns={columns} onCellClick={onCellClick} />
    </Stack>
  );
}
