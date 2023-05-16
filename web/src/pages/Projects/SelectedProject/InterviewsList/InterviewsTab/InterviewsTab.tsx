import { Stack } from "@mui/material";
import { TableL } from "../../../../../components/molecules";

interface InterviewsTabProps {
  rows: {
    [key: string]: string | number;
  }[];
  columns: {
    headerName: string;
    field: string;
  }[];
}

export default function InterviewsTab(props: InterviewsTabProps) {
  const { rows, columns } = props;
  return (
    <Stack
      sx={{
        padding: "40px 132px",
      }}
    >
      <TableL rows={rows} columns={columns} />
    </Stack>
  );
}
