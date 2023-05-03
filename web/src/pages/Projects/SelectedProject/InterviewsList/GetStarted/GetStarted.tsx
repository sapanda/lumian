import { Button, Stack, Typography } from "@mui/material";
import { useNavigate } from "react-router-dom";
import { PROJECTS } from "../../../../../router/routes.constant";
import { DescriptionText } from "../../../../../components/atoms";
import line from "./line.svg";
export default function GetStarted() {
  const navigate = useNavigate();
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
          <Typography variant="h4">Create an Interview</Typography>
          <Stack>
            <Typography variant="body1" fontWeight="bold">
              Upload a transcript
            </Typography>

            <DescriptionText>You can upload multiple files</DescriptionText>

            <div style={{ marginTop: "8px" }}>
              <Button variant="contained">Upload Transcript</Button>
            </div>
          </Stack>

          <Stack
            sx={{
              display: "flex",
              flexDirection: "row",
              gap: "20px",
            }}
          >
            <img src={line} alt="line" />
            OR
            <img src={line} alt="line" />
          </Stack>

          <Stack>
            <Typography variant="body1" fontWeight="bold">
              Initiate transcription for a live interview
            </Typography>
            <DescriptionText>
              If you’ve already initiated the interview, you can connect our bot
              and get a live transcript at the end of the interview
            </DescriptionText>

            <div
              style={{ marginTop: "8px" }}
              onClick={() => {
                navigate(PROJECTS.CREATE_PROJECT);
              }}
            >
              <Button variant="contained">Initiate Transcription</Button>
            </div>
          </Stack>
        </Stack>
      </Stack>
    </Stack>
  );
}
