import datetime
import json
import uuid
from fastapi import FastAPI, UploadFile, File, Form
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


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Angular dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Prepare class labels at startup
dataset = ImageFolder("data/classification")
class_labels = dataset.classes

# Temporary memory
# doc_store = {
#     "ocr_text": None,
#     "structured_data": None,
#     "document_type": None
# }

# Make sure storage directory exists
os.makedirs("storage/docs", exist_ok=True)

@app.post("/upload-document/")
async def upload_document(files: List[UploadFile] = File(...),document_type: str = Form(...)):
    """
    Upload multiple documents (PDFs or images). For PDFs, process all pages.
    Extract raw text + structured data for each, and save as individual JSONs.
    """
    results =[]

    train_document_classifier()

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
            doc_type+predict_document_type(temp_img_path, class_labels=class_labels)
            os.remove(temp_img_path)


        structured_data=extract_structured_data(combined_text)
        # text = extract_text("uploaded.jpg")
        # structured_data = extract_structured_data(text)
        # doc_type = predict_document_type("uploaded.jpg", class_labels=class_labels)
        
        # store results
        # doc_store["ocr_text"] = text
        # doc_store["structured_data"] = structured_data
        # doc_store["document_type"] = doc_type

        #store permanetly
        timestamp = datetime.now().timestamp()
        filename=f"{doc_type}_{timestamp}.json"
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

    
    return {
        "message": f"{len(files)} document(s) processed successfully.",
        "results": results
    }



@app.post("/chat/")
async def chat_bot(question: str = Form(...)):
    """
    Search all previously uploaded documents and answer using RAG.
    """
    all_texts = ""

    for file in os.listdir("storage/docs"):
        if file.endswith(".json"):
            with open(os.path.join("storage/docs", file), "r",encoding="utf-8") as f:
                data=json.load(f)
                all_texts +=data.get("raw_text","")+"\n\n"


    if not all_texts.strip():
        return {"error":"Now documents found"}
    
    answer=ask_question(all_texts,question)


    return {
        "answer":answer
    }