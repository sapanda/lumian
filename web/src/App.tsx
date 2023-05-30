import { ThemeProvider } from "@emotion/react";
import theme from "./theme";
import Router from "./router";
import GlobalProvider from "./context/GlobalContext";

function App() {
  return (
    <GlobalProvider>
      <ThemeProvider theme={theme}>
        <Router />
      </ThemeProvider>
    </GlobalProvider>
  );
}

export default App;
