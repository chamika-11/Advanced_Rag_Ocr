import datetime
import json
import logging
import traceback
import uuid
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from ocr_engine import extract_text
from classifier import train_document_classifier
from classifier import predict_document_type
from torchvision.datasets import ImageFolder
from extract import extract_structured_data
from datetime import datetime
import traceback
from typing import Optional
from pdf2image import convert_from_bytes
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import os
from datetime import datetime
from typing import List
from chunk import chunk_text
from vector_store import save_vector_index, store_document,hybrid_search
import uuid
from langchain.docstore.document import Document
from langchain_together import Together
from langchain.chains.question_answering import load_qa_chain
from fastapi import Form
from vector_store import load_vector_index
from preprocess import preprocess_image
import cv2
from vector_store import load_vector_index, save_vector_index, store_document
from agentic_rag import create_agentic_rag_system
from contextlib import asynccontextmanager
from fastapi import FastAPI
from langchain_together import Together
import re

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize everything on startup."""
    global agentic_system
    
    # Load existing vector index
    load_vector_index()
    
    dataset = ImageFolder("data/classification")
    class_labels = dataset.classes

    train_document_classifier()
    
    # Create directories
    os.makedirs("storage/docs", exist_ok=True)
    os.makedirs("storage/conversations", exist_ok=True)
    
    # Initialize agentic RAG system
    agentic_system = create_agentic_rag_system()
    
    logging.info("Agentic RAG system initialized successfully")

    llm = Together(model="meta-llama/Llama-3-8b-instruct") 
    chain = load_qa_chain(llm, chain_type="stuff")
    
    yield #for cleanup


app = FastAPI(lifespan=lifespan)

# app = FastAPI(title="Agentic RAG Document Processing")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agentic_system = None



@app.post("/upload-document/")
async def upload_document(files: List[UploadFile] = File(...)):
    """
    Upload multiple documents (PDFs or images). For PDFs, process all pages.
    Extract raw text + structured data for each, and save as individual JSONs.
    """
    results = []

    for file in files:
        try:
            file_bytes = await file.read()
            ext = file.filename.split(".")[-1].lower()
            # giving unique id per file
            unique_id = str(uuid.uuid4())

            combined_text = ""
            doc_type = "unknown"  # Initialize doc_type
            class_labels = ["forms", "invoice", "text"]

            if ext == "pdf":
                images = convert_from_bytes(file_bytes, poppler_path="C:/Program Files/poppler-24.08.0/Library/bin")
                for i, img in enumerate(images):
                    temp_img_path = f"tempFile_{unique_id}_page_{i}.jpg"
                    img.save(temp_img_path, "JPEG")

                    preprocessed = preprocess_image(temp_img_path)
                    cv2.imwrite(temp_img_path, preprocessed)

                    page_text = extract_text(temp_img_path)
                    combined_text += page_text + "\n\n"
                    os.remove(temp_img_path)

                # use first page for classification
                first_page_path = f"temp_{unique_id}_page_0.jpg"
                images[0].save(first_page_path, "JPEG")
                doc_type = predict_document_type(first_page_path, class_labels=class_labels)
                os.remove(first_page_path)

            else:
                temp_img_path = f"temp_{unique_id}.jpg"

                with open(temp_img_path, "wb") as f:
                    f.write(file_bytes)

                preprocessed = preprocess_image(temp_img_path)
                cv2.imwrite(temp_img_path, preprocessed)

                combined_text = extract_text(temp_img_path)
                doc_type = predict_document_type(temp_img_path, class_labels=class_labels)

                os.remove(temp_img_path)

            # Extract structured data
            structured_data = extract_structured_data(combined_text)

            # Generate document ID
            doc_id = str(uuid.uuid4())

            # Store in vector database
            chunks = chunk_text(combined_text, max_words=300)
            for chunk in chunks:
                store_document(doc_id, chunk, metadata={  
                    "filename": file.filename,
                    "doc_type": doc_type,
                })

            # Store permanently
            filename = f"{doc_type}_{doc_id}.json"
            filepath = os.path.join("storage/docs", filename)

            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            document_data = {
                "doc_id": doc_id,
                "document_type": doc_type,
                "raw_text": combined_text,
                "structured_data": structured_data,
                "created_at": datetime.now().isoformat()
            }

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(document_data, f, ensure_ascii=False, indent=2)

            # Add result to results list - THIS WAS MISSING!
            results.append({
                "filename": file.filename,
                "doc_id": doc_id,
                "document_type": doc_type,
                "structured_data": structured_data,
                "text_preview": combined_text[:200] + "..." if len(combined_text) > 200 else combined_text,
                "status": "success",
                "filepath": filepath
            })

        except Exception as e:
            # Add error result if processing fails
            results.append({
                "filename": file.filename,
                "status": "error",
                "error_message": str(e)
            })

    # Save vector index
    save_vector_index()
    
    return {
        "message": f"{len(files)} document(s) processed successfully.",
        "results": results
    }


@app.post("/agentic-chat/")
async def agentic_chat(
    question: str = Form(...),
    conversation_id: Optional[str] = Form(None)
):
    """
    Advanced agentic RAG chat endpoint with conversation memory.
    """
    try:
        if not question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty.")
        
        global agentic_system
        if not agentic_system:
            raise HTTPException(status_code=500, detail="Agentic RAG system not initialized.")
        
        # Generate conversation ID if not provided
        if not conversation_id:
            conversation_id = str(uuid.uuid4())

        # Use the agentic RAG system
        result = agentic_system["query_router"].route_query(question)

        # Log the conversation
        conversation_log = {
            "conversation_id": conversation_id,
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "answer": result["answer"],
            "query_type": result.get("query_type", "unknown"),
            "success": result.get("success", True),
            "metadata": {
                "sources": result.get("sources", 0)
            }
        }

        # Save conversation log
        log_path = f"storage/conversations/{conversation_id}.jsonl"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(conversation_log) + "\n")

        return {
            "conversation_id": conversation_id,
            "answer": str(result.get("answer", "No answer found.")),
            "query_type": result.get("query_type", "unknown"),
            "success": result.get("success", True),
            "timestamp": conversation_log["timestamp"],
            "sources": result.get("sources", 0)
        }

    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        logging.error("Error in agentic chat: %s", traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail={
                "message": "An internal error occurred while processing your request.",
                "error": str(e)
            }
        )


@app.get("/system-status/")
async def get_system_status():
    """Get the status of the agentic RAG system."""
    try:
        global agentic_system
        from vector_store import doc_metadata

        system_ready = agentic_system is not None and "agentic_rag" in agentic_system
        available_tools = []
        if system_ready:
            try:
                available_tools = [tool.name for tool in agentic_system["agentic_rag"].tools]
            except Exception:
                available_tools = []

        status = {
            "system_initialized": system_ready,
            "total_documents": len(doc_metadata) if doc_metadata else 0,
            "available_tools": available_tools,
            "memory_active": True,
            "timestamp": datetime.now().isoformat()
        }
        return status

    except Exception as e:
        import traceback
        print("System Status Error:", traceback.format_exc())
        return {
            "error": f"Failed to get system status: {str(e)}",
            "system_initialized": False,
            "total_documents": 0,
            "available_tools": [],
            "memory_active": False
        }


@app.get("/search/")
async def search_documents(query: str, top_k: int = 5):
    """
    Semantic search across all uploaded documents using FAISS.
    Returns the top_k most relevant chunks.
    """
    try:
        from vector_store import index, embedding_model, doc_metadata

        if not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty.")

        # Convert query into embedding
        query_vector = embedding_model.encode([query])

        # Search in FAISS index
        distances, indices = index.search(query_vector, top_k)

        results = []
        for rank, idx in enumerate(indices[0]):
            if idx == -1 or idx >= len(doc_metadata):
                continue
            metadata = doc_metadata[idx]
            results.append({
                "rank": rank + 1,
                "doc_id": metadata.get("doc_id"),
                "filename": metadata.get("filename"),
                "document_type": metadata.get("doc_type", "unknown"),
                "score": float(distances[0][rank]),
            })

        return {
            "query": query,
            "results_found": len(results),
            "results": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in semantic search: {str(e)}")
    

@app.get("/get-document/{doc_id}")
async def get_document(doc_id: str):
    """
    Retrieve full details of a document by doc_id.
    Includes raw text, structured data, metadata, and timestamps.
    """
    try:
        found_file = None
        for filename in os.listdir("storage/docs"):
            if doc_id in filename:   # match by substring
                found_file = filename
                break

        if not found_file:
            raise HTTPException(status_code=404, detail=f"Document with ID {doc_id} not found")

        filepath = os.path.join("storage/docs", found_file)
        with open(filepath, "r", encoding="utf-8") as f:
            doc_data = json.load(f)

        # Load vector metadata if available
        from vector_store import doc_metadata
        vector_meta = next((m for m in doc_metadata if m.get("doc_id") == doc_id), None)

        return {
            "doc_id": doc_id,
            "filename": found_file,
            "document_type": doc_data.get("document_type", "unknown"),
            "raw_text": doc_data.get("raw_text", ""),
            "structured_data": doc_data.get("structured_data", {}),
            "created_at": doc_data.get("created_at"),
            "metadata": vector_meta or {}
        }

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print("Error in get_document:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error retrieving document: {str(e)}")
    

@app.get("/keyword-search/")
async def keyword_search(keyword: str):
    """
    Search documents for a keyword and return only the matching snippets.
    """
    try:
        results = []
        keyword_lower = keyword.lower()

        for filename in os.listdir("storage/docs"):
            filepath = os.path.join("storage/docs", filename)

            with open(filepath, "r", encoding="utf-8") as f:
                doc_data = json.load(f)

            raw_text = doc_data.get("raw_text", "")
            raw_text_lower = raw_text.lower()

            if keyword_lower in raw_text_lower:
                # Extract matching sentences/snippets
                pattern = re.compile(r".{0,50}" + re.escape(keyword_lower) + r".{0,50}", re.IGNORECASE)
                matches = pattern.findall(raw_text)

                results.append({
                    "doc_id": doc_data.get("doc_id"),
                    "filename": filename,
                    "document_type": doc_data.get("document_type", "unknown"),
                    "created_at": doc_data.get("created_at"),
                    "matches": matches,  # show only relevant snippets
                    "structured_data": doc_data.get("structured_data", {})
                })

        if not results:
            raise HTTPException(status_code=404, detail=f"No documents found containing '{keyword}'")

        return {
            "keyword": keyword,
            "results_found": len(results),
            "results": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in keyword search: {str(e)}")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
