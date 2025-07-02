import os
from langchain_community.llms import Together
from langchain.chains.question_answering import load_qa_chain
from langchain.docstore.document import Document
from dotenv import load_dotenv

load_dotenv()

def ask_question(text, question):
    docs = [Document(page_content=text)]

    llm = Together(
        model="mistralai/Mistral-7B-Instruct-v0.1",
        temperature=0.5,
        max_tokens=512
    )

    chain = load_qa_chain(llm, chain_type="stuff")
    result = chain.run(input_documents=docs, question=question)
    return result
