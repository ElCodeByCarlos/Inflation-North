import { useEffect, useState } from "react";
import { fetchAccount, fetchTransactions } from "../../services/api.js";
import "./AccountDetails.css";

const money = new Intl.NumberFormat("en-US", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});
const fmt = (n) => (n == null ? "—" : money.format(n));
const PAGE = 50;

function ageFrom(birthDate) {
  if (!birthDate) return null;
  const b = new Date(birthDate);
  const now = new Date();
  let age = now.getFullYear() - b.getFullYear();
  if (now < new Date(now.getFullYear(), b.getMonth(), b.getDate())) age -= 1;
  return age;
}

function Section({ title, count, className = "", children }) {
  return (
    <section className={`details__section ${className}`.trim()}>
      <h3 className="details__title">
        {title}
        {count != null && <span className="details__count">{count}</span>}
      </h3>
      {children}
    </section>
  );
}

function Field({ label, value }) {
  return (
    <div className="details__field">
      <dt>{label}</dt>
      <dd>{value ?? "—"}</dd>
    </div>
  );
}

export default function AccountDetails({ accountId }) {
  const [detail, setDetail] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [error, setError] = useState(null);
  const [loadingMore, setLoadingMore] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setDetail(null);
    setError(null);
    fetchAccount(accountId)
      .then((data) => {
        if (cancelled) return;
        setDetail(data);
        setTransactions(data.transactions.items);
      })
      .catch((err) => !cancelled && setError(err.message));
    return () => {
      cancelled = true;
    };
  }, [accountId]);

  async function loadMore() {
    setLoadingMore(true);
    try {
      const page = await fetchTransactions(accountId, { limit: PAGE, offset: transactions.length });
      setTransactions((prev) => [...prev, ...page.items]);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingMore(false);
    }
  }

  if (error) return <p className="details__error">Could not load account: {error}</p>;
  if (!detail) return <p className="details__loading">Loading account {accountId}…</p>;

  const { account, district, clients, loans, standing_orders, monthly_summary } = detail;
  const totalTx = detail.transactions.total;
  const recentMonths = monthly_summary.slice(-12).reverse();

  return (
    <div className="details">
      <Section
        title="Transactions"
        count={`${transactions.length} of ${totalTx}`}
        className="details__section--transactions"
      >
        <div className="details__table-wrap details__table-wrap--scroll">
          <table className="details__table">
            <thead>
              <tr>
                <th>Date</th><th>Operation</th><th>Purpose</th><th>Partner</th>
                <th className="num">Amount</th><th className="num">Balance</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((t) => (
                <tr key={t.transaction_id}>
                  <td>{t.date}</td>
                  <td>{t.operation ?? "—"}</td>
                  <td>{t.purpose ?? "—"}</td>
                  <td>{t.partner_bank ? `${t.partner_bank} ${t.partner_account ?? ""}` : "—"}</td>
                  <td className={`num ${t.signed_amount < 0 ? "neg" : "pos"}`}>{fmt(t.signed_amount)}</td>
                  <td className="num">{fmt(t.balance)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {transactions.length < totalTx && (
          <button className="details__more" type="button" onClick={loadMore} disabled={loadingMore}>
            {loadingMore ? "Loading…" : `Load ${Math.min(PAGE, totalTx - transactions.length)} more`}
          </button>
        )}
      </Section>

      <Section title="Account">
        <dl className="details__fields">
          <Field label="Account ID" value={account.account_id} />
          <Field label="Opened" value={account.account_opened} />
          <Field label="Statements" value={account.frequency} />
          <Field label="District" value={district && `${district.district_name} (${district.region})`} />
          <Field label="Inhabitants" value={district?.inhabitants.toLocaleString("en-US")} />
          <Field label="Avg. salary" value={district && fmt(district.average_salary)} />
          <Field
            label="Unemployment 2023"
            value={district?.unemployment_rate_2023 != null ? `${district.unemployment_rate_2023}%` : null}
          />
          <Field label="Urban ratio" value={district && `${district.urban_ratio_pct}%`} />
        </dl>
      </Section>

      <Section title="Clients" count={clients.length}>
        <div className="details__table-wrap">
          <table className="details__table">
            <thead>
              <tr>
                <th>Client</th><th>Role</th><th>Gender</th><th>Born</th><th>Age</th><th>District</th><th>Cards</th>
              </tr>
            </thead>
            <tbody>
              {clients.map((c) => (
                <tr key={c.disposition_id}>
                  <td>{c.client_id}</td>
                  <td>{c.role}</td>
                  <td>{c.gender}</td>
                  <td>{c.birth_date}</td>
                  <td>{ageFrom(c.birth_date)}</td>
                  <td>{c.district_name}</td>
                  <td>
                    {c.cards.length === 0
                      ? "—"
                      : c.cards.map((card) => `${card.card_type} (${card.issued})`).join(", ")}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Section>

      {loans.length > 0 && (
        <Section title="Loans" count={loans.length}>
          <div className="details__table-wrap">
            <table className="details__table">
              <thead>
                <tr>
                  <th>Start</th><th className="num">Amount</th><th className="num">Months</th>
                  <th className="num">Monthly</th><th>Status</th>
                </tr>
              </thead>
              <tbody>
                {loans.map((l) => (
                  <tr key={l.loan_id}>
                    <td>{l.loan_start}</td>
                    <td className="num">{fmt(l.amount)}</td>
                    <td className="num">{l.duration_months}</td>
                    <td className="num">{fmt(l.monthly_payment)}</td>
                    <td className={l.defaulted ? "neg" : ""}>
                      {l.status} · {l.status_meaning}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Section>
      )}

      {standing_orders.length > 0 && (
        <Section title="Standing orders" count={standing_orders.length}>
          <div className="details__table-wrap">
            <table className="details__table">
              <thead>
                <tr>
                  <th>To bank</th><th>To account</th><th>Purpose</th><th className="num">Amount</th>
                </tr>
              </thead>
              <tbody>
                {standing_orders.map((o) => (
                  <tr key={o.order_id}>
                    <td>{o.to_bank ?? "—"}</td>
                    <td>{o.to_account ?? "—"}</td>
                    <td>{o.purpose ?? "—"}</td>
                    <td className="num">{fmt(o.amount)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Section>
      )}

      {recentMonths.length > 0 && (
        <Section title="Monthly summary (last 12 months)" count={monthly_summary.length}>
          <div className="details__table-wrap">
            <table className="details__table">
              <thead>
                <tr>
                  <th>Month</th><th className="num">Money in</th><th className="num">Money out</th>
                  <th className="num">End balance</th><th className="num">Min balance</th>
                  <th className="num">Days &lt; 0</th>
                </tr>
              </thead>
              <tbody>
                {recentMonths.map((m) => (
                  <tr key={m.month}>
                    <td>{m.month}</td>
                    <td className="num pos">{fmt(m.money_in)}</td>
                    <td className="num neg">{fmt(m.money_out)}</td>
                    <td className="num">{fmt(m.month_end_balance)}</td>
                    <td className="num">{fmt(m.min_balance)}</td>
                    <td className={`num ${m.days_below_zero > 0 ? "neg" : ""}`}>{m.days_below_zero}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Section>
      )}
    </div>
  );
}
