import { Button, Stack, TextField, Typography } from "@mui/material";
import { PublicContainer } from "../../components/Containers";
import useLogin from "./useLogin";

export default function Login() {
  const { email, password, setEmail, setPassword, handleLogin } = useLogin();
  return (
    <PublicContainer align="center">
      <Stack
        sx={{
          flexDirection: "row",
          boxShadow: "0px 4px 40px rgba(0, 0, 0, 0.2)",
          borderRadius: "32px",
          minWidth: "700px",
          minHeight: "400px",
          maxWidth: "700px",
          maxHeight: "400px",
          textAlign: "left",
          overflow: "hidden",
        }}
      >
        <Stack
          sx={{
            minWidth: "60%",
            padding: "32px",
          }}
        >
          <Typography variant="h1">Hello Again</Typography>
          <Typography variant="body1">
            Synthesize your expert calls to make the most of your time.
          </Typography>
          <Stack sx={{ marginTop: "32px", gap: "10px" }}>
            <TextField
              label="Email"
              variant="outlined"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <TextField
              type="password"
              label="Password"
              variant="outlined"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <Button variant="contained" onClick={() => handleLogin()}>
              Continue
            </Button>
          </Stack>
          <Stack
            sx={{
              justifyContent: "center",
              minHeight: "70px",
            }}
          >
            <Typography variant="body1">
              By using MetaNext you agree to the{" "}
              <span style={{ color: "#0268C6", cursor: "pointer" }}>
                Terms of Service
              </span>{" "}
              and{" "}
              <span style={{ color: "#0268C6", cursor: "pointer" }}>
                Privacy Policy
              </span>
            </Typography>
          </Stack>
        </Stack>
        <Stack
          sx={{
            justifyContent: "center",
            alignItems: "center",
            backgroundColor: "#58A0E2",
            minWidth: "40%",
          }}
        >
          <Stack
            sx={{
              boxShadow: "0px 4px 40px rgba(0, 0, 0, 0.1)",
              borderRadius: "10px",
              padding: "8px",
              backgroundColor: "#FAFAFA",
              minHeight: "160px",
              minWidth: "170px",
              maxWidth: "170px",
              justifyContent: "center",
              alignItems: "center",
              textAlign: "center",
            }}
          >
            <Typography variant="h4">
              Some Promotion Message or Testimonial
            </Typography>
          </Stack>
        </Stack>
      </Stack>
    </PublicContainer>
  );
}
