import streamlit as st
import os
import requests
from PIL import Image
from utils import convert_pdf_to_images
# ...existing code...


API_UPLOAD_URL = "http://localhost:8000/upload-document"
API_CHAT_URL = "http://localhost:8000/chat"

st.set_page_config(page_title="Smart OCR System", layout="wide")
st.title("📄 Smart Document OCR + Chatbot")

uploaded_file = st.file_uploader("Upload a document (PDF or Image)", type=["pdf", "jpg", "png", "jpeg"])

if uploaded_file:
    file_ext = uploaded_file.name.split(".")[-1].lower()
    if file_ext == "pdf":
        with open("temp.pdf", "wb") as f:
            f.write(uploaded_file.read())
        image_paths = convert_pdf_to_images("temp.pdf")
        image_path = image_paths[0] 
    else:
        with open("temp.jpg", "wb") as f:
            f.write(uploaded_file.read())
        image_path = "temp.jpg"

    # Upload document to FastAPI endpoint
    with open(image_path, "rb") as img_file:
        files = {"file": (os.path.basename(image_path), img_file, "image/jpeg")}
        response = requests.post(API_UPLOAD_URL, files=files)
    if response.status_code == 200:
        result = response.json()
        st.success("✅ Document uploaded and OCR complete!")
        st.subheader("🧾 Structured Data")
        st.json(result.get("structured_data"))
        st.subheader("📝 Raw OCR Text")
        st.text_area("Text", value=result.get("extracted_text", ""), height=300)
    else:
        st.error(f"API Error: {response.status_code} - {response.text}")

    # Chatbot
    st.subheader("🤖 Ask a Question")
    question = st.text_input("Ask about this document:")
    if st.button("Get Answer") and question:
        data = {"question": question}
        response = requests.post(API_CHAT_URL, data=data)
        if response.status_code == 200:
            answer = response.json().get("answer", "No answer returned.")
            st.success(answer)
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
