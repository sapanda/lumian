import { Button } from "@mui/material";

interface Props {
  children: React.ReactNode;
  onClick: () => void;
  sx?: object;
}
export default function Buttons(props: Props) {
  const { children, onClick, sx } = props;
  return <Button sx={{ ...sx }}></Button>;
}
