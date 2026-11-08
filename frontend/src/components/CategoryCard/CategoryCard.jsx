import "./CategoryCard.css";

const currency = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

export default function CategoryCard({ category, featured = false }) {
  const { title, amount, change } = category;
  const trend = change > 0 ? "up" : change < 0 ? "down" : "flat";

  return (
    <article className={`card ${featured ? "card--featured" : ""}`}>
      <p className="card__title">{title}</p>
      <p className="card__amount">{currency.format(amount)}</p>
      <p className={`card__change card__change--${trend}`}>
        <span className="card__change-value">
          {change > 0 ? "+" : ""}
          {change.toFixed(1)}%
        </span>{" "}
        vs last period
      </p>
    </article>
  );
}
