import { Stack } from "@mui/material";
import { projects_icon } from "../../../assets/icons/svg";
import { PrivateContainer } from "../../../components/Containers";
import { TableL } from "../../../components/molecules";
import GetStarted from "./GetStarted";

const allProjects = [
  {
    id: 1,
    name: "Project 1",
    date: "2022-09-01 to 2022-09-12",
    participants: 10,
    owner: "John Doe",
  },
  {
    id: 2,
    name: "Project 2",
    date: "2021-11-01 to 2021-12-03",
    participants: 8,
    owner: "Trisha Johansson",
  },
  {
    id: 3,
    name: "Project 3",
    date: "2021-10-01 to 2021-10-12",
    participants: 10,
    owner: "Tony Stark",
  },
];
const columns = [
  {
    field: "name",
    headerName: "Name",
    width: 200,
  },
  {
    field: "date",
    headerName: "Dates",
    width: 200,
  },
  {
    field: "participants",
    headerName: "Participants",
    width: 200,
  },
  {
    field: "owner",
    headerName: "Owner",
    width: 200,
  },
];
export default function AllProjects() {
  return (
    <PrivateContainer title="Projects" icon={projects_icon}>
      {allProjects.length === 0 && <GetStarted />}
      {allProjects.length > 0 && (
        <Stack
          sx={{
            padding: "40px 132px",
          }}
        >
          <TableL rows={allProjects} columns={columns} />
        </Stack>
      )}
    </PrivateContainer>
  );
}
