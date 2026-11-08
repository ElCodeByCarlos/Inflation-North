import { useEffect, useState } from "react";
import CategoryCard from "../../components/CategoryCard/CategoryCard.jsx";
import AiInsights from "../../components/AiInsights/AiInsights.jsx";
import AccountDetails from "../../components/AccountDetails/AccountDetails.jsx";
import PlanView from "../PlanView/PlanView.jsx";
import { fetchDashboard } from "../../services/api.js";
import { FALLBACK_CATEGORIES, MODES } from "../../constants/categories.js";
import "./Dashboard.css";

export default function Dashboard({ mode, accountId }) {
  const [categories, setCategories] = useState(FALLBACK_CATEGORIES);
  const [month, setMonth] = useState(null);
  const [offline, setOffline] = useState(false);
<<<<<<< Updated upstream
  const hasAccount = accountId != null;
=======
  const isPlan = mode === MODES.PLAN;
>>>>>>> Stashed changes

  useEffect(() => {
    // Plan mode fetches its own data (scenario simulation) in PlanView.
    if (isPlan) return undefined;
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
  }, [mode, accountId, isPlan]);

  return (
    <section className="dashboard">
<<<<<<< Updated upstream
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
=======
      <div className="dashboard__heading">
        <h1>
          {accountId != null && `Account ${accountId} · `}
          {isPlan ? "Plan" : "Current"} overview
        </h1>
        {month && <span className="dashboard__notice">Figures for {month}</span>}
        {!isPlan && offline && (
          <span className="dashboard__notice">Backend offline, showing placeholders</span>
        )}
      </div>
      {isPlan ? (
        <PlanView accountId={accountId} onMonthChange={setMonth} />
      ) : (
        <>
          <div className="dashboard__grid">
            {categories.map((c) => (
              <CategoryCard key={c.key} category={c} />
            ))}
          </div>
          <AiInsights mode={mode} />
        </>
      )}
      {accountId != null && <AccountDetails accountId={accountId} />}
>>>>>>> Stashed changes
    </section>
  );
}
