import { Button, IconButton, Menu, Typography } from "@mui/material";
import { Concise, Query, Summary } from ".";
import {
  updateMeetingTranscript,
  useDeleteInterviewMutation,
} from "../../../../api/meetingApi";
import { profile_icon } from "../../../../assets/icons/svg";
import { PrivateContainer } from "../../../../components/Containers";
import { TabNav } from "../../../../components/molecules";
import { PrivateAppbar } from "../../../../layout";
import useInterview from "./useInterview";
import MoreHorizIcon from "@mui/icons-material/MoreHoriz";
import { useState } from "react";
import ModalL from "../../../../components/molecules/ModalL/ModalL";
import { useNavigate } from "react-router-dom";

export default function SelectedInterview() {
  const {
    summary,
    concise,
    interviewTitle,
    projectTitle,
    projectId,
    interviewId,
    refreshInterviewList,
    refreshInterviewData,
  } = useInterview();

  const { mutateAsync: deleteInterview } = useDeleteInterviewMutation(
    parseInt(interviewId || "0"),
    parseInt(projectId || "0")
  );
  const navigate = useNavigate();
  const [modalOpen, setModalOpen] = useState<boolean>(false);

  // --------- Menu --------------------
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };
  const handleClose = () => {
    setAnchorEl(null);
  };

  // --------- Menu Block End -----------

  async function onEditEnd(newTitle: string) {
    const res = await updateMeetingTranscript(
      {
        project: parseInt(projectId || "0"),
        title: newTitle,
      },
      parseInt(interviewId || "0")
    );

    if (res?.status === 200) {
      await refreshInterviewData();
      await refreshInterviewList();
    }
  }
  return (
    <PrivateContainer
      appBar={
        <PrivateAppbar
          title={interviewTitle}
          icon={profile_icon}
          breadcrumb={{
            title: projectTitle,
            path: `/project/${projectId}`,
          }}
          isTitleEditable
          onEditEnd={(newTitle) => {
            onEditEnd(newTitle);
          }}
        >
          <div className="flex items-center justify-end w-full gap-5 px-10">
            <Typography variant="body1">
              Thu Feb 10, 1:31pm to 2:16pm PT
            </Typography>
            <Button variant="text" color="inherit">
              <IconButton onClick={handleClick}>
                <MoreHorizIcon />
              </IconButton>
              <Menu
                sx={{
                  "& .MuiMenu-paper": {
                    width: "110px",
                  },
                }}
                anchorOrigin={{
                  vertical: "center",
                  horizontal: "left",
                }}
                anchorEl={anchorEl}
                id="account-menu"
                open={open}
                onClose={handleClose}
                onClick={handleClose}
                PaperProps={{
                  elevation: 0,
                  sx: {
                    overflow: "visible",
                    filter: "drop-shadow(0px 2px 8px rgba(0,0,0,0.32))",
                    mt: 1.5,
                    "& .MuiAvatar-root": {
                      width: 32,
                      height: 32,
                      ml: -0.5,
                      mr: 1,
                    },
                    "&:before": {
                      content: '""',
                      display: "block",
                      position: "absolute",
                      top: 0,
                      right: 14,
                      width: 10,
                      height: 10,
                      bgcolor: "background.paper",
                      zIndex: 0,
                    },
                  },
                }}
              >
                <div className="flex justify-center">
                  <Button
                    variant="text"
                    color="error"
                    onClick={() => {
                      setModalOpen(true);
                    }}
                    sx={{
                      width: "100px",
                      "&:hover": {
                        backgroundColor: "#FEE2E2",
                      },
                    }}
                  >
                    Delete
                  </Button>
                </div>
              </Menu>
            </Button>
          </div>
        </PrivateAppbar>
      }
    >
      <TabNav
        tabs={[
          {
            name: "Summary",
            component: <Summary data={summary} />,
          },
          {
            name: "Concise",
            component: <Concise data={concise} />,
          },
          {
            name: "Query",
            component: <Query />,
          },
        ]}
        activeTabIndex={0}
      />

      {/* ------------ DELETE INTERVIEW MODAL----------- */}
      <ModalL open={modalOpen} handleClose={() => setModalOpen(false)}>
        <div className="flex flex-col justify-center gap-5 max-w-[400px]">
          <h2 className="text-20-700">Delete Interview?</h2>
          <p className="text-red-500 text-12-400">
            This interview and its synthesized content will be permanently
            deleted. Are you sure you want to proceed?
          </p>

          <div className="flex justify-end gap-5">
            <Button
              variant="text"
              onClick={() => setModalOpen(false)}
              sx={{ width: "100px" }}
            >
              Cancel
            </Button>
            <Button
              variant="contained"
              color="error"
              sx={{ width: "100px" }}
              onClick={() => {
                projectId && deleteInterview();
                setModalOpen(false);
                setTimeout(() => {
                  navigate(`/project/${projectId}`);
                }, 1000);
              }}
            >
              Delete
            </Button>
          </div>
        </div>
      </ModalL>
    </PrivateContainer>
  );
}
