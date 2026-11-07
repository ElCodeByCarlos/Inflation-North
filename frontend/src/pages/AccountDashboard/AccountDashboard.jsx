import { useParams } from "react-router";
import { AccountPageViewModel } from "../../viewModels/AccountPageViewModel.jsx";
import "./AccountDashboard.css";

export function AccountDashboard() {
  const { accountId } = useParams();
  const { accountData, loading, error } = AccountPageViewModel(accountId);

  if (loading) {
    return (
      <section className="account-dashboard">
        <p className="account-dashboard__status">Loading account…</p>
      </section>
    );
  }
  if (error) {
    return (
      <section className="account-dashboard">
        <p className="account-dashboard__status account-dashboard__status--error">
          Could not load account: {error}
        </p>
      </section>
    );
  }
  if (!accountData) {
    return (
      <section className="account-dashboard">
        <p className="account-dashboard__status">No account selected.</p>
      </section>
    );
  }

  const { account, district, owners, cards, loans } = accountData;

  return (
    <section className="account-dashboard">
      <div className="account-dashboard__heading">
        <h1>Account overview</h1>
        <span className="account-dashboard__id">Account #{account.account_id}</span>
      </div>

      <section className="account-dashboard__summary">
        <div>
          <span className="account-dashboard__label">Frequency</span>
          <strong>{account.frequency}</strong>
        </div>
        <div>
          <span className="account-dashboard__label">Opened</span>
          <strong>{account.account_opened}</strong>
        </div>
        {district && (
          <div>
            <span className="account-dashboard__label">District</span>
            <strong>{district.district_name}</strong>
          </div>
        )}
      </section>

      <div className="account-dashboard__grid">
        <section className="account-dashboard__card account-dashboard__card--owners">
          <h2>Owners <span>({owners.length})</span></h2>
          {owners.map((owner) => (
            <div className="account-dashboard__item" key={owner.disposition_id}>
              <strong>Client #{owner.client_id}</strong>
              <span>{owner.type}</span>
            </div>
          ))}
        </section>

        <section className="account-dashboard__card account-dashboard__card--cards">
          <h2>Cards <span>({cards.length})</span></h2>
          {cards.map((card) => (
            <div className="account-dashboard__item" key={card.card_id}>
              <strong>{card.card_type}</strong>
              <span>Issued {card.issued}</span>
            </div>
          ))}
        </section>

        <section className="account-dashboard__card account-dashboard__card--loans">
          <h2>Loans <span>({loans.length})</span></h2>
          {loans.map((loan) => (
            <div className="account-dashboard__item" key={loan.loan_id}>
              <strong>{loan.amount}</strong>
              <span>{loan.status_meaning}</span>
            </div>
          ))}
        </section>
      </div>
    </section>
  );
}
