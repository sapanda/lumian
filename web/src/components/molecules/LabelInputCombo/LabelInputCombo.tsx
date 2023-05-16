import { FormHelperText, InputLabel, Stack } from "@mui/material";
import { DescriptionText, TextInputL } from "../../atoms";

interface LabelInputPairProps {
  error?: string;
  name?: string;
  label: string;
  onChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  value: string;
  placeholder: string;
  inputDescription?: string;
  type?: "text" | "password" | "email" | "number" | "tel" | "url";
  size?: "small" | "default";
  multiline?: boolean;
}

const LabelInputCombo = (props: LabelInputPairProps) => {
  const {
    label,
    onChange,
    value,
    placeholder,
    name,
    error,
    inputDescription,
    type,
    size = "default",
    multiline = false,
  } = props;
  return (
    <Stack spacing={2}>
      <InputLabel
        htmlFor={label}
        sx={{
          fontWeight: "bold",
          fontSize: "12px",
        }}
      >
        {label}
      </InputLabel>
      {!!inputDescription && (
        <DescriptionText>{inputDescription}</DescriptionText>
      )}
      <TextInputL
        onChange={onChange}
        value={value}
        placeholder={placeholder}
        name={name}
        type={type}
        size={size}
        multiline={multiline}
      />
      <FormHelperText error={!!error}>{error}</FormHelperText>
    </Stack>
  );
};

export default LabelInputCombo;
