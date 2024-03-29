import axios from "axios";
import { toast } from "react-toastify";

const baseApiUrl = import.meta.env.VITE_API_URL as string;

const axiosInstanceHoc = (showToastDisabled = false) => {
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
      const msg = response.data.message;

      if (showToastDisabled || !msg) {
        return response;
      }
      toast.success(msg, {
        style: {
          backgroundColor: "#00b300",
          color: "#fff",
          fill: "#fff",
        },
        theme: "colored",
      });

      return response;
    },
    (error) => {
      if (error.response.status === 400) {
        toast.error(error.response.statusText, {
          style: {
            backgroundColor: "#ff0000",
            color: "#fff",
            fill: "#fff",
          },
          theme: "colored",
          toastId: "unauthorized",
        });
      } else if (error.response.status === 401) {
        toast.error("Unauthorized", {
          style: {
            backgroundColor: "#ff0000",
            color: "#fff",
            fill: "#fff",
          },
          theme: "colored",
          toastId: "unauthorized",
        });
        localStorage.removeItem("token");
        window.location.href = "/";
      }

      return Promise.reject(error);
    }
  );

  return axiosInstance;
};
const axiosInstance = axiosInstanceHoc();

export { axiosInstance, axiosInstanceHoc };
