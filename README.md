# Document Processing System (OCR + Classification + RAG Chatbot)

A full-stack application that allows users to upload documents (PDFs/images), automatically extract text, classify the document type, extract structured data, and ask questions using RAG (Retrieval-Augmented Generation).

---

## Technologies Used

### Backend (FastAPI)
- OCR text extraction (`ocr_engine.py`)
- Document classification (`classifier.py`)
- Structured data extraction (`extract.py`)
- RAG chatbot using all uploaded documents (`rag_chatbot.py`)
- File handling & storage

### Frontend (Angular)
- Upload documents via form
- Ask questions using a chat interface
- Display results (structured data + answers)

---
