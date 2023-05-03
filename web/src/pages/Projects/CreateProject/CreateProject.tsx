import { Button, Stack, Typography } from "@mui/material";
import { PrivateContainer } from "../../../components/Containers";
import { projects_icon } from "../../../assets/icons/svg";
import { LabelInputCombo } from "../../../components/molecules";
import useCreateProject from "./useCreateProject";

export default function CreateProject() {
  const { errors, handleChange, handleSave, state } = useCreateProject();
  return (
    <PrivateContainer title="Projects" icon={projects_icon}>
      <Stack
        sx={{
          width: "100%",
          justifyContent: "center",
          alignItems: "center",
          marginTop: "5%",
        }}
      >
        <Stack
          sx={{
            minWidth: "600px",
            maxWidth: "600px",
            gap: "16px",
          }}
        >
          <Typography variant="h1">Create a New Project</Typography>

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
            placeholder="What are the main themes around financial priorities that the interviewees expect to have at retirement? Are interviewees with lower debt levels more likely to contribute to their 401(k)?"
            name="questions"
            error={errors.questions}
            size="small"
            multiline
          />

          <LabelInputCombo
            label="Members"
            inputDescription="Comma-separated list of emails of people you would like to include in this project."
            onChange={handleChange}
            value={state.members}
            placeholder="example1@corp.com,example2@corp.com"
            name="members"
            error={errors.members}
            size="small"
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
            >
              Cancel
            </Button>
          </Stack>
        </Stack>
      </Stack>
    </PrivateContainer>
  );
}
