import { userEndPoints } from "./apiEndpoints";
import { axiosInstance } from "./api";
import {
  QueryKey,
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

interface UpdateMePayload {
  email?: string;
  name?: string;
  password?: string;
  botName?: string;
}

const getMe = async () => {
  const res = await axiosInstance.get(`${userEndPoints.me}`);
  return res.data.data;
};

const updateMe = async (payload: UpdateMePayload) => {
  const res = await axiosInstance.patch(`${userEndPoints.me}`, payload);
  return res.data.data;
};

const useGetMeQuery = () => {
  const queryKey: QueryKey = ["me"];
  return useQuery(queryKey, getMe, {
    staleTime: 1000 * 60 * 30, // 30 minutes
  });
};

const useUpdateMeMutation = () => {
  const queryClient = useQueryClient();
  return useMutation((payload: UpdateMePayload) => updateMe(payload), {
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["me"],
      });
    },
  });
};

export { useGetMeQuery, useUpdateMeMutation };
