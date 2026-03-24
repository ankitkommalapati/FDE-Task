from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_sql(user_query: str):
    prompt = f"""
You are a PostgreSQL expert working on an Order-to-Cash dataset.

STRICT RULES:
- Only use given tables
- Do NOT hallucinate columns
- Return ONLY SQL
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

    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()