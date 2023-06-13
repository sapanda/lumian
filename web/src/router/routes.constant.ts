import {
  Login,
  ForgotPassword,
  PrivacyPolicy,
  TermsOfServices,
  ResetPassword,
  Projects,
  AccountSettings,
  Integrations,
} from "../pages";

// Public Routes
export const LOGIN = "/login";
export const FORGOT_PASSWORD = "/forgot-password";
export const RESET_PASSWORD = "/reset-password";
export const HOME = "/";
export const PRIVACY_POLICY = "/privacy-policy";
export const TERMS_OF_SERVICES = "/terms-of-services";
export const ACCOUNT_SETTINGS = "/account-settings";
export const INTEGRATIONS = "/integrations";

// Private Routes
export const PROJECTS = {
  default: "/all-projects",
  SELECTED_PROJECT: {
    default: "/project/:projectId",
    SELECTED_INTERVIEW: "/project/:projectId/interview/:interviewId",
  },
  CREATE_PROJECT: "/create-project",
  MANAGE_PROJECT: "/manage-project/:projectId",
};

export const PUBLIC_ROUTES = [
  {
    path: LOGIN,
    component: Login,
    exact: true,
  },

  {
    path: FORGOT_PASSWORD,
    component: ForgotPassword,
    exact: true,
  },
  {
    path: RESET_PASSWORD,
    component: ResetPassword,
    exact: true,
  },
  {
    path: HOME,
    component: Projects.AllProjects,
    exact: true,
  },
  {
    path: PRIVACY_POLICY,
    component: PrivacyPolicy,
    exact: true,
  },
  {
    path: TERMS_OF_SERVICES,
    component: TermsOfServices,
    exact: true,
  },
];

export const PRIVATE_ROUTES = [
  {
    path: PROJECTS.default,
    component: Projects.AllProjects,
    exact: true,
  },
  {
    path: PROJECTS.CREATE_PROJECT,
    component: Projects.CreateProject,
    exact: true,
  },
  {
    path: PROJECTS.MANAGE_PROJECT,
    component: Projects.CreateProject,
    exact: true,
  },
  {
    path: PROJECTS.SELECTED_PROJECT.default,
    component: Projects.SelectedProject.default,
    exact: true,
  },

  {
    path: PROJECTS.SELECTED_PROJECT.SELECTED_INTERVIEW,
    component: Projects.SelectedProject.SelectedInterview,
    exact: true,
  },

  {
    path: INTEGRATIONS,
    component: Integrations,
    exact: true,
  },
  {
    path: ACCOUNT_SETTINGS,
    component: AccountSettings,
    exact: true,
  },
];
