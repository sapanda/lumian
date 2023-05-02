const baseApiUrl = import.meta.env.VITE_API_URL as string;

const authEndPoints = {
  login: "api/user/token/",
};

const userEndPoints = {
  me: "api/user/me/",
};

export { baseApiUrl, authEndPoints, userEndPoints };
