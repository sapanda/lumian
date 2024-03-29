import { FormHelperText, InputLabel, Stack } from "@mui/material";
import { DescriptionText, TextInputL } from "../../atoms";

interface LabelInputPairProps {
  error?: string;
  name?: string;
  label: string;
  onChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  value: string;
  placeholder: string | string[];
  inputDescription?: string;
  type?: "text" | "password" | "email" | "number" | "tel" | "url";
  size?: "small" | "default";
  multiline?: boolean;
  isOptional?: boolean;
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
    isOptional = false,
  } = props;

  let finalPlaceholderText = "";
  if (Array.isArray(placeholder)) finalPlaceholderText = placeholder.join("\n");
  else finalPlaceholderText = placeholder;
  return (
    <Stack spacing={2}>
      <InputLabel
        htmlFor={label}
        sx={{
          fontWeight: "bold",
          fontSize: "12px",
        }}
      >
        {label}{" "}
        <span className="text-12-400">{isOptional && "(optional)"}</span>
      </InputLabel>
      {!!inputDescription && (
        <DescriptionText>{inputDescription}</DescriptionText>
      )}
      <TextInputL
        onChange={onChange}
        value={value}
        placeholder={finalPlaceholderText}
        name={name}
        type={type}
        size={size}
        multiline={multiline}
        sx={{
          "& .MuiInputBase-input": {
            padding: "8px 14px",
          },

          "& .MuiOutlinedInput-root": {
            borderRadius: "8px",
            padding: "0",
            ...(size === "small" && {
              height: "30px",
            }),

            ...(multiline && {
              height: "126px",
            }),

            "& fieldset": {
              borderColor: "#CFCECE",
            },
            "&:hover fieldset": {
              borderColor: "#CFCECE",
            },
            "&.Mui-focused fieldset": {
              borderColor: "#CFCECE",
            },
          },
        }}
      />
      {!!error && <FormHelperText error={!!error}>{error}</FormHelperText>}
    </Stack>
  );
};

export default LabelInputCombo;
