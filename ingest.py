import json
import os
from datetime import datetime
import psycopg2
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DB_URL)
cur = conn.cursor()

def get_all_jsonl_files(folder_path):
    files = []
    for root, _, filenames in os.walk(folder_path):
        for file in filenames:
            if file.endswith(".jsonl"):
                files.append(os.path.join(root, file))
    return files

def parse_date(date_str):
    if not date_str:
        return None
    return datetime.fromisoformat(date_str.replace("Z", ""))


def ingest_sales_orders(folder_path):
    files = get_all_jsonl_files(folder_path)

    for file_path in files:
        with open(file_path, "r") as f:
            for line in tqdm(f, desc=f"Sales Orders ({file_path})"):
                row = json.loads(line)

                cur.execute("""
                    INSERT INTO sales_orders VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (sales_order) DO NOTHING
                """, (
                    row.get("salesOrder"),
                    row.get("soldToParty"),
                    parse_date(row.get("creationDate")),
                    float(row.get("totalNetAmount", 0)),
                    row.get("transactionCurrency")
                ))

    conn.commit()


def ingest_billing_items(folder_path):
    files = get_all_jsonl_files(folder_path)

    for file_path in files:
        with open(file_path, "r") as f:
            for line in tqdm(f, desc=f"Billing Items ({file_path})"):
                row = json.loads(line)

            cur.execute("""
                INSERT INTO billing_document_items VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                row.get("billingDocument"),
                row.get("billingDocumentItem"),
                row.get("material"),
                float(row.get("netAmount", 0)),
                row.get("transactionCurrency"),
                row.get("referenceSdDocument")
            ))

    conn.commit()


def ingest_billing_docs(folder_path):
    files = get_all_jsonl_files(folder_path)

    for file_path in files:
        with open(file_path, "r") as f:
            for line in tqdm(f, desc=f"Billing Docs ({file_path})"):
                row = json.loads(line)

            cur.execute("""
                INSERT INTO billing_documents VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (billing_document) DO NOTHING
            """, (
                row.get("billingDocument"),
                parse_date(row.get("billingDocumentDate")),
                float(row.get("totalNetAmount", 0)),
                row.get("transactionCurrency"),
                row.get("accountingDocument"),
                row.get("soldToParty")
            ))

    conn.commit()


def ingest_journal_entries(folder_path):
    files = get_all_jsonl_files(folder_path)

    for file_path in files:
        with open(file_path, "r") as f:
            for line in tqdm(f, desc=f"Journal Entries ({file_path})"):
                row = json.loads(line)

            cur.execute("""
                INSERT INTO journal_entries VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                row.get("accountingDocument"),
                row.get("referenceDocument"),
                float(row.get("amountInTransactionCurrency", 0)),
                row.get("transactionCurrency"),
                row.get("customer"),
                row.get("clearingAccountingDocument")
            ))

    conn.commit()


if __name__ == "__main__":
    BASE_PATH = "/Users/ankitkommalapati/Downloads/sap-o2c-data"

    ingest_sales_orders(f"{BASE_PATH}/sales_order_headers")
    ingest_billing_items(f"{BASE_PATH}/billing_document_items")
    ingest_billing_docs(f"{BASE_PATH}/billing_document_headers")
    ingest_journal_entries(f"{BASE_PATH}/journal_entry_items_accounts_receivable")

    cur.close()
    conn.close()

    print("✅ Data ingestion complete!")