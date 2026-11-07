import { useParams } from "react-router";
import { AccountPageViewModel } from "../../viewModels/AccountPageViewModel.jsx";

export function AccountDashboard() {
  const { accountId } = useParams();
  const { accountData, loading, error } = AccountPageViewModel(accountId);

  if (loading) return <p>Loading account…</p>;
  if (error) return <p>Could not load account: {error}</p>;
  if (!accountData) return <p>No account selected.</p>;

  const { account, district, owners, cards, loans } = accountData;

  return (
    <div>
      <h1>Account Dashboard</h1>
      <section>
        <h2>Account #{account.account_id}</h2>
        <p>Frequency: {account.frequency}</p>
        <p>Opened: {account.account_opened}</p>
        {district && <p>District: {district.district_name}</p>}
      </section>

      <section>
        <h2>Owners ({owners.length})</h2>
        {owners.map((owner) => (
          <div key={owner.disposition_id}>
            <p>Client #{owner.client_id}</p>
            <p>{owner.type}</p>
          </div>
        ))}
      </section>

      <section>
        <h2>Cards ({cards.length})</h2>
        {cards.map((card) => (
          <p key={card.card_id}>
            {card.card_type} · issued {card.issued}
          </p>
        ))}
      </section>

      <section>
        <h2>Loans ({loans.length})</h2>
        {loans.map((loan) => (
          <p key={loan.loan_id}>
            {loan.amount} · {loan.status_meaning}
          </p>
        ))}
      </section>
    </div>
  );
}
