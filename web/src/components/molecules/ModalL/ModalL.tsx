import { Dialog, SxProps, Theme } from "@mui/material";

interface ModalLProps {
  children: React.ReactNode;
  open: boolean;
  handleClose: () => void;
  sx?: SxProps<Theme>;
  containerStyles?: React.CSSProperties;
}
export default function ModalL(props: ModalLProps) {
  const { children, open, handleClose, sx, containerStyles } = props;
  return (
    <Dialog
      fullWidth
      open={open}
      onClose={handleClose}
      sx={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        ".MuiDialog-paper": {
          padding: "20px",
          width: "100%",
          ...containerStyles,
        },
        ...sx,
      }}
    >
      {children}
    </Dialog>
  );
}
