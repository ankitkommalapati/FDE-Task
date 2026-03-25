import React, { useEffect, useState } from "react";
import ForceGraph2D from "react-force-graph-2d";
import axios from "axios";

const BACKEND = "http://127.0.0.1:8000";

function App() {
  const [graph, setGraph] = useState({ nodes: [], links: [] });
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);

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

  // 🔥 Send query (CHAT)
  const sendQuery = async () => {
    if (!input) return;

    const userMsg = { role: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);

    try {
      const res = await axios.post(`${BACKEND}/query`, {
        query: input
      });

      const botMsg = {
        role: "bot",
        text: res.data.answer || res.data.error
      };

      setMessages((prev) => [...prev, botMsg]);

    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "bot", text: "Something went wrong." }
      ]);
    }

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
        />
      </div>

      {/* RIGHT: CHAT */}
      <div
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          borderLeft: "1px solid #ccc"
        }}
      >
        {/* CHAT HISTORY */}
        <div style={{ flex: 1, overflowY: "auto", padding: "10px" }}>
          {messages.map((msg, i) => (
            <div
              key={i}
              style={{
                textAlign: msg.role === "user" ? "right" : "left",
                margin: "10px"
              }}
            >
              <div
                style={{
                  display: "inline-block",
                  padding: "10px",
                  borderRadius: "10px",
                  background: msg.role === "user" ? "#333" : "#eee",
                  color: msg.role === "user" ? "white" : "black"
                }}
              >
                {msg.text}
              </div>
            </div>
          ))}
        </div>

        {/* INPUT BAR */}
        <div style={{ padding: "10px", borderTop: "1px solid #ccc" }}>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") sendQuery();
            }}
            placeholder="Ask something..."
            style={{ width: "80%", padding: "10px" }}
          />

          <button onClick={sendQuery} style={{ marginLeft: "10px" }}>
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;