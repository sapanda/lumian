import { useEffect } from "react";
import { Button } from "@mui/material";
import { ModalL } from "../../../../components/molecules";
import { useNavigate } from "react-router-dom";
import { INTEGRATIONS } from "../../../../router/routes.constant";
import { line__icon } from "../../../../assets/icons/svg";
import { TextInputL } from "../../../../components/atoms";
import { useState } from "react";
import {
  useAddBotToMeetingMutation,
  useCalendarStatusQuery,
  useMeetingListQuery,
  useRemoveBotFromMeetingMutation,
} from "../../../../api/meetingApi";

interface TranscribeModalProps {
  modalOpen: boolean;
  setModalOpen: (value: boolean) => void;
  projectId: string | null | undefined;
}

interface Meeting {
  title: string;
  meeting_url: string;
  start_time: string;
  end_time: string;
  bot_added: boolean;
  bot_status: string;
  bot_id: string;
}

export default function TranscribeModal(props: TranscribeModalProps) {
  const { modalOpen, setModalOpen, projectId } = props;
  const [meetingUrl, setMeetingUrl] = useState<string>("");
  const navigate = useNavigate();
  const { status: googleStatus } = useCalendarStatusQuery("google");
  const { status: microsoftStatus } = useCalendarStatusQuery("microsoft");
  const { data: meetingsLists, refetch } = useMeetingListQuery(modalOpen);
  const { mutateAsync: addBotToMeeting } = useAddBotToMeetingMutation();
  const { mutateAsync: removeBotFromMeeting } =
    useRemoveBotFromMeetingMutation();

  const noAppConnected =
    googleStatus !== "success" && microsoftStatus !== "success";
  useEffect(() => {
    if (modalOpen) refetch();
  }, [modalOpen, refetch]);
  return (
    <ModalL open={modalOpen} handleClose={() => setModalOpen(false)}>
      <div className="flex flex-col justify-center gap-5 max-w-[500px]">
        <h2 className="text-20-700">Transcribe Meeting</h2>
        {!noAppConnected ? (
          <div className="flex flex-col gap-5">
            <p className="text-12-400">
              Have the Lumian Notetaker join a meeting that is currently in
              progress.
            </p>

            <div className="flex flex-col gap-5">
              <h2 className="text-gray-700 text-12-700">Current Meetings</h2>
              {meetingsLists?.length > 0 ? (
                <div className="flex flex-col gap-2">
                  {meetingsLists.map((meeting: Meeting) => {
                    return (
                      <div
                        className="flex items-center w-full gap-4"
                        key={meeting.meeting_url}
                      >
                        <div className="flex w-full gap-2 max-w-fit">
                          <span className="text-gray-600 text-12-400">
                            {new Date(meeting?.start_time).toLocaleTimeString(
                              [],
                              {
                                hour: "numeric",
                                minute: "numeric",
                                hour12: true,
                                timeZoneName: "short",
                              }
                            )}{" "}
                            -{" "}
                            {new Date(meeting?.end_time).toLocaleTimeString(
                              [],
                              {
                                hour: "numeric",
                                minute: "numeric",
                                hour12: true,
                                timeZoneName: "short",
                              }
                            )}
                          </span>
                          <span className="text-12-400">{meeting?.title}</span>
                        </div>
                        <div className="flex items-center justify-end flex-1 w-full gap-2">
                          {meeting.bot_added && (
                            <h2 className="text-gray-700 text-[10px] font-[400] italic">{`${meeting.bot_status}`}</h2>
                          )}
                          {meeting.bot_added ? (
                            <Button
                              variant="contained"
                              color="error"
                              onClick={() => {
                                removeBotFromMeeting(meeting?.bot_id).then(
                                  () => {
                                    setModalOpen(false);
                                  }
                                );
                              }}
                              sx={{
                                minWidth: "105px",
                                maxWidth: "105px",
                              }}
                            >
                              Cancel
                            </Button>
                          ) : (
                            <Button
                              variant="contained"
                              color="primary"
                              onClick={() => {
                                addBotToMeeting({
                                  ...meeting,
                                  project_id: projectId,
                                }).then(() => {
                                  setModalOpen(false);
                                });
                              }}
                              sx={{
                                minWidth: "105px",
                                maxWidth: "105px",
                              }}
                            >
                              Transcribe
                            </Button>
                          )}
                        </div>
                      </div>
                    );
                  })}
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
              onClick={() => {
                addBotToMeeting({
                  meeting_url: meetingUrl,
                  project_id: projectId,
                }).then(() => {
                  setModalOpen(false);
                  setMeetingUrl("");
                });
              }}
            >
              Transcribe
            </Button>
          </div>
        </div>
      </div>
    </ModalL>
  );
}
