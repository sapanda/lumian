import { useRef, useState } from "react";
import {
  cloud_upload__icon,
  projects_icon,
} from "../../../../assets/icons/svg";
import { PrivateContainer } from "../../../../components/Containers";
import {
  FileUploadDnD,
  ModalL,
  TabNav,
} from "../../../../components/molecules";
import { GetStarted, InterviewsTab } from ".";

import useInterviewsList from "./useInterviewsList";
import { PrivateAppbar } from "../../../../layout";
import { Button, Typography } from "@mui/material";
import { useCreateInterviewWithTranscriptMutation } from "../../../../api/meetingApi";
import { updateProject } from "../../../../api/projectApi";
import { PROJECTS } from "../../../../router/routes.constant";
import { useNavigate } from "react-router-dom";
import TranscribeModal from "./TranscribeModal";

export default function InterviewsList() {
  const {
    rows,
    columns,
    projectTitle,
    projectId,
    getProject,
    refreshProjectsList,
    date,
  } = useInterviewsList();

  const navigate = useNavigate();
  const [modalOpen, setModalOpen] = useState<boolean>(false);
  const [transcribeModalOpen, setTranscribeModalOpen] =
    useState<boolean>(false);
  const [pickedFiles, setPickedFiles] = useState<File[]>([]);
  const transcriptRef = useRef<string>("");
  const { mutateAsync: createInterview } =
    useCreateInterviewWithTranscriptMutation(
      parseInt(projectId || "0"),
      transcriptRef.current
    );
  async function onEditEnd(newTitle: string) {
    const res = await updateProject(
      {
        title: newTitle,
      },
      parseInt(projectId || "0")
    );
    if (res.status === 200) {
      await getProject();
      await refreshProjectsList();
    }
  }
  const handlePickedFiles = (files: File[]) => {
    setPickedFiles(files);
    //read the content of the file, it will be a json file
    const reader = new FileReader();
    reader.readAsText(files[0]);
    reader.onloadend = () => {
      // The file's text will be printed here
      transcriptRef.current = reader.result as string;
    };
  };

  const handleUpload = () => {
    //upload the file to the server
    createInterview();
    setPickedFiles([]);
    setModalOpen(false);
  };

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
          isTitleEditable
          onEditEnd={(newTitle: string) => onEditEnd(newTitle)}
        >
          <div className="flex items-center justify-end w-full gap-5 px-10">
            <Typography variant="body1">{date ?? ""}</Typography>
            {rows?.length > 0 && (
              <>
                <Button
                  variant="contained"
                  onClick={() => setTranscribeModalOpen(true)}
                >
                  Transcribe
                </Button>

                <Button variant="contained" onClick={() => setModalOpen(true)}>
                  Upload
                </Button>
              </>
            )}
            <Button
              variant="outlined"
              onClick={() =>
                navigate(
                  PROJECTS.MANAGE_PROJECT.replace(":projectId", `${projectId}`)
                )
              }
            >
              Settings
            </Button>
          </div>
        </PrivateAppbar>
      }
    >
      {rows?.length === 0 && (
        <GetStarted
          onUploadClick={() => setModalOpen(true)}
          startTranscibe={() => setTranscribeModalOpen(true)}
        />
      )}
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

      <ModalL
        open={modalOpen}
        handleClose={() => setModalOpen(false)}
        containerStyles={{
          maxWidth: "400px",
        }}
      >
        <div className="flex flex-col gap-5">
          <h3 className="text-20-700">Upload Transcripts</h3>
          <p className="text-12-400">
            Drop your transcript text files in the area below to start
            processing. Upon upload, your project status will be updated to
            Processing and will remain so until all transcripts have been
            successfully processed.
          </p>

          <FileUploadDnD
            onUpload={(files: File[]) => {
              handlePickedFiles(files);
            }}
            uploaderStyles={{
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              alignItems: "center",
              height: "132px",
            }}
            extensions={{
              "application/json": [".json"],
              "text/plain": [".txt"],
            }}
          >
            <img src={cloud_upload__icon} alt="cloud_upload__icon" />
            <span className="text-sm text-gray-500">
              Drag & drop files or click to browse
            </span>
          </FileUploadDnD>
          {pickedFiles.length > 0 && (
            <div className="flex flex-col items-center justify-center rounded py-[10px] border-gray400 border-solid border-2">
              {pickedFiles.map((file, index) => (
                <div key={index} className="flex flex-col gap-2">
                  <span className="text-xs text-gray-500">{file.name}</span>
                </div>
              ))}
            </div>
          )}
          <div className="flex justify-end gap-5">
            <Button
              variant="outlined"
              onClick={() => {
                setPickedFiles([]);
                setModalOpen(false);
              }}
            >
              Cancel
            </Button>
            <Button
              variant="contained"
              onClick={() => {
                handleUpload();
              }}
            >
              Upload
            </Button>
          </div>
        </div>
      </ModalL>
      <TranscribeModal
        modalOpen={transcribeModalOpen}
        setModalOpen={setTranscribeModalOpen}
        projectId={projectId}
      />
    </PrivateContainer>
  );
}
