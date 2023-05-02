import { Stack, Typography } from "@mui/material";

export default function Header() {
  return (
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
  );
}
