from fastapi import FastAPI
from pydantic import BaseModel
from db import run_sql
from llm import generate_sql

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