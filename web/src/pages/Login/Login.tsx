import { Button } from "@mui/material";
import { PublicContainer } from "../../components/Containers";
import useLogin from "./useLogin";
import { TextInputL } from "../../components/atoms";
import { email_icon, lock_icon } from "../../assets/icons/svg";

export default function Login() {
  const { email, password, setEmail, setPassword, handleLogin } = useLogin();
  return (
    <PublicContainer align="center">
      <div className="flex flex-row shadow-card rounded-2xl text-left overflow-hidden min-w-[700px] min-h-[400px] max-w-[700px] max-h-[400px]">
        <div className="flex flex-col p-8 min-w[60%]">
          <span className="text-24-700">Hello Again</span>

          <span className="text-gray-600 text-14-400">
            Synthesize your expert calls to make the most of your time.
          </span>

          <div className="flex flex-col gap-3 mt-5">
            <TextInputL
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              startIcon={{
                position: "start",
                content: <img className="w-5 h-5" src={email_icon} />,
              }}
              placeholder="Email"
            />
            <TextInputL
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              startIcon={{
                position: "start",
                content: (
                  <img
                    src={lock_icon}
                    style={{ width: "20px", height: "20px" }}
                  />
                ),
              }}
              type="password"
              placeholder="Password"
            />

            <Button variant="contained" onClick={() => handleLogin()}>
              Continue
            </Button>
          </div>

          <div className="flex flex-col justify-center min-h-[70px]">
            <p className="text-12-400">
              By using MetaNext you agree to the{" "}
              <span
                className="text-blue-500 cursor-pointer"
                onClick={() =>
                  window.open(
                    "https://metanext.notion.site/Terms-of-Service-c5c6b953067d4b138ee9d8b23b919734",
                    "_blank"
                  )
                }
              >
                Terms of Service
              </span>{" "}
              and{" "}
              <span
                className="text-blue-500 cursor-pointer"
                onClick={() =>
                  window.open(
                    "https://metanext.notion.site/Privacy-Policy-8efe42dc1ec14e4ba5dc5155455d3927",
                    "_blank"
                  )
                }
              >
                Privacy Policy
              </span>
            </p>
          </div>
        </div>

        <div className="flex flex-col items-center justify-center w-1/2 bg-blue-300">
          <div className="flex flex-col items-center justify-center text-center bg-white shadow-2xl rounded-2xl min-w-[170px] min-h-[160px] max-w-[170px]">
            <p className="text-16-500">
              Skip note-taking.
              <br />
              Focus on what matters.
            </p>
          </div>
        </div>
      </div>
    </PublicContainer>
  );
}
