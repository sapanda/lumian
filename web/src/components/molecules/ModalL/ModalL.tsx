import { Dialog, SxProps, Theme } from "@mui/material";

interface ModalLProps {
  children: React.ReactNode;
  open: boolean;
  handleClose: () => void;
  sx?: SxProps<Theme>;
}
export default function ModalL(props: ModalLProps) {
  const { children, open, handleClose, sx } = props;
  return (
    <Dialog
      fullWidth
      open={open}
      onClose={handleClose}
      sx={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",

        ...sx,
      }}
    >
      {children}
    </Dialog>
  );
}
