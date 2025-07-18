import React, { useState } from 'react';
import axios from 'axios';

function RagChat() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false); 

  const handleAskQuestion = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    try {
      setLoading(true); 
      const res = await axios.post(
        'http://localhost:8000/chat/',
        new URLSearchParams({ question }),
        {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        }
      );
      setAnswer(res.data.answer);
    } catch (err) {
      console.error('RAG question failed:', err);
      setAnswer('❌ An error occurred while fetching the answer.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto p-6 mt-10 bg-white shadow-md rounded-xl">
      <h2 className="text-2xl font-bold mb-6 text-gray-800 text-center">
        Deep Search
      </h2>

      <form onSubmit={handleAskQuestion} className="flex flex-col sm:flex-row gap-4 items-center justify-center">
        <input
          type="text"
          placeholder="Type your question here..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          className="w-full sm:w-3/4 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
        />
        <button
          type="submit"
          disabled={loading}
          className={`px-6 py-2 rounded-lg font-semibold text-white transition 
            ${loading ? 'bg-gray-500 cursor-not-allowed' : 'bg-green-600 hover:bg-green-700'}`}
        >
          {loading ? 'Searching...' : 'Search'}
        </button>
      </form>

      {answer && (
        <div className="mt-6 bg-green-50 border border-green-200 text-green-900 px-6 py-4 rounded-lg">
          <h4 className="text-lg font-semibold mb-2">Data:</h4>
          <p>{answer}</p>
        </div>
      )}
    </div>
  );
}

export default RagChat;
