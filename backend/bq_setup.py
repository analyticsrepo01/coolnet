"""Run once to create BigQuery dataset, tables, and seed product catalog."""
import json
from datetime import datetime, timezone
from google.cloud import bigquery
from config import PROJECT_ID, BQ_DATASET, USERS, BQ_LOCATION
from products import PRODUCTS

client = bigquery.Client(project=PROJECT_ID)
dataset_ref = bigquery.Dataset(f"{PROJECT_ID}.{BQ_DATASET}")


def create_dataset():
    try:
        dataset_ref.location = BQ_LOCATION
        client.create_dataset(dataset_ref, exists_ok=True)
        print(f"✓ Dataset {BQ_DATASET} ready")
    except Exception as e:
        print(f"Dataset error: {e}")


SCHEMAS = {
    "users": [
        bigquery.SchemaField("user_id",       "STRING",    mode="REQUIRED"),
        bigquery.SchemaField("name",           "STRING"),
        bigquery.SchemaField("email",          "STRING"),
        bigquery.SchemaField("loyalty_tier",   "STRING"),
        bigquery.SchemaField("total_spend",    "FLOAT64"),
        bigquery.SchemaField("created_at",     "STRING"),
        bigquery.SchemaField("updated_at",     "STRING"),
    ],
    "sessions": [
        bigquery.SchemaField("session_id",  "STRING",  mode="REQUIRED"),
        bigquery.SchemaField("user_id",     "STRING"),
        bigquery.SchemaField("started_at",  "STRING"),
        bigquery.SchemaField("ended_at",    "STRING"),
        bigquery.SchemaField("agents_used", "STRING",  mode="REPEATED"),
        bigquery.SchemaField("outcome",     "STRING"),
        bigquery.SchemaField("satisfaction","INT64"),
    ],
    "conversations": [
        bigquery.SchemaField("id",           "STRING", mode="REQUIRED"),
        bigquery.SchemaField("session_id",   "STRING"),
        bigquery.SchemaField("user_id",      "STRING"),
        bigquery.SchemaField("timestamp",    "STRING"),
        bigquery.SchemaField("speaker",      "STRING"),
        bigquery.SchemaField("agent_id",     "STRING"),
        bigquery.SchemaField("message",      "STRING"),
        bigquery.SchemaField("message_type", "STRING"),
    ],
    "agent_handoffs": [
        bigquery.SchemaField("id",          "STRING", mode="REQUIRED"),
        bigquery.SchemaField("session_id",  "STRING"),
        bigquery.SchemaField("from_agent",  "STRING"),
        bigquery.SchemaField("to_agent",    "STRING"),
        bigquery.SchemaField("reason",      "STRING"),
        bigquery.SchemaField("timestamp",   "STRING"),
    ],
    "products": [
        bigquery.SchemaField("sku",           "STRING", mode="REQUIRED"),
        bigquery.SchemaField("name",          "STRING"),
        bigquery.SchemaField("category",      "STRING"),
        bigquery.SchemaField("subcategory",   "STRING"),
        bigquery.SchemaField("price_sgd",     "FLOAT64"),
        bigquery.SchemaField("description",   "STRING"),
        bigquery.SchemaField("specs",         "STRING"),   # JSON string
        bigquery.SchemaField("in_stock",      "BOOL"),
        bigquery.SchemaField("rating",        "FLOAT64"),
        bigquery.SchemaField("review_count",  "INT64"),
        bigquery.SchemaField("specialist_id", "STRING"),
    ],
    "orders": [
        bigquery.SchemaField("order_id",     "STRING", mode="REQUIRED"),
        bigquery.SchemaField("user_id",      "STRING"),
        bigquery.SchemaField("sku",          "STRING"),
        bigquery.SchemaField("quantity",     "INT64"),
        bigquery.SchemaField("price_paid",   "FLOAT64"),
        bigquery.SchemaField("discount_pct", "FLOAT64"),
        bigquery.SchemaField("order_date",   "STRING"),
        bigquery.SchemaField("status",       "STRING"),
    ],
}


def create_tables():
    for name, schema in SCHEMAS.items():
        table_ref = f"{PROJECT_ID}.{BQ_DATASET}.{name}"
        table = bigquery.Table(table_ref, schema=schema)
        try:
            client.create_table(table, exists_ok=True)
            print(f"✓ Table {name} ready")
        except Exception as e:
            print(f"  Table {name} error: {e}")


def seed_users():
    table = f"{PROJECT_ID}.{BQ_DATASET}.users"
    now = datetime.now(timezone.utc).isoformat()
    rows = []
    for uid, u in USERS.items():
        rows.append({
            "user_id": uid, "name": u["name"], "email": u["email"],
            "loyalty_tier": u["loyalty_tier"], "total_spend": 0.0,
            "created_at": now, "updated_at": now,
        })
    errors = client.insert_rows_json(table, rows)
    if errors:
        print(f"  User seed errors: {errors}")
    else:
        print(f"✓ Seeded {len(rows)} users")


def seed_products():
    table = f"{PROJECT_ID}.{BQ_DATASET}.products"
    rows = []
    for sku, p in PRODUCTS.items():
        rows.append({
            "sku":           sku,
            "name":          p["name"],
            "category":      p["category"],
            "subcategory":   p["subcategory"],
            "price_sgd":     float(p["price"]),
            "description":   p["description"],
            "specs":         json.dumps(p["specs"]),
            "in_stock":      p["in_stock"],
            "rating":        p["rating"],
            "review_count":  p["review_count"],
            "specialist_id": p["specialist_id"],
        })
    errors = client.insert_rows_json(table, rows)
    if errors:
        print(f"  Product seed errors: {errors}")
    else:
        print(f"✓ Seeded {len(rows)} products")


def seed_sample_orders():
    """Give each demo user a sample order for richer context."""
    table = f"{PROJECT_ID}.{BQ_DATASET}.orders"
    now = datetime.now(timezone.utc).isoformat()
    rows = [
        {"order_id": "ORD-001", "user_id": "saurabh", "sku": "CN-TV65O",  "quantity": 1, "price_paid": 1499.0, "discount_pct": 0, "order_date": "2026-03-10T10:00:00+00:00", "status": "delivered"},
        {"order_id": "ORD-002", "user_id": "rajan",   "sku": "CN-WF8",    "quantity": 1, "price_paid": 699.0,  "discount_pct": 0, "order_date": "2026-02-15T09:30:00+00:00", "status": "delivered"},
        {"order_id": "ORD-003", "user_id": "vamsi",   "sku": "CN-AC12",   "quantity": 1, "price_paid": 899.0,  "discount_pct": 0, "order_date": "2026-01-20T14:00:00+00:00", "status": "delivered"},
        {"order_id": "ORD-004", "user_id": "saurabh", "sku": "CN-RV1",    "quantity": 1, "price_paid": 399.0,  "discount_pct": 5, "order_date": "2026-04-01T11:00:00+00:00", "status": "delivered"},
    ]
    errors = client.insert_rows_json(table, rows)
    if errors:
        print(f"  Order seed errors: {errors}")
    else:
        print(f"✓ Seeded {len(rows)} sample orders")


if __name__ == "__main__":
    print("\n🚀 Setting up CoolNest BigQuery dataset...\n")
    create_dataset()
    create_tables()
    seed_users()
    seed_products()
    seed_sample_orders()
    print("\n✅ Setup complete!\n")
