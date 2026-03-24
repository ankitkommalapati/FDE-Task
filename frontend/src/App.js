import React, { useEffect, useState } from "react";
import ForceGraph2D from "react-force-graph-2d";
import axios from "axios";

const BACKEND = "http://127.0.0.1:8000";

function App() {
  const [graph, setGraph] = useState({ nodes: [], links: [] });
  const [query, setQuery] = useState("");
  const [result, setResult] = useState(null);

  // 🔥 Load initial graph
  useEffect(() => {
    axios.get(`${BACKEND}/graph/sample`).then((res) => {
      const nodes = res.data.map((d) => ({
        id: d.billing_document,
        type: "Billing"
      }));

      setGraph({ nodes, links: [] });
    });
  }, []);

  // 🔥 Expand node
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

  // 🔥 Query API
  const handleQuery = async () => {
    const res = await axios.post(`${BACKEND}/query`, { query });
    setResult(res.data);
  };

  return (
    <div style={{ display: "flex", height: "100vh" }}>
      
      {/* LEFT: GRAPH */}
      <div style={{ flex: 2, borderRight: "1px solid #ddd" }}>
        <ForceGraph2D
          graphData={graph}
          nodeLabel="id"
          onNodeClick={handleNodeClick}
        />
      </div>

      {/* RIGHT: CHAT PANEL */}
      <div style={{ flex: 1, padding: "20px" }}>
        <h3>Query</h3>

        <input
          style={{ width: "100%", padding: "10px" }}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask something..."
        />

        <button onClick={handleQuery} style={{ marginTop: "10px" }}>
          Ask
        </button>

        {result && (
          <div style={{ marginTop: "20px" }}>
            <h4>SQL</h4>
            <pre>{result.sql}</pre>

            <h4>Result</h4>
            <pre>{JSON.stringify(result.result, null, 2)}</pre>
          </div>
        )}
      </div>

    </div>
  );
}

export default App;