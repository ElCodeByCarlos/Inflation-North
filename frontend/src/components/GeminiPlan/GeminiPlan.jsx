import "./GeminiPlan.css";

// Box showing the Gemini-written recovery plan. `severity` tints the border
// to match the rule-based green/yellow/red message above it.
export default function GeminiPlan({ loading, error, advice, severity }) {
  return (
    <section className={`gemini gemini--${severity ?? "none"}`}>
      <div className="gemini__header">
        <h2 className="gemini__title">Gemini recovery plan</h2>
        {advice && <span className="gemini__model">{advice.model}</span>}
      </div>
      {loading && <p className="gemini__status">Gemini is thinking…</p>}
      {!loading && error && <p className="gemini__error">{error}</p>}
      {!loading && !error && advice && <p className="gemini__text">{advice.text}</p>}
      {!loading && !error && !advice && (
        <p className="gemini__status">
          Pick a scenario, enter an amount and press Generate plan.
        </p>
      )}
    </section>
  );
}
