# Agentic Document Analysing System  

The **Agentic Document Analysing System** is an advanced solution designed to automate document processing and enable intelligent information retrieval.  
It combines **OCR, Convolutional Neural Networks (CNN)**, and **Agentic Retrieval-Augmented Generation (RAG)** to handle multiple file formats, extract structured information, and provide semantic and conversational search capabilities.  

---

## 🚀 Features  

- **Multi-format Support**  
  Upload and process documents in **PDF, PNG, JPG, Word, and Excel** formats.  

- **Advanced Preprocessing**  
  Enhances file quality before OCR to ensure higher text recognition accuracy.  

- **Document Classification**  
  Utilizes a custom **CNN model** (trained at system initialization) to verify and classify document types.  

- **Data Extraction**  
  Automatically extracts key details such as **names, locations, and organizations**.  

- **Data Storage**  
  Saves extracted data in:  
  - A **vector database** for semantic search  
  - Structured **JSON files** for interoperability and external use  

- **Intelligent Retrieval**  
  - **Semantic Search**: Retrieve relevant documents and information using meaning-based queries  
  - **Keyword Search**: Direct retrieval using keywords  
  - **Agentic RAG Chatbot**: Interact through natural conversation, with tools for:  
    - Document Search  
    - Document Metadata Search  

---

## 🛠️ Tech Stack  

- **Programming Language:** Python  
- **Deep Learning:** TensorFlow / PyTorch (for CNN model)  
- **OCR Framework:** Tesseract OCR / EasyOCR  
- **Vector Database:** FAISS / Chroma  
- **RAG Framework:** LangChain / LangGraph  
- **Backend:** FastAPI  
- **Frontend (if applicable):** React / Angular  
- **Data Storage:** JSON, Vector Store  

---

## 📂 Project Workflow  

1. **Upload Document** (PDF, image, Word, or Excel)  
2. **Preprocessing** (noise removal, resizing, quality enhancement)  
3. **OCR Processing** to extract raw text  
4. **Document Classification** using CNN model  
5. **Entity Extraction** (names, locations, organizations, etc.)  
6. **Data Storage** in vector DB and JSON file  
7. **Data Retrieval** via:  
   - Semantic Search  
   - Keyword Search  
   - Agentic RAG Chatbot  

---

## 💡 Use Cases  

- Automating document processing in **banking, healthcare, and insurance**  
- Intelligent search across scanned or uploaded corporate documents  
- Building **digital archives** with easy retrieval capabilities  
- Enhancing **compliance and reporting systems** through structured data extraction  
