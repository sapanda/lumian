interface User {
  email: string;
  name: string;
}

export default function useUser(): User {
  const user = localStorage.getItem("user");
  if (!user) {
    return {
      email: "",
      name: "",
    };
  }
  return JSON.parse(user);
}
