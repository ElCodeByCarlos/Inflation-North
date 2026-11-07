import { useEffect, useState } from "react";

export function AccountPageViewModel(accountId) {
  const [accountData, setAccountData] = useState(null);
  const [loading, setLoading] = useState(Boolean(accountId));
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!accountId) {
      setAccountData(null);
      setLoading(false);
      return undefined;
    }

    let cancelled = false;
    setLoading(true);
    setError(null);

    fetch(`/api/accounts/${accountId}`)
      .then((response) => {
        if (!response.ok) throw new Error(`Request failed: ${response.status}`);
        return response.json();
      })
      .then((data) => {
        if (!cancelled) setAccountData(data);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [accountId]);

  return { accountData, loading, error };
}
