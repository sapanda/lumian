import { useContext } from "react";
import { GlobalContext } from "../context/GlobalContext";

interface User {
  email: string;
  name: string;
}

export default function useUser(): User {
  const { state } = useContext(GlobalContext);
  let storageUser = localStorage.getItem("user");
  storageUser = !!storageUser && JSON.parse(storageUser);
  const user = state.user || storageUser;

  if (!user) {
    return {
      email: "",
      name: "",
    };
  }
  return user;
}
