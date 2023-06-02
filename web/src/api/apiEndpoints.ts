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
  oauthUrl: "api/meeting/calendar/oauth-request",
  initiateTranscription: "api/meeting/initiate-transcription",
  accessToken: "api/meeting/calendar/oauth-response",
};

export {
  authEndPoints,
  userEndPoints,
  interviewEndPoints,
  projectEndpoints,
  meetingEndPoints,
};
