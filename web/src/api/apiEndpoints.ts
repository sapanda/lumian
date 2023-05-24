const baseApiUrl = import.meta.env.VITE_API_URL as string;

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
export {
  baseApiUrl,
  authEndPoints,
  userEndPoints,
  interviewEndPoints,
  projectEndpoints,
};
