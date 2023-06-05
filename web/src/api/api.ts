import axios from "axios";
import { toast } from "react-toastify";

const baseApiUrl = import.meta.env.VITE_API_URL as string;
const axiosInstance = axios.create({
  baseURL: baseApiUrl,
  headers: {
    "Content-Type": "application/json",
  },
});

axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers["Authorization"] = `Token ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

axiosInstance.interceptors.response.use(
  (response) => {
    console.log(response);
    if (response.status === 201) {
      toast.success(response.statusText);
    } else if (response.status === 401) {
      toast.error("Unauthorized");
      localStorage.removeItem("token");
      window.location.href = "/";
    }
    return response;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export { axiosInstance };
