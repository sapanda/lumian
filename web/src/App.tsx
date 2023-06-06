import { ThemeProvider } from "@emotion/react";
import theme from "./theme";
import Router from "./router";
import GlobalProvider from "./context/GlobalContext";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.min.css";

function App() {
  return (
    <GlobalProvider>
      <ThemeProvider theme={theme}>
        <Router />
        <ToastContainer position="top-center" autoClose={5000} />
      </ThemeProvider>
    </GlobalProvider>
  );
}

export default App;
