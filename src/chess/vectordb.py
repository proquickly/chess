# pip install chromadb
import pprint
import re
import chromadb
from chromadb.config import Settings
import json
from transformers import AutoTokenizer, AutoModel
import torch
import os

RELOAD_DB = False

# 1) Get the absolute directory containing this script (vectordb.py).
current_dir = os.path.dirname(os.path.abspath(__file__))

# 2) Build a path two levels up (.., ..) into data/, then chroma.db.
db_path = os.path.join(current_dir, "..", "..", "data", "chroma.db")

# 3) Initialize the PersistentClient with the absolute path.
chroma_client = chromadb.PersistentClient(
    path=db_path,
    settings=Settings(
        anonymized_telemetry=False
    )
)

collection = chroma_client.get_or_create_collection(name="chess")

tokenizer = AutoTokenizer.from_pretrained(
    "sentence-transformers/all-MiniLM-L6-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")


def generate_embedding(text):
    inputs = tokenizer(text, return_tensors="pt",
                       truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    embedding = outputs.last_hidden_state.mean(dim=1).squeeze().tolist()
    # print(f"Generated embedding: {embedding}")
    return embedding


import os
import re


def query_source_data():
    # Get the absolute directory where this file (vectordb.py) is located
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Navigate two levels up to reach the main "chess" folder, then go into "data/info.txt"
    info_path = os.path.join(current_dir, "..", "..", "data", "info.txt")

    # For debugging, print out the path to ensure it's correct
    print("Loading info from:", info_path)

    with open(info_path, "r", encoding="utf-8") as f:
        content = f.read()

    chess_moves = content.split("\n")
    return [re.sub(' +', ' ', chess_move.replace("\n", "")) for chess_move in chess_moves]


def query_source_data_inline():
    return [
        [("drink", "good"), "This is cola"],
        [("food", "good"), "This is fish and chips"],
        [("drink", "bad"), "This is a wine"],
        [("drink", "bad"), "This is beer"],
    ]


def load_data(results: list) -> None:
    documents = [{"text": text, "labels": labels} for labels, text in results]
    ids = [f"id{num}" for num in range(1, len(documents) + 1)]
    embeddings = [generate_embedding(doc["text"]) for doc in documents]
    documents_json = [json.dumps(doc) for doc in documents]
    # print(f"Upserting documents: {documents_json}")
    # print(f"With embeddings: {embeddings}")
    collection.upsert(
        documents=documents_json,
        ids=ids,
        embeddings=embeddings
    )


def run_query(query: str):
    # note collection query return shows embeddings as None
    # but per chromadb this is for performance
    # now shifted to creating and returning more_results
    # need to investigate if metadata can be useful
    query_embedding = generate_embedding(query)
    collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )
    more_results = collection.get(
        include=['embeddings', 'documents', 'metadatas'])
    return more_results


def main():
    if RELOAD_DB:
        #results = query_source_data_inline()
        results = query_source_data()
        load_data(results)
    questions = [
        "what is a good",
    ]
    for question in questions:
        findings = run_query(question)
        print(question)
        pprint.pprint(findings)
        print("-" * len(question), "\n")


if __name__ == "__main__":
    main()
