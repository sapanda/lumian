import { Typography } from "@mui/material";

interface DescriptionTextProps {
  children?: React.ReactNode;
}
export default function DescriptionText({ children }: DescriptionTextProps) {
  return (
    <Typography
      component="span"
      sx={{
        marginTop: "4px!important",
        fontSize: "12px",
        fontWeight: 400,
      }}
    >
      <i>{children}</i>
    </Typography>
  );
}
