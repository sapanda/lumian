import { TextField } from "@mui/material";
import React from "react";
import SendIcon from "@mui/icons-material/Send";

interface TextInputLProps {
  name?: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onSend: () => void;
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
}

export default function QueryInput(props: TextInputLProps) {
  const { value, onChange, placeholder, name, onSend } = props;

  return (
    <TextField
      sx={{
        marginTop: "8px!important",
        background: "#FAFAFA",
        boxShadow: "0px 0px 6px rgba(0, 0, 0, 0.25)",
        borderRadius: "10px",
        "& .MuiOutlinedInput-root": {
          borderRadius: "6px",
          "& fieldset": {
            border: "none",
          },

          "& textarea": {
            scrollbarWidth: "none",
            "&::-webkit-scrollbar": {
              display: "none",
            },
          },
        },
      }}
      InputProps={{
        endAdornment: (
          <SendIcon
            sx={{ color: "#707070", cursor: "pointer" }}
            onClick={onSend}
          />
        ),
      }}
      placeholder={placeholder}
      variant="outlined"
      value={value}
      onChange={onChange}
      name={name}
      maxRows={5}
      multiline
    />
  );
}
