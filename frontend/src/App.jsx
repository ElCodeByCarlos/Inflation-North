import { useState } from "react";
import Taskbar from "./components/Taskbar/Taskbar.jsx";
import Dashboard from "./pages/Dashboard/Dashboard.jsx";
import { MODES } from "./constants/categories.js";

export default function App() {
  const [mode, setMode] = useState(MODES.CURRENT);

  return (
    <div className="app">
      <Taskbar mode={mode} onModeChange={setMode} />
      <main className="app__content">
        <Dashboard mode={mode} />
      </main>
    </div>
  );
}
