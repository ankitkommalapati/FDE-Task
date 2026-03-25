import React, { useEffect, useState, useRef } from "react";
import ForceGraph2D from "react-force-graph-2d";
import axios from "axios";
import ReactMarkdown from "react-markdown";

const BACKEND = "http://127.0.0.1:8000";

function App() {
  const [graph, setGraph] = useState({ nodes: [], links: [] });
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [highlightedNodes, setHighlightedNodes] = useState(new Set());
  const [loading, setLoading] = useState(false);
  const [controller, setController] = useState(null);

  const chatEndRef = useRef(null);

  const extractIds = (text) => {
    return text.match(/\d{6,}/g) || [];
  };

  // 🔥 Auto scroll
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // 🔥 Load graph
  useEffect(() => {
    axios.get(`${BACKEND}/graph/sample`).then((res) => {
      const nodes = res.data.nodes.map((n) => ({
        id: n.id,
        type: n.type
      }));

      setGraph({ nodes, links: [] });
    });
  }, []);

  // 🔥 Expand graph
  const handleNodeClick = async (node) => {
    const res = await axios.get(`${BACKEND}/graph/expand/${node.id}`);

    const newNodes = res.data.nodes.map((n) => ({
      id: n.id,
      type: n.type
    }));

    const newLinks = res.data.edges.map((e) => ({
      source: e.source,
      target: e.target
    }));

    setGraph((prev) => ({
      nodes: [...prev.nodes, ...newNodes],
      links: [...prev.links, ...newLinks]
    }));
  };

  // 🔥 Send query
  const sendQuery = async () => {
    if (!input.trim() || loading) return;

    const abortController = new AbortController();
    setController(abortController);
    setLoading(true);

    const userMsg = { role: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);

    try {
      const res = await axios.post(
        `${BACKEND}/query`,
        { query: input },
        { signal: abortController.signal }
      );

      const answer = res.data.answer || res.data.error;

      // 🔥 Highlight graph nodes
      const ids = extractIds(answer);
      setHighlightedNodes(new Set(ids));

      const botMsg = {
        role: "bot",
        text: answer,
        sql: res.data.sql,
        showSQL: false
      };

      setMessages((prev) => [...prev, botMsg]);

    } catch (err) {
      if (err.name !== "CanceledError") {
        setMessages((prev) => [
          ...prev,
          { role: "bot", text: "Something went wrong." }
        ]);
      }
    }

    setLoading(false);
    setInput("");
  };

  return (
    <div style={{ display: "flex", height: "100vh" }}>

      {/* LEFT: GRAPH */}
      <div style={{ flex: 3 }}>
        <ForceGraph2D
          graphData={graph}
          width={window.innerWidth * 0.7}
          height={window.innerHeight}
          nodeLabel="id"
          onNodeClick={handleNodeClick}
          nodeCanvasObject={(node, ctx, globalScale) => {
            const label = node.id;
            const fontSize = 15 / globalScale;
            ctx.font = `${fontSize}px Sans-Serif`;

            const isHighlighted = highlightedNodes.has(String(node.id));

            ctx.fillStyle = isHighlighted ? "#ef4444" : "#2563eb";

            ctx.beginPath();
            ctx.arc(node.x, node.y, isHighlighted ? 8 : 5, 0, 2 * Math.PI);
            ctx.fill();

            ctx.fillStyle = "#111";
            ctx.fillText(label, node.x + 8, node.y + 3);
          }}
        />
      </div>

      {/* RIGHT: CHAT PANEL */}
      <div
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          background: "#f4f6f8",
          padding: "12px"
        }}
      >

        {/* CHAT CARD */}
        <div
          style={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            background: "white",
            borderRadius: "16px",
            boxShadow: "0 4px 20px rgba(0,0,0,0.08)",
            overflow: "hidden"
          }}
        >

          {/* CHAT HISTORY */}
          <div style={{ flex: 1, overflowY: "auto", padding: "15px" }}>
            {messages.map((msg, i) => (
              <div
                key={i}
                style={{
                  display: "flex",
                  justifyContent: msg.role === "user" ? "flex-end" : "flex-start",
                  marginBottom: "12px"
                }}
              >
                <div
                  style={{
                    padding: "12px 14px",
                    borderRadius: "14px",
                    background: msg.role === "user" ? "#1f2937" : "#f1f5f9",
                    color: msg.role === "user" ? "white" : "#111",
                    maxWidth: "75%",
                    fontSize: "20px",
                    lineHeight: "1.5",
                    boxShadow: msg.role === "user"
                      ? "0 2px 10px rgba(0,0,0,0.2)"
                      : "0 2px 8px rgba(0,0,0,0.05)"
                  }}
                >

                  <ReactMarkdown>
                    {msg.text}
                  </ReactMarkdown>

                  {/* SQL TOGGLE */}
                  {msg.sql && (
                    <div style={{ marginTop: "8px" }}>
                      <button
                        style={{
                          fontSize: "18px",
                          padding: "4px 8px",
                          borderRadius: "6px",
                          border: "none",
                          background: "#e5e7eb",
                          cursor: "pointer"
                        }}
                        onClick={() => {
                          setMessages(prev => {
                            const updated = [...prev];
                            updated[i] = {
                              ...updated[i],
                              showSQL: !updated[i].showSQL
                            };
                            return updated;
                          });
                        }}
                      >
                        {msg.showSQL ? "Hide SQL" : "Show SQL"}
                      </button>

                      {msg.showSQL && (
                        <pre
                          style={{
                            marginTop: "6px",
                            background: "#111",
                            color: "#0f0",
                            padding: "10px",
                            borderRadius: "8px",
                            fontSize: "12px",
                            overflowX: "auto"
                          }}
                        >
                          {msg.sql}
                        </pre>
                      )}
                    </div>
                  )}

                </div>
              </div>
            ))}

            <div ref={chatEndRef} />
          </div>

          {/* INPUT BAR */}
          <div
            style={{
              padding: "12px",
              borderTop: "1px solid #eee",
              background: "#fafafa"
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "10px",
                background: "white",
                padding: "12px",
                borderRadius: "12px",
                boxShadow: "0 2px 10px rgba(0,0,0,0.08)"
              }}
            >
              <input
                value={input}
                disabled={loading}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") sendQuery();
                }}
                placeholder="Ask anything about your data..."
                style={{
                  flex: 1,
                  border: "none",
                  outline: "none",
                  fontSize: "22px",
                  color: "#111",
                  background: "transparent"
                }}
              />

              <button
                onClick={() => {
                  if (loading && controller) {
                    controller.abort();
                    setLoading(false);
                  } else {
                    sendQuery();
                  }
                }}
                style={{
                  fontSize: "18px",
                  padding: "8px 14px",
                  borderRadius: "8px",
                  border: "none",
                  background: loading ? "#ef4444" : "#2563eb",
                  color: "white",
                  cursor: "pointer",
                  fontWeight: "500"
                }}
              >
                {loading ? "Stop" : "Send"}
              </button>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}

export default App;