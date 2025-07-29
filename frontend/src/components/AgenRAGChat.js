import React, { useState } from "react";
import axios from "axios";

function RAGChat() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [useSimpleRAG, setUseSimpleRAG] = useState(false);

  const ask = async () => {
    const form = new FormData();
    form.append("question", question);
    form.append("use_simple_rag", useSimpleRAG.toString());

    try {
      const res = await axios.post("http://localhost:8000/agentic-chat/", form);
      setAnswer(res.data.answer);
    } catch (err) {
      alert("Query failed.");
    }
  };

  return (
    <div className="bg-white shadow-md rounded p-4 mb-6">
      <h2 className="text-xl font-semibold mb-2">Ask a Question</h2>
      <textarea
        rows="3"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        className="w-full p-2 border rounded mb-2"
        placeholder="Ask something..."
      ></textarea>
      <div className="flex items-center mb-2">
        <input
          type="checkbox"
          checked={useSimpleRAG}
          onChange={() => setUseSimpleRAG(!useSimpleRAG)}
          className="mr-2"
        />
        <span>Use Simple RAG</span>
      </div>
      <button
        onClick={ask}
        className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
      >
        Submit
      </button>
      {answer && (
        <div className="mt-4">
          <h3 className="font-semibold">Answer:</h3>
          <p className="bg-gray-100 p-2 rounded">{answer}</p>
        </div>
      )}
    </div>
  );
}

export default RAGChat;
