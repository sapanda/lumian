import { BrowserRouter, Routes, Route } from "react-router-dom";
import { PRIVATE_ROUTES, PUBLIC_ROUTES } from "./routes.constant";
import { Notfound } from "../pages";

export default function Router() {
  return (
    <BrowserRouter>
      <Routes>
        {PUBLIC_ROUTES.map((route) => (
          <Route
            key={route.path}
            path={route.path}
            element={<route.component />}
          />
        ))}

        {PRIVATE_ROUTES.map((route) => (
          <Route
            key={route.path}
            path={route.path}
            element={<route.component />}
          />
        ))}

        <Route path="*" element={<Notfound />} />
      </Routes>
    </BrowserRouter>
  );
}
