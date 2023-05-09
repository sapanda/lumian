const baseApiUrl = import.meta.env.VITE_API_URL as string;

console.log("baseApiUrl", baseApiUrl);
const authEndPoints = {
  login: "api/user/token/",
};

const userEndPoints = {
  me: "api/user/me/",
};

const interviewEndPoints = {
  interviewTranscipt: "api/transcript/transcripts/:interviewId/",
  interviewList: "api/transcript/transcripts/",
  interviewSummary: "api/transcript/transcripts/:interviewId/summary/",
  interviewConcise: "api/transcript/transcripts/:interviewId/concise/",
  interviewQuery: "api/transcript/transcripts/:interviewId/query/",
};
export { baseApiUrl, authEndPoints, userEndPoints, interviewEndPoints };
