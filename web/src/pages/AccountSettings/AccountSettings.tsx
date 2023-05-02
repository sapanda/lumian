import {
  Button,
  FormHelperText,
  InputLabel,
  Stack,
  Typography,
} from "@mui/material";
import { settings_icon } from "../../assets/icons/svg";
import { PrivateContainer } from "../../components/Containers";
import { TextInputL } from "../../components/atoms";
import useAccountSettings from "./useAccountSettings";
import useUser from "../../hooks/useUser";

interface LabelInputPairProps {
  error?: string;
  name?: string;
  label: string;
  onChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  value: string;
  placeholder: string;
}

const LabelInputPair = (props: LabelInputPairProps) => {
  const { label, onChange, value, placeholder, name, error } = props;
  return (
    <Stack spacing={2}>
      <InputLabel htmlFor={label}>{label}</InputLabel>
      <TextInputL
        onChange={onChange}
        value={value}
        placeholder={placeholder}
        name={name}
      />
      <FormHelperText error={!!error}>{error}</FormHelperText>
    </Stack>
  );
};

export default function AccountSettings() {
  const user = useUser();
  const { errors, handleChange, handleSave, state } = useAccountSettings({
    ...user,
    oldPassword: "",
    newPassword: "",
  });
  return (
    <PrivateContainer icon={settings_icon} title="Account Settings">
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
          <Typography variant="h1">Manage Account</Typography>

          <LabelInputPair
            label="Name"
            onChange={handleChange}
            value={state.name}
            placeholder="Name"
            name="name"
            error={errors.name}
          />

          <LabelInputPair
            label="Primary Email"
            onChange={handleChange}
            value={state.email}
            placeholder="john@example.com"
            name="email"
            error={errors.email}
          />

          <LabelInputPair
            label="Old Password"
            onChange={handleChange}
            value={state.oldPassword}
            placeholder="Old Password"
            name="oldPassword"
            error={errors.oldPassword}
          />

          <LabelInputPair
            label="New Password"
            onChange={handleChange}
            value={state.newPassword}
            placeholder="New Password"
            name="newPassword"
            error={errors.newPassword}
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
