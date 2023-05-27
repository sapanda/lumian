import { useState } from "react";

import { useLoginMutation } from "../../api/authApi";

export default function useLogin() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const { mutate: login } = useLoginMutation({ email, password });

  async function handleLogin() {
    login();
  }

  return { email, password, setEmail, setPassword, handleLogin };
}
