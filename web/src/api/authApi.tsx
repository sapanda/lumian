import { baseApiUrl, authEndPoints } from "./apiEndpoints";
import { axiosInstance } from "./api";
import { useMutation, useQueryClient } from "@tanstack/react-query";

interface LoginResponse {
  token: string;
}
interface LoginParams {
  email: string;
  password: string;
}

const login = async (credentials: LoginParams) => {
  const response = await axiosInstance.post<LoginResponse>(
    `${baseApiUrl}${authEndPoints.login}`,
    credentials
  );
  return response.data;
};

const useLoginMutation = (credentials: LoginParams) => {
  const queryClient = useQueryClient();
  return useMutation(() => login(credentials), {
    onSuccess: (data) => {
      localStorage.setItem("token", data.token);
      queryClient.invalidateQueries({
        queryKey: ["me"],
      });
    },
  });
};
export { useLoginMutation };
