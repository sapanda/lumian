import { Button,  Typography } from "@mui/material";
import { useNavigate } from "react-router-dom";
import { PROJECTS } from "../../../../../router/routes.constant";
import { DescriptionText } from "../../../../../components/atoms";
import line from "./line.svg";
export default function GetStarted() {
  const navigate = useNavigate();
  return (
    <div className="flex flex-col items-center flex-1 h-full">
      <div className="flex flex-col max-w-[360px] mt-[10%]">
        <div className="flex flex-col gap-5">
          <Typography variant="h4">Create an Interview</Typography>
          <div className="flex flex-col">
            <Typography variant="body1" fontWeight="bold">
              Upload a transcript
            </Typography>

            <DescriptionText>You can upload multiple files</DescriptionText>

            <div className="mt-2">
              <Button variant="contained">Upload Transcript</Button>
            </div>
          </div>

          <div className="flex gap-5">
            <img src={line} alt="line" />
            OR
            <img src={line} alt="line" />
          </div>

          <div className="flex flex-col">
            <Typography variant="body1" fontWeight="bold">
              Initiate transcription for a live interview
            </Typography>
            <DescriptionText>
              If you’ve already initiated the interview, you can connect our bot
              and get a live transcript at the end of the interview
            </DescriptionText>

            <div
              className="mt-2"
              onClick={() => {
                navigate(PROJECTS.CREATE_PROJECT);
              }}
            >
              <Button variant="contained">Initiate Transcription</Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
