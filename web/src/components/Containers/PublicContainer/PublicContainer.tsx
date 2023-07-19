import { useEffect, useState } from "react";
import { Backdrop, CircularProgress, Stack, Typography } from "@mui/material";
import { useNavigate } from "react-router-dom";
import { PROJECTS } from "../../../router/routes.constant";
import { useIsFetching, useIsMutating } from "@tanstack/react-query";

interface PublicContainerProps {
  children: React.ReactNode;
  bodyStyles?: React.CSSProperties;
  align?: "center" | "flex-start";
}
export default function PublicContainer(props: PublicContainerProps) {
  const { children, bodyStyles, align } = props;

  const navigate = useNavigate();
  const isFetching = useIsFetching();
  const isMutating = useIsMutating();
  const [isAuthReady, setIsAuthReady] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("token");
    const authenticated = !!token; // Check if token exists

    setIsAuthReady(true);
    if (location.pathname === "/404") return;

    if (authenticated) {
      navigate(PROJECTS.default);
    }
  }, [navigate]);

  const isLoading = isFetching > 0 || isMutating > 0;
  if (!isAuthReady) {
    // Render loading state or placeholder while verifying authentication status
    return <div></div>;
  }
  return (
    <Stack
      sx={{
        height: "66px",
      }}
    >
      <Stack
        sx={{
          flexDirection: "row",
          gap: "6px",
          marginTop: "40px",
          padding: "0px 40px",
        }}
      >
        <div
          style={{
            height: "39px",
          }}
        >
          <img src="/lumian.svg" alt="logo" />
        </div>
        <Typography variant="h1">Lumian</Typography>
      </Stack>
      {isLoading ? (
        <Backdrop
          sx={{ zIndex: (theme) => theme.zIndex.drawer + 999 }}
          open={isLoading}
        >
          <CircularProgress color="primary" />
        </Backdrop>
      ) : (
        <Stack
          sx={{
            justifyContent: align === "center" ? "center" : "flex-start",
            alignItems: "center",
            minHeight: `calc(100vh - 80px)`,
            padding: "40px",
            ...bodyStyles,
          }}
        >
          {children}
        </Stack>
      )}
    </Stack>
  );
}
