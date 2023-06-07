import { useNavigate } from "react-router-dom";

export default function useAuth() {
  const navigate = useNavigate();
  const isAuthenticated = localStorage.getItem("token");
  function handleLogout() {
    localStorage.clear();
    navigate("/login");
  }

  return { handleLogout, isAuthenticated };
}
