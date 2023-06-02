import { projects_icon } from "../../../../assets/icons/svg";
import { PrivateContainer } from "../../../../components/Containers";
import { TabNav } from "../../../../components/molecules";
import { GetStarted, InterviewsTab } from ".";

import useInterviewsList from "./useInterviewsList";
import { PrivateAppbar } from "../../../../layout";
import { Button, Typography } from "@mui/material";
import { startTranscribe } from "../../../../api/meetingApi";

export default function InterviewsList() {
  const { rows, columns, projectTitle, projectId } = useInterviewsList();

  return (
    <PrivateContainer
      appBar={
        <PrivateAppbar
          title={projectTitle}
          icon={projects_icon}
          breadcrumb={{
            title: "All projects",
            path: "/all-projects",
          }}
        >
          <div className="flex items-center justify-end w-full gap-5 px-10 py-5">
            <Typography variant="body1">Feb 2 to Feb 10</Typography>
            <Button
              variant="contained"
              onClick={() => startTranscribe(parseInt(projectId || "0"))}
            >
              Transcribe
            </Button>
            <Button variant="contained">Upload</Button>
            <Button variant="outlined">Settings</Button>
          </div>
        </PrivateAppbar>
      }
    >
      {rows?.length === 0 && <GetStarted />}
      {rows?.length > 0 && (
        <TabNav
          tabs={[
            {
              name: "Interviews",
              component: <InterviewsTab rows={rows} columns={columns} />,
            },
          ]}
          activeTabIndex={0}
        />
      )}
    </PrivateContainer>
  );
}
