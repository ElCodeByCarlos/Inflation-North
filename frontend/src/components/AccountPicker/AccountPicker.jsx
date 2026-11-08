import { useEffect, useMemo, useRef, useState } from "react";
import "./AccountPicker.css";

// Searchable account selector: type part of an ID/district to filter the list.
export default function AccountPicker({ accounts, accountId, onChange }) {
  const [text, setText] = useState(accountId != null ? String(accountId) : "");
  const [open, setOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);
  const rootRef = useRef(null);

  const ids = useMemo(() => new Set(accounts.map((a) => a.account_id)), [accounts]);

  // Keep the input in sync when the selection changes from outside.
  useEffect(() => {
    setText(accountId != null ? String(accountId) : "");
  }, [accountId]);

  // Filter on whatever the user typed, not just the ID.
  const options = useMemo(() => {
    const query = text.trim().toLowerCase();
    if (!query) return accounts;
    return accounts.filter((a) =>
      [a.account_id, a.district_name, a.frequency]
        .filter((value) => value != null)
        .some((value) => String(value).toLowerCase().includes(query))
    );
  }, [accounts, text]);

  // Close when the user clicks anywhere outside the picker.
  useEffect(() => {
    function handleOutsideClick(e) {
      if (rootRef.current && !rootRef.current.contains(e.target)) setOpen(false);
    }
    document.addEventListener("mousedown", handleOutsideClick);
    return () => document.removeEventListener("mousedown", handleOutsideClick);
  }, []);

  // Keep the keyboard-highlighted option visible in the scrollable list.
  useEffect(() => {
    if (!open || activeIndex < 0) return;
    const option = options[activeIndex];
    if (!option) return;
    document
      .getElementById(`account-option-${option.account_id}`)
      ?.scrollIntoView({ block: "nearest" });
  }, [open, activeIndex, options]);

  function selectAccount(account) {
    setText(String(account.account_id));
    setOpen(false);
    setActiveIndex(-1);
    if (account.account_id !== accountId) onChange(account.account_id);
  }

  function handleChange(e) {
    const value = e.target.value;
    setText(value);
    setOpen(true);
    setActiveIndex(-1);
    const id = Number(value);
    if (ids.has(id) && id !== accountId) onChange(id);
  }

  function handleKeyDown(e) {
    if (e.key === "ArrowDown" || e.key === "ArrowUp") {
      e.preventDefault();
      setOpen(true);
      if (options.length === 0) return;
      setActiveIndex((index) => {
        if (e.key === "ArrowDown") return (index + 1) % options.length;
        return index <= 0 ? options.length - 1 : index - 1;
      });
    } else if (e.key === "Enter") {
      const option = options[activeIndex];
      if (open && option) {
        e.preventDefault();
        selectAccount(option);
      }
    } else if (e.key === "Escape") {
      setOpen(false);
      setActiveIndex(-1);
    }
  }

  const invalid = text !== "" && !ids.has(Number(text));

  return (
    <div className="picker" ref={rootRef}>
      <label className="picker__label" htmlFor="account-picker-input">
        Account
      </label>
      <div className="picker__control">
        <input
          id="account-picker-input"
          className={`picker__input ${invalid ? "is-invalid" : ""}`}
          role="combobox"
          aria-expanded={open}
          aria-controls="account-picker-options"
          aria-autocomplete="list"
          aria-activedescendant={
            open && activeIndex >= 0 && options[activeIndex]
              ? `account-option-${options[activeIndex].account_id}`
              : undefined
          }
          aria-invalid={invalid}
          autoComplete="off"
          inputMode="numeric"
          value={text}
          onChange={handleChange}
          onFocus={() => setOpen(true)}
          onClick={() => setOpen(true)}
          onKeyDown={handleKeyDown}
          onBlur={(e) => {
            if (invalid) setText(accountId != null ? String(accountId) : "");
            if (!rootRef.current?.contains(e.relatedTarget)) setOpen(false);
          }}
          placeholder="Search account"
        />
        <button
          type="button"
          className="picker__toggle"
          aria-label={open ? "Close account list" : "Open account list"}
          tabIndex={-1}
          onClick={() => setOpen((isOpen) => !isOpen)}
        >
          <span className={`picker__caret ${open ? "is-open" : ""}`} aria-hidden="true" />
        </button>

        {open && (
          <ul className="picker__menu" id="account-picker-options" role="listbox">
            {options.length === 0 ? (
              <li className="picker__empty">No matching accounts</li>
            ) : (
              options.map((account, index) => (
                <li
                  key={account.account_id}
                  id={`account-option-${account.account_id}`}
                  role="option"
                  aria-selected={account.account_id === accountId}
                  className={[
                    "picker__option",
                    index === activeIndex ? "is-active" : "",
                    account.account_id === accountId ? "is-selected" : "",
                  ]
                    .filter(Boolean)
                    .join(" ")}
                  onMouseDown={(e) => {
                    e.preventDefault();
                    selectAccount(account);
                  }}
                  onMouseEnter={() => setActiveIndex(index)}
                >
                  <span className="picker__option-id">#{account.account_id}</span>
                  <span className="picker__option-meta">
                    {account.district_name} · {account.frequency}
                  </span>
                </li>
              ))
            )}
          </ul>
        )}
      </div>
    </div>
  );
}
