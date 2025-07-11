from sentence_transformers import SentenceTransformer
import faiss
import os
import json


#load the sentence transformer model
embedding_model=SentenceTransformer('all-MiniLM-L6-v2')

#faiss index 
embedding_dim=384
index=faiss.IndexFlatL2(embedding_dim)

#storage for metadata
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


###################
def save_vector_index(path="faiss_index.index", meta_path="doc_metadata.json"):
    faiss.write_index(index, path)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(doc_metadata, f, ensure_ascii=False, indent=2)


def load_vector_index(path="faiss_index.index", meta_path="doc_metadata.json"):
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


def hybrid_search (query, top_k=3):
    sem_results=search_documents(query, top_k=top_k)

    #keyword filtering
    keyword_matches=[]
    for doc in doc_metadata:
        if query.lower() in doc["text"].lower():
            keyword_matches.append(doc)


    unique_results={doc["doc_id"]:doc for doc in sem_results+keyword_matches}

    return list(list(unique_results.values())[:top_k])

