import { Button } from "@mui/material";
import { ModalL } from "../../../../components/molecules";
import { useNavigate } from "react-router-dom";
import { INTEGRATIONS } from "../../../../router/routes.constant";
import { line__icon } from "../../../../assets/icons/svg";
import { TextInputL } from "../../../../components/atoms";
import { useState } from "react";

interface TranscribeModalProps {
  modalOpen: boolean;
  setModalOpen: (value: boolean) => void;
  projectId: string | null | undefined;
}

interface Meeting {
  id: string;
  title: string;
  startTime: string;
  endTime: string;
}

const meetingsLists: Meeting[] = [
  {
    id: "1",
    title: "Meeting 1",
    startTime: "10:00 AM",
    endTime: "11:00 AM",
  },

  {
    id: "2",
    title: "Meeting 2",
    startTime: "11:00 AM",
    endTime: "12:00 PM",
  },
];

export default function TranscribeModal(props: TranscribeModalProps) {
  const { modalOpen, setModalOpen } = props;
  const [meetingUrl, setMeetingUrl] = useState<string>("");
  const navigate = useNavigate();
  const isAppConnected = false;

  return (
    <ModalL open={modalOpen} handleClose={() => setModalOpen(false)}>
      <div className="flex flex-col justify-center gap-5 max-w-[500px]">
        <h2 className="text-20-700">Transcribe Meeting</h2>
        {!isAppConnected ? (
          <div className="flex flex-col gap-5">
            <p className="text-12-400">
              Have the Lumian Notetaker join a meeting that is currently in
              progress.
            </p>

            <div className="flex flex-col">
              <h2 className="text-gray-700 text-12-700">Current Meetings</h2>
              {meetingsLists?.length > 0 ? (
                <div className="flex flex-col gap-1">
                  {meetingsLists.map((meeting) => (
                    <div className="flex items-center w-full gap-4">
                      <div className="flex w-full max-w-fit">
                        <span className="text-gray-600 text-12-400">
                          {meeting?.startTime} - {meeting?.endTime}
                        </span>
                      </div>
                      <div className="flex items-center justify-between w-full gap-2">
                        <span className="text-12-400">{meeting?.title}</span>
                        <Button
                          variant="contained"
                          color="primary"
                          onClick={() => {
                            console.log("Transcribe");
                          }}
                        >
                          Transcribe
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <span className="italic text-gray-600 text-12-400">
                  No meetings in progress
                </span>
              )}
            </div>
          </div>
        ) : (
          <div className="flex flex-col gap-5">
            <p className="text-12-400">
              Connect a calendar app to get started, or enter the meeting URL
              below. Once you start, you’ll see the Lumian Notetaker show up in
              your meeting!
            </p>
            <div className="flex items-center justify-between">
              <span className="text-gray-600 text-12-700">
                Connect App (Google, Microsoft)
              </span>
              <Button
                variant="contained"
                color="primary"
                onClick={() => {
                  navigate(INTEGRATIONS);
                }}
              >
                Connect
              </Button>
            </div>
          </div>
        )}

        <div className="flex gap-5">
          <img src={line__icon} alt="line" />
          OR
          <img src={line__icon} alt="line" />
        </div>

        <div className="flex flex-col gap-2">
          <span className="text-gray-600 text-12-700">
            Meeting URL (Zoom, Teams, Meet, Webex)
          </span>
          <TextInputL
            placeholder="Enter only the meeting URL"
            value={meetingUrl}
            onChange={(e) => {
              setMeetingUrl(e.target.value);
            }}
          />
          <div className="flex justify-end gap-7">
            <Button
              variant="outlined"
              color="primary"
              onClick={() => setModalOpen(false)}
            >
              Cancel
            </Button>
            <Button
              variant="contained"
              color="primary"
              disabled={meetingUrl === ""}
            >
              Transcribe
            </Button>
          </div>
        </div>
      </div>
    </ModalL>
  );
}
