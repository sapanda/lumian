import { Button, Typography } from "@mui/material";
import { useNavigate } from "react-router-dom";
import { PROJECTS } from "../../../../router/routes.constant";
import { connectApp, useCalendarStatusQuery } from "../../../../api/meetingApi";

export default function GetStarted() {
  const navigate = useNavigate();
  const { status } = useCalendarStatusQuery();
  return (
    <div className="flex flex-col items-center flex-1 h-full">
      <div className="flex flex-col max-w-[360px] mt-[10%]">
        <div className="flex flex-col gap-5">
          <Typography variant="h4">Let's get started</Typography>
          {status !== "loading" && status !== "success" && (
            <div className="flex flex-col">
              <Typography variant="body1" fontWeight="bold">
                Connect your conferencing app (optional)
              </Typography>

              <Typography variant="body1">
                <i>
                  Select from Zoom, Teams, Meet, Webex and more to get automated
                  transcripts at the end of a call
                </i>
              </Typography>
              <div className="mt-2">
                <Button variant="contained" onClick={() => connectApp()}>
                  Connect App
                </Button>
              </div>
            </div>
          )}
          <div className="flex flex-col">
            <Typography variant="body1" fontWeight="bold">
              Create a new project
            </Typography>

            <Typography variant="body1">
              <i>
                You’ll need to create a project to get started with processing
                interviews
              </i>
            </Typography>
            <div
              className="mt-2"
              onClick={() => {
                navigate(PROJECTS.CREATE_PROJECT);
              }}
            >
              <Button variant="contained">New Project</Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
