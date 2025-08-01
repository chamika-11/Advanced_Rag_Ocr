from sentence_transformers import SentenceTransformer
import faiss
import os
import json
import numpy as np

#load the sentence transformer model
embedding_model=SentenceTransformer('all-MiniLM-L6-v2')

#faiss index 
embedding_dim=384
index=faiss.IndexFlatL2(embedding_dim)

doc_metadata=[]

def store_document(doc_id,text,metadata={}):
    vector=embedding_model.encode([text])
    index.add(vector)
    doc_metadata.append({"doc_id":doc_id,"text":text,"metadata":metadata})


def search_documents(query, top_k=3):
    query_vec = embedding_model.encode([query])
    _, indices = index.search(query_vec, top_k)
    results = []

    for idx in indices[0]:
        if 0 <= idx < len(doc_metadata):
            results.append(doc_metadata[idx])
        else:
            print(f"FAISS returned index {idx}, but doc_metadata only has {len(doc_metadata)} entries")

    return results


def save_vector_index(path="faissFile/faiss_index.index", meta_path="faissFile/faiss_index.json"):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    faiss.write_index(index, path)
    os.makedirs(os.path.dirname(meta_path), exist_ok=True)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(doc_metadata, f, ensure_ascii=False, indent=2)


def load_vector_index(path="faissFile/faiss_index.index", meta_path="faissFile/faiss_index.json"):
    global index, doc_metadata
    if os.path.exists(path):
        index = faiss.read_index(path)
        print(f"Loaded FAISS index with {index.ntotal} vectors")
    else:
        print("FAISS index not found")

    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            doc_metadata = json.load(f)
        print(f"Loaded metadata with {len(doc_metadata)} documents")
    else:
        doc_metadata = []
        print("Metadata file not found")


def hybrid_search (query, top_k=5):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    query_vector=model.encode([query])
    distances, indices=index.search(query_vector,top_k)

    results=[]

    for i,idx in enumerate(indices[0]):
        if idx==-1:
            continue
        score=distances[0][i]
        results.append({
            "text":doc_metadata[idx]["text"],
            "metadata":doc_metadata[idx],
            "score":score
        })

    if not results:
        return None
    
    return results