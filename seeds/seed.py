from pymongo import MongoClient, ASCENDING
from bson import json_util
import os, pathlib

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGODB_DB", "theatersdb")
FILE = pathlib.Path(__file__).with_name("theaters.json")

def main():
    client = MongoClient(MONGODB_URI)
    db = client[DB_NAME]
    col = db["theaters"]
    col.create_index([("slug", ASCENDING)], unique=True)
    col.create_index([("location", "2dsphere")])
    data = json_util.loads(FILE.read_text(encoding="utf-8"))
    col.delete_many({})
    col.insert_many(data)
    print(f"Seeded {col.count_documents({})} theaters into '{DB_NAME}.theaters'")

if __name__ == "__main__":
    main()