import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Login } from "../pages";

export default function Router() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="*" element={<h2>Not found </h2>} />
      </Routes>
    </BrowserRouter>
  );
}
