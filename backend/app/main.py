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
from rag_chatbot import ask_question
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


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_vector_index()

# Prepare class labels at startup
dataset = ImageFolder("data/classification")
class_labels = dataset.classes

# Temporary memory
# doc_store = {
#     "ocr_text": None,
#     "structured_data": None,
#     "document_type": None
# }

train_document_classifier()


# Make sure storage directory exists
os.makedirs("storage/docs", exist_ok=True)

@app.post("/upload-document/")
async def upload_document(files: List[UploadFile] = File(...),document_type: str = Form(...)):
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
                page_text=extract_text(temp_img_path)
                combined_text+=page_text+"\n\n"
                os.remove(temp_img_path)

            #use first page for classification
            first_page_path=f"temp_{unique_id}_page_0.jpg"
            images[0].save(first_page_path,"JPEG")
            doc_type=predict_document_type(first_page_path,class_labels=class_labels)
            os.remove(first_page_path)

        else:
            temp_img_path=f"temp_{unique_id}.jpg"
            with open(temp_img_path,"wb") as f:
                f.write(file_bytes)


            combined_text=extract_text(temp_img_path)
            doc_type = predict_document_type(temp_img_path, class_labels=class_labels)
            os.remove(temp_img_path)


        structured_data=extract_structured_data(combined_text)

        doc_id=str(uuid.uuid4())
        text_blob=json.dumps(structured_data,indent=2)

        #store in a vector
        store_document(doc_id,text_blob,metadata={
            "filename": file.filename,
            "doc_type":doc_type,
        })

        #store permanetly
        filename = f"{doc_type}_{doc_id}.json"
        filepath=os.path.join("storage/docs",filename)

        

        with open (filepath,"w") as f:
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


@app.post("/chat/")
async def chat_bot(question: str = Form(...)):
    """
    Perform hybrid search and LLM-based RAG via ask_question().
    Includes robust error handling.
    """
    try:
        if not question.strip():
            raise HTTPException(status_code=400, detail="Question must not be empty.")
        
        answer = ask_question(question)

        if not answer or not answer.strip():
            return {"answer": "No meaningful response found."}

        return {"answer": answer}
    
    except HTTPException as http_err:
        raise http_err

    except Exception as e:
        logging.error("Unhandled error in /chat/: %s", traceback.format_exc())
        return {
            "error": "An internal error occurred while processing your request.",
            "details": str(e)
        }




# @app.post("/chat/")
# async def chat_bot(question: str = Form(...)):
#     """
#     Search all previously uploaded documents and answer using RAG.
#     """

#     all_texts = ""

#     for file in os.listdir("storage/docs"):
#         if file.endswith(".json"):
#             file_path=os.path.join("storage/docs",file)
#             try:
#                 with open(file_path,"r",encoding="utf-8") as f:
#                     data=json.load(f)
#             except UnicodeDecodeError:

#                 try:
#                     with open(file_path,"r", encoding="latin-1") as f:
#                         data=json.load(f)
#                 except Exception as e:
#                     print(f"Skipped file due to decoding error: {file}-{e}")
#                     continue

#                 all_texts+= data.get("raw_text","") + "\n\n"
            

#     if not all_texts.strip():
#         return {"error":"Now documents found"}
    
#     answer=ask_question(all_texts,question)


#     return {
#         "answer":answer
#     }