import { Button} from "@mui/material";
import { PublicContainer } from "../../components/Containers";
import useLogin from "./useLogin";
import { TextInputL } from "../../components/atoms";
import { email_icon, lock_icon } from "../../assets/icons/svg";

export default function Login() {
  const { email, password, setEmail, setPassword, handleLogin } = useLogin();
  return (
    <PublicContainer align="center">
      <div
        className="flex flex-row shadow-card rounded-2xl text-left overflow-hidden"
        style={{
          minWidth: "700px",
          minHeight: "400px",
          maxWidth: "700px",
          maxHeight: "400px",
        }}
      >
        <div
          className="flex flex-col p-8"
          style={{
            minWidth: "60%",
          }}
        >
          <span className="text-24700">Hello Again</span>

          <span className="text-14400 text-gray-600">
            Synthesize your expert calls to make the most of your time.
          </span>

          <div className="flex flex-col mt-5 gap-3">
            <TextInputL
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              startIcon={{
                position: "start",
                content: (
                  <img
                    src={email_icon}
                    style={{ width: "20px", height: "20px" }}
                  />
                ),
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

          <div
            className="flex flex-col justify-center"
            style={{
              minHeight: "70px",
            }}
          >
            <p className="text-12400">
              By using MetaNext you agree to the{" "}
              <span className="cursor-pointer text-blue-500">
                Terms of Service
              </span>{" "}
              and{" "}
              <span className="cursor-pointer text-blue-500">
                Privacy Policy
              </span>
            </p>
          </div>
        </div>

        <div className="flex flex-col justify-center items-center bg-blue-300 w-1/2">
          <div
            className="flex justify-center items-center bg-white rounded-2xl shadow-2xl flex-col text-center"
            style={{
              minHeight: "160px",
              minWidth: "170px",
              maxWidth: "170px",
            }}
          >
            <p className="text-16500">Some Promotion Message or Testimonial</p>
          </div>
        </div>
      </div>
    </PublicContainer>
  );
}
