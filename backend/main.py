from fastapi import FastAPI
from pydantic import BaseModel
from db import run_sql
from llm import generate_sql
from fastapi import HTTPException

app = FastAPI()

class QueryRequest(BaseModel):
    query: str

def is_valid_query(query: str):
    banned = ["drop", "delete", "update", "insert"]
    return not any(word in query.lower() for word in banned)

@app.post("/query")
def query_data(req: QueryRequest):
    user_query = req.query

    # Guardrail: domain check
    if any(x in user_query.lower() for x in ["weather", "poem", "joke"]):
        return {"error": "This system is designed to answer dataset-related questions only."}

    sql = generate_sql(user_query)

    if "INVALID_QUERY" in sql:
        return {"error": "Invalid query for this dataset."}

    if not is_valid_query(sql):
        return {"error": "Unsafe query detected."}

    try:
        result = run_sql(sql)
        return {
            "sql": sql,
            "result": result
        }
    except Exception as e:
        return {
            "error": str(e),
            "sql": sql
        }


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
def sample_nodes():
    return {
        "sales_orders": run_sql("SELECT sales_order FROM sales_orders"),
        "billing_documents": run_sql("SELECT billing_document FROM billing_documents"),
        "journal_entries": run_sql("SELECT accounting_document FROM journal_entries")
    }