import { CATEGORY_META } from "../../constants/categories.js";
import "./SplitCard.css";

const currency = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

// For expenses a rise is bad; for income, savings and balance a drop is bad.
const HIGHER_IS_WORSE = new Set(["expenses"]);

export default function SplitCard({ category }) {
  const { key, title, current, projected } = category;
  const meta = CATEGORY_META[key];
  const delta = projected - current;
  const worse = HIGHER_IS_WORSE.has(key) ? delta > 0 : delta < 0;
  const tone = delta === 0 ? "flat" : worse ? "down" : "up";

  return (
    <article className="split" style={{ "--accent": meta.accent }}>
      <div className="split__header">
        <span className="split__icon" aria-hidden="true">{meta.icon}</span>
        <h2 className="split__title">{title}</h2>
      </div>
      <div className="split__halves">
        <div className="split__half">
          <span className="split__label">Now</span>
          <p className="split__amount">{currency.format(current)}</p>
        </div>
        <div className="split__half split__half--after">
          <span className="split__label">After loss</span>
          <p className="split__amount">{currency.format(projected)}</p>
          <p className={`split__delta split__delta--${tone}`}>
            {delta === 0 ? "No change" : `${delta > 0 ? "+" : "−"}${currency.format(Math.abs(delta))}`}
          </p>
        </div>
      </div>
    </article>
  );
}
