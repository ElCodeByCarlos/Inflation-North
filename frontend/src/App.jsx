import { BrowserRouter, Route, Routes, useLocation, useNavigate } from "react-router";
import Taskbar from "./components/Taskbar/Taskbar.jsx";
import Dashboard from "./pages/Dashboard/Dashboard.jsx";
import { AccountDashboard } from "./pages/AccountDashboard/AccountDashboard.jsx";
import { MODES } from "./constants/categories.js";

function AppLayout() {
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const mode = pathname === "/plan" ? MODES.PLAN : MODES.CURRENT;

  return (
    <div className="app">
      <Taskbar
        mode={mode}
        onModeChange={(next) => navigate(next === MODES.PLAN ? "/plan" : "/")}
      />
      <main className="app__content">
        <Routes>
          <Route path="/" element={<Dashboard mode={MODES.CURRENT} />} />
          <Route path="/plan" element={<Dashboard mode={MODES.PLAN} />} />
          <Route path="/accounts/:accountId" element={<AccountDashboard />} />
        </Routes>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppLayout />
    </BrowserRouter>
  );
}
