import { useEffect, useState } from "react";
import { fetchInsights } from "../../services/api.js";
import "./AiInsights.css";

export default function AiInsights({ mode }) {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  // Clear stale output when switching between Current / Plan.
  useEffect(() => {
    setResult(null);
    setError(null);
  }, [mode]);

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      setResult(await fetchInsights(mode, question.trim() || undefined));
    } catch (err) {
      setError(err.message);
      setResult(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="ai">
      <div className="ai__header">
        <h2 className="ai__title">AI insights</h2>
        {result && <span className="ai__model">{result.model}</span>}
      </div>
      <form className="ai__form" onSubmit={handleSubmit}>
        <input
          className="ai__input"
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask about your finances (optional)"
          maxLength={1000}
        />
        <button className="ai__button" type="submit" disabled={loading}>
          {loading ? "Thinking…" : "Generate"}
        </button>
      </form>
      {error && <p className="ai__error">{error}</p>}
      {result && <p className="ai__text">{result.text}</p>}
    </section>
  );
}
