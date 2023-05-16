const baseApiUrl = import.meta.env.VITE_API_URL as string;

console.log("baseApiUrl", baseApiUrl);
const authEndPoints = {
  login: "api/user/token/",
};

const userEndPoints = {
  me: "api/user/me/",
};

const interviewEndPoints = {
  interviewList: "api/transcript/transcripts/",
};
export { baseApiUrl, authEndPoints, userEndPoints, interviewEndPoints };
