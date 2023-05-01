import { useState } from "react";
import {
  authEndPoints,
  baseApiUrl,
  userEndPoints,
} from "../../api/apiEndpoints";
import { useNavigate } from "react-router-dom";
import { PRIVATE_ROUTES } from "../../router/routes.constant";
import { PROJECTS } from "../../router/routes.constant";

export default function useLogin() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  async function handleLogin() {
    const res = await fetch(baseApiUrl + authEndPoints.login, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email: email,
        password: password,
      }),
    });

    const data = await res.json();
    if (data.token) {
      localStorage.setItem("token", data.token);
      getUser();
    }
    return data;
  }

  async function getUser() {
    const res = await fetch(baseApiUrl + userEndPoints.me, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Token " + localStorage.getItem("token"),
      },
    });

    const data = await res.json();
    localStorage.setItem("user", JSON.stringify(data));

    navigate(PROJECTS);
    return data;
  }
  return { email, password, setEmail, setPassword, handleLogin };
}
