import { useEffect, useState } from "react";
import CategoryCard from "../../components/CategoryCard/CategoryCard.jsx";
import AiInsights from "../../components/AiInsights/AiInsights.jsx";
import AccountDetails from "../../components/AccountDetails/AccountDetails.jsx";
import { fetchDashboard } from "../../services/api.js";
import { FALLBACK_CATEGORIES, MODES } from "../../constants/categories.js";
import "./Dashboard.css";

export default function Dashboard({ mode, accountId }) {
  const [categories, setCategories] = useState(FALLBACK_CATEGORIES);
  const [month, setMonth] = useState(null);
  const [offline, setOffline] = useState(false);

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
      <div className="dashboard__heading">
        <h1>
          {accountId != null && `Account ${accountId} · `}
          {mode === MODES.PLAN ? "Plan" : "Current"} overview
        </h1>
        {month && <span className="dashboard__notice">Figures for {month}</span>}
        {mode === MODES.PLAN && !offline && (
          <span className="dashboard__notice">Plan figures are placeholders</span>
        )}
        {offline && (
          <span className="dashboard__notice">Backend offline, showing placeholders</span>
        )}
      </div>
      <div className="dashboard__grid">
        {categories.map((c) => (
          <CategoryCard key={c.key} category={c} />
        ))}
      </div>
      <AiInsights mode={mode} />
      {accountId != null && <AccountDetails accountId={accountId} />}
    </section>
  );
}
