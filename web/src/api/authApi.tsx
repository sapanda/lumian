import { authEndPoints } from "./apiEndpoints";
import { axiosInstance } from "./api";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { PROJECTS } from "../router/routes.constant";

interface LoginResponse {
  token: string;
}
interface LoginParams {
  email: string;
  password: string;
}

const login = async (credentials: LoginParams) => {
  const response = await axiosInstance.post<LoginResponse>(
    `${authEndPoints.login}`,
    credentials
  );
  return response.data;
};

const useLoginMutation = (credentials: LoginParams) => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  return useMutation(() => login(credentials), {
    onSuccess: (data) => {
      localStorage.setItem("token", data.token);
      queryClient.invalidateQueries({
        queryKey: ["me"],
      });
      navigate(PROJECTS.default);
    },
  });
};
export { useLoginMutation };
