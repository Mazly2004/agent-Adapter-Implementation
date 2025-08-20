import React, { useState } from "react";

function App() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showLogs, setShowLogs] = useState(false);
  const [logs, setLogs] = useState([]);

 const fetchLogs = async () => {
  if (!showLogs) {
    const res = await fetch("http://localhost:8000/logs");
    const data = await res.json();
    setLogs(data.logs);
    setShowLogs(true);
  } else {
    setShowLogs(false);
  }
  };


  const ask = async () => {
    setLoading(true);
    const res = await fetch("http://localhost:8000/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    setResult(await res.json());
    setLoading(false);
    setQuestion("");
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
          <br />
          <div><b>Sentiment:</b> {result.sentiment}</div>
          <br />
          <div><b>Self-Check:</b> {result.selfCheckResult}</div>
          <br />
          <div className='initial-response'><b>Initial Response:</b> <div>{result.initialResponse}</div></div>
          {result.finalResponse && (
            <div className="rewritten-response"><b>Rewritten Response:</b> <div>{result.finalResponse}</div></div>
          )}
        </div>
        
      )}
      <button onClick={fetchLogs} style={{ marginTop: 20 }}>
        {showLogs ? "Hide Flagged Logs" : "Show Flagged Logs"}
      </button>
      {showLogs && (
        <div style={{ marginTop: 20, background: "#f8f9fa", padding: 10, borderRadius: 5 }}>
          <h3>Flagged/Not Found Logs</h3>
          <button onClick={async () => {
            const res = await fetch("http://localhost:8000/logs");
            const data = await res.json();
            setLogs(data.logs);
          }} style={{ marginBottom: 10 }}>Refresh Logs</button>
          {logs.length === 0 ? (
            <div>No logs found.</div>
          ) : (
            <ul>
              {logs.map((log, idx) => (
                <li key={idx} style={{ fontSize: 12, marginBottom: 5 }}>{log}</li>
              ))}
            </ul>
          )}
        </div>
)}
    </div>
  );
}

export default App;