from pymilvus import MilvusClient
client = MilvusClient(uri="http://localhost:19530")

# Load before querying
client.load_collection(collection_name="bcm_docs")

# Optional: wait for load (best-effort)
# print(client.get_load_state(collection_name="bcm_docs"))

# Query a few rows (use a non-empty filter)
rows = client.query(
    collection_name="bcm_docs",
    filter="id >= 0",
    output_fields=["file_name", "source", "text"],
    limit=3,
)
print(rows)
