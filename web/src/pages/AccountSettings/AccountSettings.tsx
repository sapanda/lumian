import { Button,  Typography } from "@mui/material";
import { settings_icon } from "../../assets/icons/svg";
import { PrivateContainer } from "../../components/Containers";
import useAccountSettings from "./useAccountSettings";
import useUser from "../../hooks/useUser";
import { LabelInputCombo } from "../../components/molecules";
import { PrivateAppbar } from "../../layout";

export default function AccountSettings() {
  const user = useUser();
  const { errors, handleChange, handleSave, state } = useAccountSettings({
    ...user,
    oldPassword: "",
    newPassword: "",
  });
  return (
    <PrivateContainer
      appBar={<PrivateAppbar icon={settings_icon} title="Account Settings" />}
    >
      <div className="w-full flex flex-col items-center justify-center mt-[10%]">
        <div className="flex flex-col min-w-[600px] max-w-[600px] gap-[20px]">
          <Typography variant="h1">Manage Account</Typography>

          <LabelInputCombo
            label="Name"
            onChange={handleChange}
            value={state.name}
            placeholder="Name"
            name="name"
            error={errors.name}
          />

          <LabelInputCombo
            label="Primary Email"
            onChange={handleChange}
            value={state.email}
            placeholder="john@example.com"
            name="email"
            error={errors.email}
          />

          <LabelInputCombo
            label="Old Password"
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

          <div className="flex gap-3">
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
          </div>
        </div>
      </div>
    </PrivateContainer>
  );
}
