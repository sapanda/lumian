import axios from "axios";

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
    if (response.status === 401) {
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
    return response;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export { axiosInstance };
