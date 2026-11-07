import { MODES } from "../../constants/categories.js";
import "./Taskbar.css";

const BUTTONS = [
  { mode: MODES.CURRENT, label: "Current" },
  { mode: MODES.PLAN, label: "Plan" },
];

export default function Taskbar({ mode, onModeChange }) {
  return (
    <header className="taskbar">
      <span className="taskbar__brand">Finance Dashboard</span>
      <nav className="taskbar__actions">
        {BUTTONS.map((b) => (
          <button
            key={b.mode}
            type="button"
            className={`taskbar__btn ${mode === b.mode ? "is-active" : ""}`}
            aria-pressed={mode === b.mode}
            onClick={() => onModeChange(b.mode)}
          >
            {b.label}
          </button>
        ))}
      </nav>
    </header>
  );
}
