import React, { useState } from "react";

function App() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const ask = async () => {
    setLoading(true);
    const res = await fetch("http://localhost:8000/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    setResult(await res.json());
    setLoading(false);
  };

  return (
    <div style={{ maxWidth: 600, margin: "2rem auto", fontFamily: "sans-serif" }}>
      <h2>Adapter Analysis Dashboard</h2>
      <input
        style={{ width: "100%", padding: 8, fontSize: 16 }}
        value={question}
        onChange={e => setQuestion(e.target.value)}
        placeholder="Ask a question..."
      />
      <button style={{ marginTop: 10 }} onClick={ask} disabled={loading}>
        {loading ? "Loading..." : "Ask"}
      </button>
      {result && (
        <div style={{ marginTop: 30 }}>
          <div><b>Question:</b> {result.question}</div>
          <div><b>Sentiment:</b> {result.sentiment}</div>
          <div><b>Self-Check:</b> {result.selfCheckResult}</div>
          <div><b>Initial Response:</b> <pre>{result.initialResponse}</pre></div>
          {result.finalResponse && (
            <div><b>Rewritten Response:</b> <pre>{result.finalResponse}</pre></div>
          )}
        </div>
      )}
    </div>
  );
}

export default App;