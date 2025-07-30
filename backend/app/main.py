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
from langchain_community.llms import Together
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

    llm = Together(model="mistralai/Mistral-7B-Instruct-v0.1") 
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
    results =[]

    for file in files:
        file_bytes = await file.read()
        ext = file.filename.split(".")[-1].lower()
        #giving unique id per file
        unique_id = str(uuid.uuid4())

        combined_text=""

        if ext=="pdf":
            images=convert_from_bytes(file_bytes,poppler_path="C:/Program Files/poppler-24.08.0/Library/bin")
            for i,img in enumerate(images):
                temp_img_path=f"tempFile_{unique_id}_page_{i}.jpg"
                img.save(temp_img_path,"JPEG")

                preprocessed=preprocess_image(temp_img_path)
                cv2.imwrite(temp_img_path,preprocessed)

                page_text=extract_text(temp_img_path)
                combined_text+=page_text+"\n\n"
                os.remove(temp_img_path)
                class_labels = ["forms", "invoice", "text"]

            #use first page for classification
            first_page_path=f"temp_{unique_id}_page_0.jpg"
            images[0].save(first_page_path,"JPEG")
            doc_type=predict_document_type(first_page_path,class_labels=class_labels)
            os.remove(first_page_path)

        else:
            temp_img_path=f"temp_{unique_id}.jpg"

            with open(temp_img_path,"wb") as f:
                f.write(file_bytes)

            preprocessed=preprocess_image(temp_img_path)
            cv2.imwrite(temp_img_path,preprocessed)

            combined_text=extract_text(temp_img_path)
            doc_type = predict_document_type(temp_img_path, class_labels=class_labels)

            os.remove(temp_img_path)


        structured_data=extract_structured_data(combined_text)

        doc_id=str(uuid.uuid4())


        chunks=chunk_text(combined_text,max_words=300)
        for chunk in chunks:
            store_document(str(uuid.uuid4()),chunk,metadata={
                "filename":file.filename,
                "doc_type":doc_type,
            })

        #store permanetly
        filename = f"{doc_type}_{doc_id}.json"
        filepath=os.path.join("storage/docs",filename)

        

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump({
                "document_type":doc_type,
                "raw_text":combined_text,
                "structured_data":structured_data,
                "created_at": datetime.now().isoformat()
            },f,ensure_ascii=False,indent=2)

            results.append({
                "file":file.filename,
                "document_type":doc_type,
                "structured_data":structured_data
            })
            
    save_vector_index()
    
    return {
        "message": f"{len(files)} document(s) processed successfully.",
        "results": results
    }
    pass


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
        
        # Count documents
        from vector_store import doc_metadata
        
        status = {
            "system_initialized": agentic_system is not None,
            "total_documents": len(doc_metadata) if doc_metadata else 0,
            "available_tools": [tool.name for tool in agentic_system["agentic_rag"].tools] if agentic_system else [],
            "memory_active": True,
            "timestamp": datetime.now().isoformat()
        }
        
        return status
        
    except Exception as e:
        return {
            "error": f"Failed to get system status: {str(e)}",
            "system_initialized": False
        }

@app.get("/query-examples/")
async def get_query_examples():
    """Get example queries for different types of interactions."""
    return {
        "simple_queries": [
            "What is the main topic of document X?",
            "Find information about safety protocols",
            "What documents do I have uploaded?"
        ],
        "complex_queries": [
            "Compare the safety protocols mentioned in document A with those in document B and explain the key differences",
            "Analyze the financial data across all uploaded documents and summarize the trends",
            "What are the step-by-step procedures mentioned in the technical manual and how do they relate to the compliance requirements?"
        ],
        "metadata_queries": [
            "Show me all PDF documents",
            "Find documents uploaded today",
            "What types of documents are available?"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
