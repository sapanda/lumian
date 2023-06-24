import { Button } from "@mui/material";
import { projects_icon } from "../../../assets/icons/svg";
import { PrivateContainer } from "../../../components/Containers";
import { TableL } from "../../../components/molecules";
import GetStarted from "./GetStarted";
import { PrivateAppbar } from "../../../layout";
import { PROJECTS } from "../../../router/routes.constant";
import { useNavigate } from "react-router-dom";
import useProjects from "../useProjects";
import {
  connectApp,
  useCalendarStatusQuery,
  useSendAccessTokenMutation,
} from "../../../api/meetingApi";
import { useEffect, useRef } from "react";

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
    field: "interviews",
    headerName: "Interviews",
    width: 200,
  },
];

interface rowType {
  [key: string]: string | number;
}

export default function AllProjects() {
  const navigate = useNavigate();
  const { allProjects } = useProjects();
  const { status } = useCalendarStatusQuery();

  const urlParams = new URLSearchParams(window.location.search);
  const code = urlParams.get("code");
  const { mutateAsync: sendAccessToken } = useSendAccessTokenMutation();
  const apiCalledFlag = useRef<boolean>(false);
  function onCellClick(row: rowType) {
    const projectId = row.id;

    if (!projectId) return;

    navigate(
      PROJECTS.SELECTED_PROJECT.default.replace(":projectId", `${projectId}`)
    );
  }
  useEffect(() => {
    if (code && !apiCalledFlag.current) {
      apiCalledFlag.current = true;
      sendAccessToken(code);
    }
  }, [code, sendAccessToken]);

  return (
    <PrivateContainer
      appBar={
        <PrivateAppbar title="Projects" icon={projects_icon}>
          <div className="flex items-center justify-end w-full gap-5 px-10">
            {status !== "loading" && status !== "success" && (
              <Button variant="contained" onClick={() => connectApp()}>
                Connect App
              </Button>
            )}
            <Button
              variant="contained"
              onClick={() => navigate(PROJECTS.CREATE_PROJECT)}
            >
              New Project
            </Button>
          </div>
        </PrivateAppbar>
      }
    >
      {allProjects?.length === 0 && <GetStarted />}
      {allProjects?.length > 0 && (
        <div className="flex flex-col py-10 px-[132px]">
          <TableL
            rows={allProjects}
            columns={columns}
            onCellClick={onCellClick}
            onEditClick={(row) => {
              const projectId = row.id;
              navigate(
                PROJECTS.MANAGE_PROJECT.replace(":projectId", `${projectId}`)
              );
            }}
          />
        </div>
      )}
    </PrivateContainer>
  );
}
