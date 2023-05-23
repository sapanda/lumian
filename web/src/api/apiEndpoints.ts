const baseApiUrl = import.meta.env.VITE_API_URL as string;

console.log("baseApiUrl", baseApiUrl);
const authEndPoints = {
  login: "api/user/token/",
};

const userEndPoints = {
  me: "api/user/me/",
};

const projectEndpoints = {
  projectList: "api/projects/",
  projectDetail: "api/projects/:projectId/",
};

const interviewEndPoints = {
  interviewTranscipt: "api/transcripts/:interviewId/",
  interviewList: "api/transcripts/?project=:projectId",
  interviewSummary: "api/transcripts/:interviewId/summary/",
  interviewConcise: "api/transcripts/:interviewId/concise/",
  interviewQuery: "api/transcripts/:interviewId/query/",
};

const meetingEndPoints = {
  oauthUrl: "/api/meeting/oauth-url",
  initiateTranscription: "api/meeting/initiate-transcription",
  accessToken: "api/meeting/access-token",
};

export {
  baseApiUrl,
  authEndPoints,
  userEndPoints,
  interviewEndPoints,
  projectEndpoints,
  meetingEndPoints,
};
