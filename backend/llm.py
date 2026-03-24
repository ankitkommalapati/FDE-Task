from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_sql(user_query: str):
    prompt = f"""
You are a PostgreSQL expert.

STRICT RULES:
- Return ONLY SQL
- No explanation
- No markdown
- Only use provided tables
- If unrelated → return INVALID_QUERY

TABLES:

sales_orders(sales_order, sold_to_party, creation_date, total_net_amount)

billing_document_items(billing_document, material, net_amount, reference_sales_order)

billing_documents(billing_document, billing_date, accounting_document)

journal_entries(accounting_document, reference_document, amount, customer)

RELATIONSHIPS:

sales_orders.sales_order = billing_document_items.reference_sales_order
billing_document_items.billing_document = billing_documents.billing_document
billing_documents.accounting_document = journal_entries.accounting_document

USER QUERY:
{user_query}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
    except Exception:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}]
        )

    sql = response.choices[0].message.content.strip()

    if "```" in sql:
        sql = sql.split("```")[1]

    return sql.strip()