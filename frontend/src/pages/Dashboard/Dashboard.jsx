import { useEffect, useState } from "react";
import CategoryCard from "../../components/CategoryCard/CategoryCard.jsx";
import AiInsights from "../../components/AiInsights/AiInsights.jsx";
import AccountDetails from "../../components/AccountDetails/AccountDetails.jsx";
import ScenarioForm from "../../components/ScenarioForm/ScenarioForm.jsx";
import { fetchDashboard } from "../../services/api.js";
import { FALLBACK_CATEGORIES, MODES } from "../../constants/categories.js";
import "./Dashboard.css";

export default function Dashboard({ mode, accountId }) {
  const [categories, setCategories] = useState(FALLBACK_CATEGORIES);
  const [month, setMonth] = useState(null);
  const [offline, setOffline] = useState(false);
  const hasAccount = accountId != null;

  useEffect(() => {
    let cancelled = false;
    fetchDashboard(mode, accountId)
      .then((data) => {
        if (cancelled) return;
        setCategories(data.categories);
        setMonth(data.month ?? null);
        setOffline(false);
      })
      .catch(() => {
        if (cancelled) return;
        setCategories(FALLBACK_CATEGORIES);
        setMonth(null);
        setOffline(true);
      });
    return () => {
      cancelled = true;
    };
  }, [mode, accountId]);

  return (
    <section className="dashboard">
      <div className="dashboard__intro">
        <h1>Home Dashboard</h1>
        <p className="dashboard__subtitle">Your account at a glance.</p>
        {(month || offline || mode === MODES.PLAN) && (
          <div className="dashboard__notices">
            {month && <span>Figures for {month}</span>}
            {mode === MODES.PLAN && !offline && <span>Plan figures are placeholders</span>}
            {offline && (
              <span className="dashboard__notice--warning">Backend offline, showing placeholders</span>
            )}
          </div>
        )}
      </div>

      {mode === MODES.PLAN && (
        <ScenarioForm accountId={accountId} />
      )}

      <div className="dashboard__grid">
        {categories.map((c, index) => (
          <CategoryCard key={c.key} category={c} featured={index === 0} />
        ))}
      </div>

      <div className={`dashboard__activity ${hasAccount ? "" : "dashboard__activity--solo"}`}>
        <AiInsights mode={mode} />
        {hasAccount && (
          <div className="dashboard__activity-main">
            <AccountDetails accountId={accountId} />
          </div>
        )}
      </div>
    </section>
  );
}
