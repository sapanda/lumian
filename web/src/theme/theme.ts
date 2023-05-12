import { createTheme } from "@mui/material/styles";

const theme = createTheme({
  palette: {
    primary: {
      light: "#127fe42b",
      main: "#127FE4",
      dark: "#0A5E9D",
    },
    secondary: {
      main: "#0268C6",
    },
    error: {
      main: "#f44336",
    },
    warning: {
      main: "#ff9800",
    },
    info: {
      main: "#2196f3",
    },
    success: {
      main: "#4caf50",
    },
    text: {
      primary: "#000000",
      secondary: "#707070",
      disabled: "#9B9B9B",
    },

    common: {
      black: "#000",
      white: "#fff",
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: "none",
        },
      },
    },
  },
  typography: {
    fontFamily: "Roboto, sans-serif",

    h1: {
      fontSize: "24px",
      fontWeight: 700,
      lineHeight: "28px",
      letterSpacing: "0.25px",
      color: "#212121",
    },
    h2: {
      fontSize: "20px",
      fontWeight: 700,
      lineHeight: "24px",
      letterSpacing: "0.25px",
      color: "#212121",
    },
    h3: {
      fontSize: "18px",
      fontWeight: 700,
      lineHeight: "22px",
      letterSpacing: "0.25px",
      color: "#212121",
    },
    h4: {
      fontSize: "16px",
      fontWeight: 700,
      lineHeight: "20px",
      letterSpacing: "0.25px",
      color: "#212121",
    },
    h5: {
      fontSize: "14px",
      fontWeight: 700,
      lineHeight: "18px",
      letterSpacing: "0.25px",
      color: "#212121",
    },
    h6: {
      fontSize: "12px",
      fontWeight: 700,
      lineHeight: "16px",
      letterSpacing: "0.25px",
      color: "#212121",
    },
    body1: {
      fontSize: "14px",
      fontWeight: 400,
      lineHeight: "18px",
      color: "#5B5B5B",
    },
    body2: {
      fontSize: "12px",
      fontWeight: 400,
      lineHeight: "16px",
    },
    fontWeightBold: 700,
    fontWeightMedium: 500,
    fontWeightRegular: 400,
    fontWeightLight: 300,
  },
});

export default theme;
