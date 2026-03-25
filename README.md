# Graph + LLM Query Assistant

An interactive full-stack application that combines **LLMs, SQL querying, and graph visualization** to explore business data in a conversational way.

---

## Overview

This project allows users to:

- Ask natural language questions about data
- Automatically convert queries → SQL using an LLM
- Execute queries on a PostgreSQL database
- Visualize relationships using an interactive graph
- Chat with the system in a conversational interface
- Highlight graph nodes based on query results

---

## Features

### Conversational AI Interface
- Chat-style UI (like ChatGPT)
- Maintains conversation history
- Human-readable responses (not raw SQL)

### LLM → SQL Engine
- Converts natural language → SQL
- Executes queries safely
- Optional SQL toggle for transparency

### Graph Visualization
- Interactive graph using `react-force-graph`
- Click nodes to expand relationships
- Dynamically grows based on user interaction

### Chat → Graph Integration
- Extracts IDs from responses
- Automatically highlights relevant nodes in graph

### UX Enhancements
- "Thinking..." loading state
- Stop button to cancel requests
- Auto-scroll chat

---

## Tech Stack

### Frontend
- React.js
- Axios
- React Markdown
- React Force Graph

### Backend
- FastAPI
- PostgreSQL
- Psycopg2

### AI Layer
- Groq API (LLM)
- LLM-based SQL generation + response formatting

### Deployment
- Frontend → Vercel
- Backend → Render

---

## ⚙️ Setup Instructions

### Clone the Repository

```bash
git clone https://github.com/ankitkommalapatu/FDE-Task.git
```

### Backend Setup (FastAPI)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

### Environment Variables

Create .env:
```bash
DATABASE_URL=your_postgres_url
GROQ_API_KEY=your_api_key
```

### Run Backend

```bash
uvicorn main:app --reload
```

Backend runs on: http://127.0.0.1:8000

### Frontend Setup (React)

```bash
cd frontend
npm install
```

### Configure Backend URL

In App.js :
```bash
const BACKEND = "http://127.0.0.1:8000";
```

### Run Frontend

```bash
npm start
```
Frontend runs on: http://localhost:3000


## Deployment

### Backend (Render)
* Create Web Service
* Start command:
```bash
uvicorn main:app --host 0.0.0.0 --port 10000
```

### Frontend (Vercel)
* Import repo
* Set:
```bash
REACT_APP_BACKEND_URL=https://your-backend-url.onrender.com
```
