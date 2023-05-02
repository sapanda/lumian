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
          marginTop: "10%",
        }}
      >
        <Stack
          sx={{
            minWidth: "600px",
            maxWidth: "600px",
            gap: "20px",
          }}
        >
          <Typography variant="h1">Create a New Project</Typography>

          <LabelInputCombo
            label="Name"
            onChange={handleChange}
            value={state.name}
            placeholder="Name of the Project"
            name="name"
            error={errors.name}
          />

          <LabelInputCombo
            label="Goal"
            inputDescription="Describe briefly what you’re looking to achieve with the project"
            onChange={handleChange}
            value={state.email}
            placeholder=""
            name="goal"
            error={errors.email}
          />

          <LabelInputCombo
            label="Old Password"
            inputDescription="These are the questions you’d like us to answer for you. List each question on a new line."
            onChange={handleChange}
            value={state.oldPassword}
            placeholder="Old Password"
            name="oldPassword"
            error={errors.oldPassword}
            type="password"
          />

          <LabelInputCombo
            label="New Password"
            onChange={handleChange}
            value={state.newPassword}
            placeholder="New Password"
            name="newPassword"
            error={errors.newPassword}
            type="password"
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
