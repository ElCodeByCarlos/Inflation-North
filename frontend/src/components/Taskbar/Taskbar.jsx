import { MODES } from "../../constants/categories.js";
import AccountPicker from "../AccountPicker/AccountPicker.jsx";
import "./Taskbar.css";

const BUTTONS = [
  { mode: MODES.CURRENT, label: "Current" },
  { mode: MODES.PLAN, label: "Plan" },
];

export default function Taskbar({ mode, onModeChange, accounts, accountId, onAccountChange }) {
  return (
    <header className="taskbar">
      <div className="taskbar__inner">
        <div className="taskbar__brand">
          <span className="taskbar__name">Financial North</span>
          <span className="taskbar__tagline">Finance, Security, Stability</span>
        </div>
        <div className="taskbar__controls">
          {accounts.length > 0 && (
            <AccountPicker accounts={accounts} accountId={accountId} onChange={onAccountChange} />
          )}
        </div>
        <nav className="taskbar__actions" aria-label="Dashboard mode">
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
      </div>
    </header>
  );
}
