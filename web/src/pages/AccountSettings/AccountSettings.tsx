import { Box, Button, InputLabel, Stack, Typography } from "@mui/material";
import { settings_icon } from "../../assets/icons/svg";
import { PrivateContainer } from "../../components/Containers";
import { TextInputL } from "../../components/atoms";
import useAccountSettings from "./useAccountSettings";

interface LabelInputPairProps {
  label: string;
  onChange: () => void;
  value: string;
  placeholder: string;
}

const LabelInputPair = (props: LabelInputPairProps) => {
  const { label, onChange, value, placeholder } = props;
  return (
    <Stack spacing={2}>
      <InputLabel htmlFor={label}>{label}</InputLabel>
      <TextInputL onChange={onChange} value={value} placeholder={placeholder} />
    </Stack>
  );
};

export default function AccountSettings() {
  const { errors, handleChange, handleSave, state } = useAccountSettings();
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
            value=""
            placeholder="Name"
          />

          <LabelInputPair
            label="Primary Email"
            onChange={handleChange}
            value=""
            placeholder="john@example.com"
          />

          <LabelInputPair
            label="Old Password"
            onChange={handleChange}
            value=""
            placeholder="Old Password"
          />

          <LabelInputPair
            label="New Password"
            onChange={handleChange}
            value=""
            placeholder="New Password"
          />

          <Stack sx={{ flexDirection: "row", gap: "12px" }}>
            <Button
              variant="contained"
              sx={{
                width: "100px",
              }}
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
