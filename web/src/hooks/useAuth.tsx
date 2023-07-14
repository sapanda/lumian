import { useNavigate } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
export default function useAuth() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const isAuthenticated = localStorage.getItem("token");
  function handleLogout() {
    localStorage.clear();
    queryClient.clear();
    navigate("/");
  }

  return { handleLogout, isAuthenticated };
}
