import Box from "@mui/material/Box";
import CssBaseline from "@mui/material/CssBaseline";

import { PrivateAppbar, Sidebar } from "../../../layout";
import { Toolbar } from "@mui/material";

interface PrivateContainerProps {
  children: React.ReactNode;
  title: string;
  icon: string;
}
export default function PrivateContainer(props: PrivateContainerProps) {
  const { children, title, icon } = props;
  return (
    <Box sx={{ display: "flex" }}>
      <CssBaseline />
      <PrivateAppbar title={title} icon={icon} />
      <Sidebar />
      <Box
        component="main"
        sx={{ flexGrow: 1, bgcolor: "background.default", p: 1 }}
      >
        <Toolbar />
        {children}
      </Box>
    </Box>
  );
}
