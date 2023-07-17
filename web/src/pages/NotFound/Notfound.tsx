import { useEffect } from "react";
import { PublicContainer } from "../../components/Containers";
import { useNavigate } from "react-router-dom";
import { Button } from "@mui/material";
// import NotFoundIllustration from "../../../public/404.png"
export default function Notfound() {
  const navigate = useNavigate();
  useEffect(() => {
    const location = window.location;
    const path = location.pathname;
    if (path !== "/404") navigate("/404");
  }, [navigate]);
  return (
    <PublicContainer>
      <img src="/404.png" alt="404" className="w-full max-w-[700px]" />
      <Button
        variant="contained"
        onClick={() => navigate("/")}
        sx={{
          marginTop: "40px",
        }}
      >
        Go to Home
      </Button>
    </PublicContainer>
  );
}
