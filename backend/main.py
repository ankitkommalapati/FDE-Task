from fastapi import FastAPI
from pydantic import BaseModel
from db import run_sql
from llm import generate_sql
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import os
from groq import Groq

DATABASE_URL = os.getenv("DATABASE_URL")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

chat_history = []

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for now allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

def is_valid_query(query: str):
    banned = ["drop", "delete", "update", "insert"]
    return not any(word in query.lower() for word in banned)


def format_response(user_query, result):
    global chat_history

    if not result:
        return "I couldn’t find any matching data."

    try:
        chat_history.append({"role": "user", "content": user_query})

        prompt = f"""
User Query: {user_query}

SQL Result:
{result}

Instructions:
- Be concise and structured
- Use bullet points
- Highlight important numbers using **bold**
- Do NOT explain SQL
- Do NOT add unnecessary commentary

Answer:
"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
        )

        answer = response.choices[0].message.content.strip()

        chat_history.append({"role": "assistant", "content": answer})

        return answer

    except Exception as e:
        print("LLM ERROR:", e)
        return f"I found {len(result)} result(s)."

@app.post("/query")
def query_data(payload: dict):
    try:
        user_query = payload.get("query")

        if not user_query:
            return {"error": "Query is required"}

        sql = generate_sql(user_query)

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(sql)
        columns = [desc[0] for desc in cur.description]
        rows = [dict(zip(columns, row)) for row in cur.fetchall()]

        cur.close()
        conn.close()

        answer = format_response(user_query, rows)

        return {"answer": answer, "sql": sql}

    except Exception as e:
        return {"error": str(e)}


@app.get("/graph/node/{node_id}")
def get_node(node_id: str):

    checks = [
        ("sales_orders", "sales_order"),
        ("billing_documents", "billing_document"),
        ("billing_document_items", "billing_document"),
        ("journal_entries", "accounting_document"),
    ]

    for table, col in checks:
        try:
            result = run_sql(
                f"SELECT * FROM {table} WHERE {col} = '{node_id}' LIMIT 1"
            )
            if result:
                return {
                    "type": table,
                    "data": result[0]
                }
        except Exception as e:
            print(f"Error checking {table}: {e}")

    return {"error": "Node not found", "node_id": node_id}


@app.get("/graph/expand/{node_id}")
def expand_node(node_id: str):

    nodes = []
    edges = []

    # 🔹 Case 1: If node is Sales Order
    so_items = run_sql(f"""
        SELECT billing_document
        FROM billing_document_items
        WHERE reference_sales_order = '{node_id}'
    """)

    for row in so_items:
        bdoc = row["billing_document"]

        nodes.append({"id": bdoc, "type": "Billing"})
        edges.append({
            "source": node_id,
            "target": bdoc,
            "type": "HAS_BILLING"
        })

    # 🔹 Case 2: If node is Billing Document → Journal Entry
    billing_to_journal = run_sql(f"""
        SELECT accounting_document
        FROM billing_documents
        WHERE billing_document = '{node_id}'
    """)

    for row in billing_to_journal:
        acc = row["accounting_document"]

        nodes.append({"id": acc, "type": "JournalEntry"})
        edges.append({
            "source": node_id,
            "target": acc,
            "type": "ACCOUNTED_AS"
        })

    # 🔹 Case 3: Reverse → find Sales Order from Billing
    reverse_so = run_sql(f"""
        SELECT reference_sales_order
        FROM billing_document_items
        WHERE billing_document = '{node_id}'
    """)

    for row in reverse_so:
        so = row["reference_sales_order"]

        nodes.append({"id": so, "type": "SalesOrder"})
        edges.append({
            "source": node_id,
            "target": so,
            "type": "BELONGS_TO_ORDER"
        })

    return {
        "nodes": list({n["id"]: n for n in nodes}.values()),
        "edges": edges
    }


@app.get("/graph/sample")
def get_sample():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT billing_document FROM billing_documents LIMIT 5")
        rows = cur.fetchall()

        nodes = [{"id": str(r[0]), "label": str(r[0])} for r in rows]

        cur.close()
        conn.close()

        return {"nodes": nodes, "edges": []}

    except Exception as e:
        return {"error": str(e)}