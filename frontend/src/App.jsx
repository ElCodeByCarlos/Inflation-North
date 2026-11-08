import { useEffect, useState } from "react";
import Taskbar from "./components/Taskbar/Taskbar.jsx";
import Dashboard from "./pages/Dashboard/Dashboard.jsx";
import { MODES } from "./constants/categories.js";
import { fetchAccounts } from "./services/api.js";

export default function App() {
  const [mode, setMode] = useState(MODES.CURRENT);
  const [accounts, setAccounts] = useState([]);
  const [accountId, setAccountId] = useState(null);

  useEffect(() => {
    fetchAccounts()
      .then((list) => {
        setAccounts(list);
        if (list.length > 0) setAccountId(list[0].account_id);
      })
      .catch(() => setAccounts([])); // backend offline: picker hidden, Dashboard shows fallback
  }, []);

  return (
    <div className="app">
      <Taskbar
        mode={mode}
        onModeChange={setMode}
        accounts={accounts}
        accountId={accountId}
        onAccountChange={setAccountId}
      />
      <main className="app__content">
        <Dashboard mode={mode} accountId={accountId} />
      </main>
    </div>
  );
}
