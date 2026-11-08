import "./RecoveryPlan.css";

const currency = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

const SEVERITY_LABEL = {
  green: "Good standing",
  yellow: "Moderate impact",
  red: "Severe impact",
};

export default function RecoveryPlan({ recovery }) {
  const { severity, months, target_month, monthly_recovery, message, steps } = recovery;
  const hasLoss = steps.length > 0;

  return (
    <section className="recovery">
      <h2 className="recovery__title">Recovery plan</h2>
      <div className={`recovery__banner recovery__banner--${severity}`} role="status">
        {hasLoss && <strong className="recovery__badge">{SEVERITY_LABEL[severity]}</strong>}
        <p className="recovery__message">{message}</p>
      </div>
      {hasLoss && (
        <>
          <dl className="recovery__stats">
            <div>
              <dt>Time to recover</dt>
              <dd>{months == null ? "Not reachable" : `${months} mo`}</dd>
            </div>
            <div>
              <dt>Back to normal by</dt>
              <dd>{target_month ?? "—"}</dd>
            </div>
            <div>
              <dt>Set aside per month</dt>
              <dd>{currency.format(monthly_recovery)}</dd>
            </div>
          </dl>
          <ol className="recovery__steps">
            {steps.map((s) => (
              <li key={s}>{s}</li>
            ))}
          </ol>
        </>
      )}
    </section>
  );
}
