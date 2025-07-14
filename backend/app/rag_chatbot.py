import os
from langchain_community.llms import Together
from langchain.chains.question_answering import load_qa_chain
from langchain.docstore.document import Document
from dotenv import load_dotenv
from vector_store import hybrid_search
from langchain.prompts import PromptTemplate

load_dotenv()

def ask_question(query):
    docs = hybrid_search(query, top_k=5)
    if not docs:
        return "No relevant documents found."

    llm = Together(
        model="mistralai/Mistral-7B-Instruct-v0.1",
        temperature=0,
        max_tokens=512
    )

    qa_prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""
You are a helpful assistant. You must answer the question **only** based on the following context:

{context}

If the answer is not in the context, reply:
"I'm sorry, I couldn't find the answer in the provided documents."

Question: {question}
Answer:"""

    )



    chain = load_qa_chain(llm, chain_type="stuff", prompt=qa_prompt)

    input_docs=[Document(page_content=doc["text"]) for doc in docs]
    result = chain.run(input_documents=input_docs, question=query)
    return result
