import { useState } from "react";
import { BrowserRouter, Route, Routes } from "react-router"
import Taskbar from "./components/Taskbar/Taskbar.jsx";
import Dashboard from "./pages/Dashboard/Dashboard.jsx";
import { MODES } from "./constants/categories.js";

export default function App() {
  const [mode, setMode] = useState(MODES.CURRENT);

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard mode={mode} />} />
        <Route path="/plan" element={<Dashboard mode={MODES.PLAN} />} />
        <Route path="/accounts/:accountId" element={<AccountDashboard />} />
      </Routes>
    </BrowserRouter>

  );
}
