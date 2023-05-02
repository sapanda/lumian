import { useEffect } from "react";
import Box from "@mui/material/Box";
import CssBaseline from "@mui/material/CssBaseline";

import { PrivateAppbar, Sidebar } from "../../../layout";
import { Toolbar } from "@mui/material";
import useAuth from "../../../hooks/useAuth";

interface PrivateContainerProps {
  children: React.ReactNode;
  title: string;
  icon: string;
}
export default function PrivateContainer(props: PrivateContainerProps) {
  const { children, title, icon } = props;
  const { isAuthenticated, handleLogout } = useAuth();

  useEffect(() => {
    if (!isAuthenticated) {
      handleLogout();
    }
  }, [isAuthenticated, handleLogout]);

  return (
    <Box
      sx={{ display: "flex", height: "100%", minHeight: "calc(100vh - 65px)" }}
    >
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
