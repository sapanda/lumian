import { Stack, Typography } from "@mui/material";

interface PublicContainerProps {
  children: React.ReactNode;
  bodyStyles?: React.CSSProperties;
  align?: "center" | "flex-start";
}
export default function PublicContainer(props: PublicContainerProps) {
  const { children, bodyStyles, align } = props;
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
    </Stack>
  );
}
