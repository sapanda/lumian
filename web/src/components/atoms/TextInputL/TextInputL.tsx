import { InputAdornment, TextField } from "@mui/material";

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
}
export default function TextInputL(props: TextInputLProps) {
  const { value, onChange, startIcon, endIcon, type, placeholder, name } =
    props;
  return (
    <TextField
      sx={{
        marginTop: "8px!important",

        "& .MuiOutlinedInput-root": {
          borderRadius: "6px",

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
    />
  );
}
