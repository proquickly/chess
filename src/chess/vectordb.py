# pip install chromadb
import pprint
import re
import chromadb
from chromadb.config import Settings
import json
from transformers import AutoTokenizer, AutoModel
import torch

RELOAD_DB = True

chroma_client = chromadb.PersistentClient(path="data/chroma.db",
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


def query_source_data():
    with open("data/chroma.db/info.txt") as f:
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
