import { useEffect, useState } from "react";
import CategoryCard from "../../components/CategoryCard/CategoryCard.jsx";
import { fetchDashboard } from "../../services/api.js";
import { FALLBACK_CATEGORIES, MODES } from "../../constants/categories.js";
import "./Dashboard.css";

export default function Dashboard({ mode }) {
  const [categories, setCategories] = useState(FALLBACK_CATEGORIES);
  const [offline, setOffline] = useState(false);

  useEffect(() => {
    let cancelled = false;
    fetchDashboard(mode)
      .then((data) => {
        if (cancelled) return;
        setCategories(data.categories);
        setOffline(false);
      })
      .catch(() => {
        if (cancelled) return;
        setCategories(FALLBACK_CATEGORIES);
        setOffline(true);
      });
    return () => {
      cancelled = true;
    };
  }, [mode]);

  return (
    <section className="dashboard">
      <div className="dashboard__heading">
        <h1>{mode === MODES.PLAN ? "Plan" : "Current"} overview</h1>
        {offline && (
          <span className="dashboard__notice">Backend offline, showing placeholders</span>
        )}
      </div>
      <div className="dashboard__grid">
        {categories.map((c) => (
          <CategoryCard key={c.key} category={c} />
        ))}
      </div>
    </section>
  );
}
