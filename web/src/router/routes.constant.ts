import {
  Login,
  ForgotPassword,
  PrivacyPolicy,
  TermsOfServices,
  ResetPassword,
  Projects,
} from "../pages";

// Public Routes
export const LOGIN = "/login";
export const FORGOT_PASSWORD = "/forgot-password";
export const RESET_PASSWORD = "/reset-password";
export const HOME = "/";
export const PRIVACY_POLICY = "/privacy-policy";
export const TERMS_OF_SERVICES = "/terms-of-services";

// Private Routes
export const PROJECTS = "/projects";

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
    component: Login,
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
    path: PROJECTS,
    component: Projects,
    exact: true,
  },
];