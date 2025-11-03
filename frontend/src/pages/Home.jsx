import React, { useState, useEffect } from "react";
import ReactFlow, { MiniMap, Controls, Background } from "reactflow";
import 'reactflow/dist/style.css';
import { simplifyExpression, getApiBaseUrl } from "../assets/api";

function Home() {
  const [input, setInput] = useState("");
  const [output, setOutput] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // React Flow state
  const [rfNodes, setRfNodes] = useState([]);
  const [rfEdges, setRfEdges] = useState([]);
  const [circuitLoading, setCircuitLoading] = useState(false);

  const handleSimplify = async () => {
    if (!input.trim()) {
      setError("Please enter an expression");
      return;
    }

    setLoading(true);
    setError(null);
    setOutput(null);
    setRfNodes([]);
    setRfEdges([]);

    try {
      const data = await simplifyExpression(input, false, true);
      setOutput(data);
    } catch (err) {
      setError(err.message || err.detail || "Error simplifying expression");
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !loading) {
      handleSimplify();
    }
  };

  useEffect(() => {
  if (!output) return;

  let cancelled = false;

  async function loadFromGraphObject(graph) {
    const nodes = (graph.nodes || []).map(n => ({
      id: String(n.id),
      type: n.type || 'default',
      data: { label: (n.data && n.data.label) ? n.data.label : (n.data || n.label || n.id) },
      position: n.position || { x: 0, y: 0 },
      style: { minWidth: 80 }
    }));

    const edges = (graph.edges || []).map(e => ({
      id: e.id || `e${e.source}-${e.target}`,
      source: String(e.source),
      target: String(e.target),
      animated: true,
    }));

    if (!cancelled) {
      setRfNodes(nodes);
      setRfEdges(edges);
    }
  }

  async function fetchCircuit() {
    try {
      setCircuitLoading(true);

      if (output.logic_graph) {
        await loadFromGraphObject(output.logic_graph);
        return;
      }

      if (!output.circuit_url) {
        return;
      }

  
      const base = getApiBaseUrl(); // ← Removed ternary
      const url = output.circuit_url.startsWith("http")
        ? output.circuit_url
        : `${base.replace(/\/$/, "")}${output.circuit_url}`; // ← Simplified

      const res = await fetch(url);
      if (!res.ok) throw new Error(`Failed to fetch circuit: ${res.statusText}`);
      const graph = await res.json();

      await loadFromGraphObject(graph);
    } catch (err) {
      console.error("Could not load circuit:", err);
    } finally {
      if (!cancelled) setCircuitLoading(false);
    }
  }

  fetchCircuit();

  return () => {
    cancelled = true;
  };
}, [output]);
    
  return (
    <>
      <style>{`
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }

        body {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
        }

        .app-container {
          min-height: 100vh;
          background: linear-gradient(135deg, #1e1b4b 0%, #581c87 50%, #1e1b4b 100%);
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 2rem;
        }

        .container {
          width: 100%;
          max-width: 900px;
        }

        .header {
          text-align: center;
          margin-bottom: 3rem;
        }

        .title {
          font-size: 3rem;
          font-weight: bold;
          margin-bottom: 1rem;
          background: linear-gradient(to right, #60a5fa, #a78bfa, #f472b6);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        .subtitle {
          font-size: 1.125rem;
          color: #d1d5db;
        }

        .card {
          background: rgba(30, 41, 59, 0.5);
          backdrop-filter: blur(10px);
          border: 1px solid rgba(71, 85, 105, 0.5);
          border-radius: 1.5rem;
          padding: 2.5rem;
          box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        }

        .form-container {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }

        .input-group {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .label {
          font-size: 0.875rem;
          font-weight: 600;
          color: #e5e7eb;
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }

        .input {
          width: 100%;
          padding: 1rem 1.25rem;
          border-radius: 0.75rem;
          background: rgba(15, 23, 42, 0.5);
          color: white;
          border: 2px solid #475569;
          font-size: 1.125rem;
          font-family: 'Courier New', monospace;
          transition: all 0.2s;
        }

        .input:focus {
          outline: none;
          border-color: #a855f7;
          box-shadow: 0 0 0 3px rgba(168, 85, 247, 0.2);
        }

        .input:disabled {
          opacity: 0.5;
          cursor: not-allowed;
          background: rgba(15, 23, 42, 0.3);
        }

        .input::placeholder {
          color: #6b7280;
        }

        .operator-box {
          margin-top: 0.75rem;
          padding: 1rem;
          background: rgba(15, 23, 42, 0.5);
          border-radius: 0.5rem;
          border: 1px solid rgba(71, 85, 105, 0.5);
        }

        .operator-title {
          font-size: 0.75rem;
          color: #9ca3af;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          margin-bottom: 0.75rem;
        }

        .operator-grid {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 1rem;
        }

        @media (max-width: 768px) {
          .operator-grid {
            grid-template-columns: repeat(2, 1fr);
          }
        }

        .operator-item {
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
        }

        .operator-label {
          font-size: 0.75rem;
          color: #9ca3af;
          font-weight: 500;
        }

        .operator-symbols {
          font-family: 'Courier New', monospace;
          color: #d8b4fe;
          font-size: 0.875rem;
        }

        .button {
          width: 100%;
          padding: 1rem 1.5rem;
          border-radius: 0.75rem;
          background: linear-gradient(to right, #2563eb, #7c3aed);
          color: white;
          border: none;
          font-size: 1.125rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
          box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
        }

        .button:hover:not(:disabled) {
          background: linear-gradient(to right, #1d4ed8, #6d28d9);
          transform: scale(1.02);
          box-shadow: 0 10px 15px -3px rgba(168, 85, 247, 0.5);
        }

        .button:disabled {
          background: #475569;
          cursor: not-allowed;
          opacity: 0.5;
          transform: none;
        }

        .loading-dots {
          display: inline-flex;
          gap: 0.25rem;
          margin-left: 0.5rem;
        }

        .dot {
          width: 0.5rem;
          height: 0.5rem;
          background: white;
          border-radius: 50%;
          animation: bounce 0.6s infinite;
        }

        .dot:nth-child(2) {
          animation-delay: 0.15s;
        }

        .dot:nth-child(3) {
          animation-delay: 0.3s;
        }

        @keyframes bounce {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-8px); }
        }

        .error-box {
          margin-top: 1.5rem;
          background: rgba(127, 29, 29, 0.3);
          backdrop-filter: blur(10px);
          border: 2px solid rgba(239, 68, 68, 0.5);
          color: #fecaca;
          padding: 1.25rem;
          border-radius: 0.75rem;
          box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
          animation: shake 0.3s ease-in-out;
        }

        @keyframes shake {
          0%, 100% { transform: translateX(0); }
          25% { transform: translateX(-5px); }
          75% { transform: translateX(5px); }
        }

        .error-strong {
          font-weight: bold;
          color: #fca5a5;
        }

        .result-box {
          margin-top: 2rem;
          background: rgba(30, 41, 59, 0.5);
          backdrop-filter: blur(10px);
          border: 1px solid rgba(71, 85, 105, 0.5);
          border-radius: 1.5rem;
          padding: 2.5rem;
          box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
          animation: fadeIn 0.4s ease-out;
        }

        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .result-title {
          font-size: 1.5rem;
          font-weight: bold;
          margin-bottom: 1.5rem;
          background: linear-gradient(to right, #4ade80, #60a5fa);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        .result-container {
          display: flex;
          flex-direction: column;
          gap: 1.25rem;
        }

        .result-row {
          display: flex;
          align-items: flex-start;
          padding: 1rem;
          background: rgba(15, 23, 42, 0.3);
          border-radius: 0.5rem;
          border: 1px solid rgba(71, 85, 105, 0.3);
          transition: border-color 0.2s;
        }

        .result-row:hover {
          border-color: rgba(100, 116, 139, 0.5);
        }

        .result-label {
          font-weight: 600;
          color: #d1d5db;
          min-width: 144px;
          font-size: 0.875rem;
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }

        .result-original {
          font-family: 'Courier New', monospace;
          color: #e5e7eb;
          font-size: 1.125rem;
          flex: 1;
        }

        .result-postfix {
          font-family: 'Courier New', monospace;
          color: #fbbf24;
          font-size: 1.125rem;
          flex: 1;
        }

        .result-simplified {
          font-family: 'Courier New', monospace;
          color: #4ade80;
          font-size: 1.25rem;
          font-weight: bold;
          flex: 1;
          text-shadow: 0 0 10px rgba(74, 222, 128, 0.3);
        }

        .result-value {
          font-family: 'Courier New', monospace;
          color: #93c5fd;
          flex: 1;
        }

        .section-divider {
          height: 2px;
          background: linear-gradient(to right, transparent, rgba(71, 85, 105, 0.5), transparent);
          margin: 1.5rem 0;
        }

        /* React Flow Custom Styles */
        .react-flow__node {
          background: rgba(168, 85, 247, 0.2);
          border: 2px solid #a855f7;
          border-radius: 8px;
          padding: 10px;
          color: white;
          font-weight: 600;
        }

        .react-flow__edge-path {
          stroke: #60a5fa;
          stroke-width: 2;
        }

        .react-flow__controls {
          background: rgba(30, 41, 59, 0.9);
          border: 1px solid rgba(71, 85, 105, 0.5);
        }

        .react-flow__controls button {
          background: rgba(168, 85, 247, 0.2);
          border-bottom: 1px solid rgba(71, 85, 105, 0.5);
          color: white;
        }

        .react-flow__controls button:hover {
          background: rgba(168, 85, 247, 0.4);
        }

        .react-flow__minimap {
          background: #1e293b;
        }

        .circuit-container {
          height: 500px;
          width: 100%;
          background: #0f172a;
          border-radius: 8px;
          border: 1px solid rgba(71, 85, 105, 0.5);
        }

        .circuit-loading {
          display: flex;
          align-items: center;
          justify-content: center;
          height: 100%;
          color: #9ca3af;
          font-size: 1rem;
        }
      `}</style>

      <div className="app-container">
        <div className="container">
          <div className="header">
            <h1 className="title">LOGIC GATE SIMULATOR</h1>
            <p className="subtitle">Takes an infix expression as input and visualizes its corresponding logic diagram.</p>
          </div>

          <div className="card">
            <div className="form-container">
              <div className="input-group">
                <label htmlFor="expression-input" className="label">
                  Boolean Expression (Infix Notation)
                </label>
                <input
                  id="expression-input"
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="e.g., A+B'C, (A&B)|C, A>B"
                  className="input"
                  disabled={loading}
                  aria-describedby={error ? "error-message" : undefined}
                />
                
                <div className="operator-box">
                  <p className="operator-title">Supported Operators</p>
                  <div className="operator-grid">
                    <div className="operator-item">
                      <span className="operator-label">NOT</span>
                      <span className="operator-symbols">~, !, '</span>
                    </div>
                    <div className="operator-item">
                      <span className="operator-label">AND</span>
                      <span className="operator-symbols">&, ., *</span>
                    </div>
                    <div className="operator-item">
                      <span className="operator-label">OR</span>
                      <span className="operator-symbols">|, +</span>
                    </div>
                    <div className="operator-item">
                      <span className="operator-label">XOR</span>
                      <span className="operator-symbols">^</span>
                    </div>
                    <div className="operator-item">
                      <span className="operator-label">XNOR</span>
                      <span className="operator-symbols">@</span>
                    </div>
                    <div className="operator-item">
                      <span className="operator-label">IMPLIES</span>
                      <span className="operator-symbols">&gt;</span>
                    </div>
                    <div className="operator-item">
                      <span className="operator-label">EQUIV</span>
                      <span className="operator-symbols">=</span>
                    </div>
                  </div>
                </div>
              </div>

              <button
                onClick={handleSimplify}
                disabled={loading || !input.trim()}
                className="button"
                aria-busy={loading}
              >
                {loading ? (
                  <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    Simplifying
                    <span className="loading-dots">
                      <span className="dot"></span>
                      <span className="dot"></span>
                      <span className="dot"></span>
                    </span>
                  </span>
                ) : (
                  "Simplify Expression"
                )}
              </button>
            </div>
          </div>

          {error && (
            <div id="error-message" className="error-box" role="alert">
              <strong className="error-strong">Error: </strong>
              {error}
            </div>
          )}

          {output && (
            <div className="result-box">
              <h2 className="result-title">Results</h2>
              
              <div className="result-container">
                <div className="result-row">
                  <span className="result-label">Infix Input</span>
                  <span className="result-original">{input}</span>
                </div>
                
                {output.postfix && (
                  <div className="result-row">
                    <span className="result-label">Postfix</span>
                    <span className="result-postfix">{output.postfix}</span>
                  </div>
                )}

                <div className="section-divider"></div>
                
                <div className="result-row">
                  <span className="result-label">Simplified SOP</span>
                  <span className="result-simplified">{output.simplified}</span>
                </div>
                
                <div className="result-row">
                  <span className="result-label">Variables</span>
                  <span className="result-value">
                    {output.variables && output.variables.length > 0 
                      ? output.variables.join(", ") 
                      : "None"}
                  </span>
                </div>
                
                {output.minterms && output.minterms.length > 0 && (
                  <div className="result-row">
                    <span className="result-label">Minterms</span>
                    <span className="result-value">{output.minterms.join(", ")}</span>
                  </div>
                )}

                {(rfNodes.length > 0 || circuitLoading) && (
                  <>
                    <div className="section-divider"></div>
                    <div className="result-row" style={{ flexDirection: 'column', alignItems: 'stretch', padding: '1.5rem' }}>
                      <span className="result-label" style={{ marginBottom: '1rem' }}>Logic Circuit</span>
                      <div className="circuit-container">
                        {circuitLoading ? (
                          <div className="circuit-loading">
                            <span>Loading circuit</span>
                            <span className="loading-dots">
                              <span className="dot"></span>
                              <span className="dot"></span>
                              <span className="dot"></span>
                            </span>
                          </div>
                        ) : (
                          <ReactFlow
                            nodes={rfNodes}
                            edges={rfEdges}
                            fitView
                            attributionPosition="bottom-right"
                          >
                            <Background color="#475569" gap={16} />
                            <Controls />
                            <MiniMap 
                              nodeColor={() => '#a855f7'} 
                              maskColor="rgba(0, 0, 0, 0.6)"
                            />
                          </ReactFlow>
                        )}
                      </div>
                    </div>
                  </>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}

export default Home;