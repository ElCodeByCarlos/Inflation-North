import { useEffect, useState } from "react";
import { fetchScenarioPlan } from "../../services/api.js";
import "./ScenarioForm.css";

export const SCENARIO_TYPES = [
  { value: "accident", label: "Accident" },
  { value: "no_income", label: "No income" },
  { value: "purchase", label: "Purchase" },
];

export default function ScenarioForm({ accountId, onSubmit }) {
  const [type, setType] = useState(SCENARIO_TYPES[0].value);
  const [amount, setAmount] = useState("");
  const [invalid, setInvalid] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  // A plan for one account is meaningless for another.
  useEffect(() => {
    setResult(null);
    setError(null);
  }, [accountId]);

  async function handleSubmit(event) {
    event.preventDefault();
    const value = Number(amount);
    if (amount.trim() === "" || !Number.isFinite(value) || value <= 0) {
      setInvalid(true);
      return;
    }
    setInvalid(false);
    onSubmit?.({ type, amount: value });
    setLoading(true);
    setError(null);
    try {
      setResult(await fetchScenarioPlan({ type, amount: value, accountId }));
    } catch (err) {
      setError(err.message);
      setResult(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="scenario" onSubmit={handleSubmit} noValidate>
      <label className="scenario__field">
        <span className="scenario__label">Scenario</span>
        <select
          className="scenario__select"
          value={type}
          onChange={(e) => setType(e.target.value)}
        >
          {SCENARIO_TYPES.map((t) => (
            <option key={t.value} value={t.value}>
              {t.label}
            </option>
          ))}
        </select>
      </label>

      <label className="scenario__field scenario__field--grow">
        <span className="scenario__label">Amount lost</span>
        <input
          className={`scenario__input ${invalid ? "is-invalid" : ""}`}
          type="number"
          inputMode="decimal"
          min="0"
          step="0.01"
          placeholder="0.00"
          value={amount}
          aria-invalid={invalid}
          onChange={(e) => {
            setAmount(e.target.value);
            if (invalid) setInvalid(false);
          }}
        />
      </label>

      <button className="scenario__button" type="submit" disabled={loading}>
        {loading ? "Planning…" : "Submit"}
      </button>

      <output
        className={`scenario__output ${error ? "is-invalid" : ""}`}
        aria-live="polite"
        aria-busy={loading}
      >
        {loading ? (
          <span className="scenario__output-placeholder">Creating your financial plan…</span>
        ) : error ? (
          <span className="scenario__output-error">{error}</span>
        ) : result ? (
          <>
            <span className="scenario__output-meta">
              {result.in_debt ? "Debt recovery plan" : "Recovery plan"} · {result.model}
            </span>
            {result.text}
          </>
        ) : (
          <span className="scenario__output-placeholder">
            Submit a scenario and Gemini will create a financial plan for you here.
          </span>
        )}
      </output>
    </form>
  );
}
