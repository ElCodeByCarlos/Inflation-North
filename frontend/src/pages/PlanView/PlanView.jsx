import { useEffect, useRef, useState } from "react";
import SplitCard from "../../components/SplitCard/SplitCard.jsx";
import RecoveryPlan from "../../components/RecoveryPlan/RecoveryPlan.jsx";
import GeminiPlan from "../../components/GeminiPlan/GeminiPlan.jsx";
import { fetchDashboard, fetchPlanAdvice, simulatePlan } from "../../services/api.js";
import { FALLBACK_CATEGORIES, MODES, SCENARIOS } from "../../constants/categories.js";
import "./PlanView.css";

// Before a simulation runs, both halves show the account's current figures.
const toSplit = (categories) =>
  categories.map(({ key, title, amount }) => ({ key, title, current: amount, projected: amount }));

export default function PlanView({ accountId, onMonthChange }) {
  const [scenario, setScenario] = useState(SCENARIOS[0].value);
  const [amountText, setAmountText] = useState("");

  const [baseline, setBaseline] = useState(null); // current-month categories
  const [baselineError, setBaselineError] = useState(null);

  const [sim, setSim] = useState(null);
  const [simError, setSimError] = useState(null);
  const [simLoading, setSimLoading] = useState(false);

  const [advice, setAdvice] = useState(null);
  const [adviceError, setAdviceError] = useState(null);
  const [adviceLoading, setAdviceLoading] = useState(false);

  // Bumped whenever inputs change so late responses from an old submit are ignored.
  const requestId = useRef(0);

  const amount = Number(amountText);
  const validAmount = amountText !== "" && Number.isFinite(amount) && amount > 0;

  // Left ("Now") side: the account's real current figures, independent of the simulation.
  useEffect(() => {
    setBaseline(null);
    setBaselineError(null);
    if (accountId == null) return undefined;
    let cancelled = false;
    fetchDashboard(MODES.CURRENT, accountId)
      .then((data) => {
        if (cancelled) return;
        setBaseline(data.categories);
        onMonthChange?.(data.month ?? null);
      })
      .catch((err) => {
        if (cancelled) return;
        setBaselineError(err.message);
        onMonthChange?.(null);
      });
    return () => {
      cancelled = true;
    };
  }, [accountId, onMonthChange]);

  // Inputs changed: previous results no longer match, clear them until resubmitted.
  useEffect(() => {
    requestId.current += 1;
    setSim(null);
    setSimError(null);
    setSimLoading(false);
    setAdvice(null);
    setAdviceError(null);
    setAdviceLoading(false);
  }, [accountId, scenario, amountText]);

  function handleSubmit(e) {
    e.preventDefault();
    if (accountId == null || !validAmount) return;
    const id = ++requestId.current;
    const isCurrent = () => id === requestId.current;

    setSimLoading(true);
    setSimError(null);
    setAdviceLoading(true);
    setAdviceError(null);
    setAdvice(null);

    simulatePlan(accountId, scenario, amount)
      .then((data) => isCurrent() && setSim(data))
      .catch((err) => isCurrent() && setSimError(err.message))
      .finally(() => isCurrent() && setSimLoading(false));

    fetchPlanAdvice(accountId, scenario, amount)
      .then((data) => isCurrent() && setAdvice(data))
      .catch((err) => isCurrent() && setAdviceError(err.message))
      .finally(() => isCurrent() && setAdviceLoading(false));
  }

  const loading = simLoading || adviceLoading;
  const splits = sim?.categories ?? toSplit(baseline ?? FALLBACK_CATEGORIES);

  return (
    <>
      <form className="scenario" onSubmit={handleSubmit}>
        <label className="scenario__field">
          <span className="scenario__label">Scenario</span>
          <select
            className="scenario__input"
            value={scenario}
            onChange={(e) => setScenario(e.target.value)}
          >
            {SCENARIOS.map((s) => (
              <option key={s.value} value={s.value}>
                {s.label}
              </option>
            ))}
          </select>
        </label>
        <label className="scenario__field scenario__field--grow">
          <span className="scenario__label">
            {scenario === "no_income" ? "Income lost" : "Amount spent"}
          </span>
          <input
            className="scenario__input"
            type="number"
            inputMode="decimal"
            min="0"
            step="any"
            placeholder="e.g. 1000"
            value={amountText}
            onChange={(e) => setAmountText(e.target.value)}
          />
        </label>
        <button
          className="scenario__button"
          type="submit"
          disabled={loading || accountId == null || !validAmount}
        >
          {loading ? "Generating…" : "Generate plan"}
        </button>
      </form>

      {accountId == null && (
        <p className="scenario__notice">Select an account to simulate a loss.</p>
      )}
      {baselineError && (
        <p className="scenario__notice scenario__notice--error">
          Couldn't load current figures: {baselineError}
        </p>
      )}
      {simError && <p className="scenario__notice scenario__notice--error">{simError}</p>}

      <div className="dashboard__grid">
        {splits.map((c) => (
          <SplitCard key={c.key} category={c} />
        ))}
      </div>

      {sim && <RecoveryPlan recovery={sim.recovery} />}
      {accountId != null && (
        <GeminiPlan
          loading={adviceLoading}
          error={adviceError}
          advice={advice}
          severity={sim?.recovery.severity}
        />
      )}
    </>
  );
}
