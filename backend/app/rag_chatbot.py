import os
from langchain_community.llms import Together
from langchain.chains.question_answering import load_qa_chain
from langchain.docstore.document import Document
from dotenv import load_dotenv
from vector_store import hybrid_search
from langchain.prompts import PromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain

load_dotenv()

def ask_question(query):
    docs = hybrid_search(query, top_k=5)
    if not docs:
        return "No relevant documents found."

    llm = Together(
        model="mistralai/Mistral-7B-Instruct-v0.1",
        temperature=0.1,
        max_tokens=512
    )

    prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""You are a helpful assistant. Use ONLY the following context to answer the question.
If the context does not provide enough information, say "Sorry, I couldn’t find that in the uploaded documents."

Context:
{context}

Question: {question}

Answer:"""
)

    chain = create_stuff_documents_chain(llm=llm, prompt=prompt)
    input_docs = [Document(page_content=doc["text"]) for doc in docs]
    result = chain.invoke({
        "context": "\n\n".join(doc.page_content for doc in input_docs),
        "question": query
    })

    return result





    # chain = load_qa_chain(llm, chain_type="stuff", prompt=prompt)

    # input_docs=[Document(page_content=doc["text"]) for doc in docs]
    # result = chain.run(input_documents=input_docs, question=query)
    # return result
