import { useEffect, useMemo, useState } from "react";
import "./AccountPicker.css";

// Searchable account selector: type part of an ID to filter the list.
export default function AccountPicker({ accounts, accountId, onChange }) {
  const [text, setText] = useState(accountId != null ? String(accountId) : "");
  const ids = useMemo(() => new Set(accounts.map((a) => a.account_id)), [accounts]);

  // Keep the input in sync when the selection changes from outside.
  useEffect(() => {
    setText(accountId != null ? String(accountId) : "");
  }, [accountId]);

  function handleChange(e) {
    const value = e.target.value;
    setText(value);
    const id = Number(value);
    if (ids.has(id) && id !== accountId) onChange(id);
  }

  const invalid = text !== "" && !ids.has(Number(text));

  return (
    <label className="picker">
      <span className="picker__label">Account</span>
      <input
        className={`picker__input ${invalid ? "is-invalid" : ""}`}
        list="account-options"
        inputMode="numeric"
        value={text}
        onChange={handleChange}
        onBlur={() => invalid && setText(accountId != null ? String(accountId) : "")}
        placeholder="Search account ID"
        aria-invalid={invalid}
      />
      <datalist id="account-options">
        {accounts.map((a) => (
          <option key={a.account_id} value={a.account_id}>
            {a.district_name} · {a.frequency}
          </option>
        ))}
      </datalist>
    </label>
  );
}
