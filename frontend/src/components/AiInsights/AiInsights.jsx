import { useEffect, useState } from "react";
import { fetchInsights } from "../../services/api.js";
import messageIcon from "../../assets/message.svg";
import continueIcon from "../../assets/continue.svg";
import "./AiInsights.css";

const EXAMPLES = ["Explain a transaction", "Summarize my transactions"];

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
        <span className="ai__badge" aria-hidden="true">
          <img src={messageIcon} alt="" />
        </span>
        <h2 className="ai__title">Get Insights</h2>
      </div>
      <p className="ai__lede">Ask a question about your account or transactions.</p>

      <form className="ai__form" onSubmit={handleSubmit}>
        <textarea
          className="ai__input"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question..."
          maxLength={1000}
          rows={3}
        />
        <div className="ai__examples">
          {EXAMPLES.map((example) => (
            <button
              key={example}
              type="button"
              className="ai__example"
              onClick={() => setQuestion(example)}
            >
              {example}
            </button>
          ))}
        </div>
        <button className="ai__button" type="submit" disabled={loading}>
          <span>{loading ? "Thinking…" : "Ask question"}</span>
          <img src={continueIcon} alt="" aria-hidden="true" />
        </button>
      </form>

      {error && <p className="ai__error">{error}</p>}
      {result && (
        <div className="ai__result">
          {result.model && <span className="ai__model">{result.model}</span>}
          <p className="ai__text">{result.text}</p>
        </div>
      )}
      <p className="ai__powered">Powered by Gemini</p>
    </section>
  );
}
