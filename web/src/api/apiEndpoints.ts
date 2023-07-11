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
  transcript: "api/transcripts/",
  interviewTranscipt: "api/transcripts/:interviewId/",
  interviewList: "api/transcripts/?project=:projectId",
  interviewSummary: "api/transcripts/:interviewId/summary/",
  interviewConcise: "api/transcripts/:interviewId/concise/",
  interviewQuery:
    "api/transcripts/:interviewId/query/?query_level=:query_level",
};

const meetingEndPoints = {
  oauthUrl: "api/meeting/calendar/oauth-request",
  initiateTranscription: "api/meeting/initiate-transcription",
  accessToken: "api/meeting/calendar/oauth-response",
  calendarStatus: "api/meeting/calendar/status",
  meetingsList: "api/meeting/calendar/meetings?app=google",
  addBotToMeeting: "/api/meeting/bot/add",
  removeBotFromMeeting: "/api/meeting/bot/delete",
  removeCalendar: "/api/meeting/calendar/delete",
};

export {
  authEndPoints,
  userEndPoints,
  interviewEndPoints,
  projectEndpoints,
  meetingEndPoints,
};
