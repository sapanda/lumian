import { InputAdornment, SxProps, TextField } from "@mui/material";

interface TextInputLProps {
  name?: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  startIcon?: {
    position: "start" | "end";
    content: React.ReactNode;
  };
  endIcon?: {
    position: "start" | "end";
    content: React.ReactNode;
  };
  variant?: "standard" | "filled" | "outlined";
  type?: "text" | "password" | "email" | "number" | "tel" | "url";
  placeholder?: string;
  size?: "small" | "default";
  multiline?: boolean;
  sx?: SxProps;
}
export default function TextInputL(props: TextInputLProps) {
  const {
    value,
    onChange,
    startIcon,
    endIcon,
    type,
    placeholder,
    name,
    sx,
    size = "default",
    multiline = false,
  } = props;

  return (
    <TextField
      sx={{
        marginTop: "8px!important",

        "& .MuiOutlinedInput-root": {
          borderRadius: "6px",
          ...(size === "small" && {
            height: "32px",
          }),

          ...(multiline && {
            height: "126px",
          }),

          "& fieldset": {
            borderColor: "#707070",
          },
          "&:hover fieldset": {
            borderColor: "#707070",
          },
          "&.Mui-focused fieldset": {
            borderColor: "#707070",
          },
        },

        ...sx,
      }}
      InputProps={{
        startAdornment: (
          <InputAdornment position={startIcon?.position ?? "end"}>
            {startIcon?.content}
          </InputAdornment>
        ),
        endAdornment: (
          <InputAdornment position={endIcon?.position ?? "end"}>
            {endIcon?.content}
          </InputAdornment>
        ),
      }}
      placeholder={placeholder}
      variant="outlined"
      value={value}
      onChange={onChange}
      type={type ?? "text"}
      name={name}
      {...(multiline && {
        multiline: true,
        rows: 4,
      })}
    />
  );
}
