import os
from langchain_community.llms import Together
from langchain.chains.question_answering import load_qa_chain
from langchain.docstore.document import Document
from dotenv import load_dotenv
from vector_store import hybrid_search

load_dotenv()

def ask_question(query):
    docs = hybrid_search(query, top_k=5)
    if not docs:
        return "No relevant documents found."

    llm = Together(
        model="mistralai/Mistral-7B-Instruct-v0.1",
        temperature=0.5,
        max_tokens=512
    )

    chain = load_qa_chain(llm, chain_type="stuff")

    input_docs=[Document(page_content=doc["text"]) for doc in docs]
    result = chain.run(input_documents=input_docs, question=query)
    return result
