import { projects_icon } from "../../../../assets/icons/svg";
import { PrivateContainer } from "../../../../components/Containers";
import { TabNav } from "../../../../components/molecules";
import { GetStarted, InterviewsTab } from ".";

import useInterviewsList from "./useInterviewsList";
import { PrivateAppbar } from "../../../../layout";
import { Button, Stack, Typography } from "@mui/material";

export default function InterviewsList() {
  const { rows, columns } = useInterviewsList();

  return (
    <PrivateContainer
      appBar={
        <PrivateAppbar
          title="Projects"
          icon={projects_icon}
          breadcrumb={{
            title: "All projects",
            path: "/all-projects",
          }}
        >
          <Stack
            direction="row"
            gap="20px"
            sx={{
              width: "100%",
              alignItems: "center",
              justifyContent: "flex-end",
              padding: "20px 40px",
            }}
          >
            <Typography variant="body1">Feb 2 to Feb 10</Typography>
            <Button variant="contained">Transcribe</Button>
            <Button variant="contained">Upload</Button>
            <Button variant="outlined">Settings</Button>
          </Stack>
        </PrivateAppbar>
      }
    >
      {rows.length === 0 && <GetStarted />}
      {rows.length > 0 && (
        <TabNav
          tabs={[
            {
              name: "Interviews",
              component: <InterviewsTab rows={rows} columns={columns} />,
            },
            {
              name: "Insights",
              component: <h1>Insights</h1>,
            },
            {
              name: "Query",
              component: <h1>Query</h1>,
            },
          ]}
          activeTabIndex={0}
        />
      )}
    </PrivateContainer>
  );
}
