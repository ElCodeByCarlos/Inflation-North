import { CATEGORY_META } from "../../constants/categories.js";
import "./CategoryCard.css";

const currency = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

export default function CategoryCard({ category }) {
  const { key, title, amount, change } = category;
  const meta = CATEGORY_META[key];
  const trend = change > 0 ? "up" : change < 0 ? "down" : "flat";

  return (
    <article className="card" style={{ "--accent": meta.accent }}>
      <div className="card__header">
        <span className="card__icon" aria-hidden="true">{meta.icon}</span>
        <h2 className="card__title">{title}</h2>
      </div>
      <p className="card__amount">{currency.format(amount)}</p>
      <p className={`card__change card__change--${trend}`}>
        {change > 0 ? "+" : ""}
        {change.toFixed(1)}% vs last period
      </p>
      {/* Placeholder area for future charts / details */}
      <div className="card__body" />
    </article>
  );
}
