import { Button, Stack, Typography } from "@mui/material";

export default function CreateProject() {
  return (
    <Stack
      sx={{
        flex: 1,
        height: "100%",
        alignItems: "center",
      }}
    >
      <Stack sx={{ maxWidth: "360px", marginTop: "10%" }}>
        <Stack gap="20px">
          <Typography variant="h4">Let's get started</Typography>
          <Stack>
            <Typography variant="body1" fontWeight="bold">
              Connect your conferencing app (optional)
            </Typography>

            <Typography variant="body1">
              <i>
                Select from Zoom, Teams, Meet, Webex and more to get automated
                transcripts at the end of a call
              </i>
            </Typography>
            <div style={{ marginTop: "8px" }}>
              <Button variant="contained">Connect App</Button>
            </div>
          </Stack>
          <Stack>
            <Typography variant="body1" fontWeight="bold">
              Create a new project
            </Typography>

            <Typography variant="body1">
              <i>
                You’ll need to create a project to get started with processing
                interviews
              </i>
            </Typography>
            <div style={{ marginTop: "8px" }}>
              <Button variant="contained">New Project</Button>
            </div>
          </Stack>
        </Stack>
      </Stack>
    </Stack>
  );
}
