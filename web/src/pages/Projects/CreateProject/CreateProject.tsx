import { useState } from "react";
import { Button, Stack, Typography } from "@mui/material";
import { PrivateContainer } from "../../../components/Containers";
import { projects_icon } from "../../../assets/icons/svg";
import { LabelInputCombo } from "../../../components/molecules";
import useCreateProject from "./useCreateProject";
import { PrivateAppbar } from "../../../layout";
import { PROJECTS } from "../../../router/routes.constant";
import { useNavigate } from "react-router-dom";
import ModalL from "../../../components/molecules/ModalL/ModalL";

export default function CreateProject() {
  const { errors, handleChange, handleSave, state, projectId, deleteProject } =
    useCreateProject();
  const [modalOpen, setModalOpen] = useState<boolean>(false);
  const navigate = useNavigate();
  return (
    <PrivateContainer
      appBar={<PrivateAppbar title="Projects" icon={projects_icon} />}
    >
      <div className="flex flex-col w-full items-center justify-center mt-[5%]">
        <div className="flex flex-col min-w-[600px] max-w-[600px] gap-4">
          <Typography variant="h1">
            {projectId ? "Manage Project" : "Create a New Project"}
          </Typography>

          <LabelInputCombo
            label="Name"
            onChange={handleChange}
            value={state.projectName}
            placeholder="Name of the Project"
            name="projectName"
            error={errors.projectName}
            size="small"
          />

          <LabelInputCombo
            label="Goal"
            inputDescription="Describe briefly what you’re looking to achieve with the project"
            onChange={handleChange}
            value={state.goal}
            placeholder="Explore why older workers do not maximize their 401(k) employer match"
            name="goal"
            error={errors.goal}
            size="small"
          />

          <LabelInputCombo
            label="Questions"
            inputDescription="These are the questions you’d like us to answer for you. List each question on a new line."
            onChange={handleChange}
            value={state.questions}
            placeholder="What are the main themes around financial priorities that the interviewees expect to have at retirement?
            Are interviewees with lower debt levels more likely to contribute to their 401(k)?"
            name="questions"
            error={errors.questions}
            size="small"
            multiline
          />

          <Stack sx={{ flexDirection: "row", gap: "12px" }}>
            <Button
              variant="contained"
              sx={{
                width: "100px",
              }}
              onClick={handleSave}
            >
              Save
            </Button>
            <Button
              variant="text"
              sx={{
                width: "100px",
              }}
              onClick={() => navigate(PROJECTS.default)}
            >
              Cancel
            </Button>
            {projectId && (
              <div className="flex justify-end w-full">
                <Button
                  variant="text"
                  sx={{ width: "100px" }}
                  color="error"
                  onClick={() => projectId && setModalOpen(true)}
                >
                  Delete
                </Button>
              </div>
            )}
          </Stack>
        </div>
      </div>

      {/* ------------ DELETE PROJECT MODAL----------- */}
      <ModalL open={modalOpen} handleClose={() => setModalOpen(false)}>
        <div className="flex flex-col justify-center gap-5 max-w-[400px]">
          <h2 className="text-20-700">Delete Project?</h2>
          <p className="text-red-500 text-12-400">
            All interviews in this project will also be deleted. Neither the
            project nor the interviews can be recovered. Are you sure you want
            to proceed?
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
                projectId && deleteProject(parseInt(projectId));
                setModalOpen(false);
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
