import { useEffect } from "react";
import Box from "@mui/material/Box";
import CssBaseline from "@mui/material/CssBaseline";

import { Sidebar } from "../../../layout";
import { Backdrop, CircularProgress, Toolbar } from "@mui/material";
import useAuth from "../../../hooks/useAuth";
import { useIsFetching, useIsMutating } from "@tanstack/react-query";

interface PrivateContainerProps {
  children: React.ReactNode;
  appBar: React.ReactNode;
}
export default function PrivateContainer(props: PrivateContainerProps) {
  const { children, appBar } = props;
  const { isAuthenticated, handleLogout } = useAuth();
  const isFetching = useIsFetching();
  const isMutating = useIsMutating();

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
      {appBar}
      <Sidebar />
      <Box
        component="main"
        sx={{ flexGrow: 1, bgcolor: "background.default", p: 1 }}
      >
        <Toolbar />
        {children}
      </Box>
      <Backdrop
        sx={{ zIndex: (theme) => theme.zIndex.drawer + 999 }}
        open={isFetching > 0 || isMutating > 0}
      >
        <CircularProgress color="primary" />
      </Backdrop>
    </Box>
  );
}
