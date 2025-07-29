import React, { useEffect, useState } from 'react';
import { useAPI, Alert } from '../hooks/useAPI';

function ConversationHistory() {
  const [history, setHistory] = useState([]);
  const { loading, error, callAPI } = useAPI();

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const result = await callAPI('/conversation-history/');
      setHistory(result.history || []);
    } catch (err) {
      // Error handled by useAPI hook
    }
  };

  return (
    <div className="bg-white shadow-md rounded-lg p-6">
      <h2 className="text-2xl font-semibold text-slate-800 mb-4">Conversation History</h2>

      {error && <Alert type="error" message={error} />}

      {loading ? (
        <div className="text-center py-4">
          <p className="text-slate-600">Loading history...</p>
        </div>
      ) : history.length === 0 ? (
        <div className="text-center py-4">
          <p className="text-slate-600">No conversation history yet.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {history.map((conversation, index) => (
            <div key={index} className="border border-slate-200 rounded-lg p-4">
              <div className="flex justify-between items-start mb-2">
                <span className="text-sm text-slate-500">
                  {new Date(conversation.timestamp).toLocaleString()}
                </span>
                <span className={`px-2 py-1 text-xs rounded-full ${
                  conversation.type === 'user' 
                    ? 'bg-indigo-100 text-indigo-700'
                    : 'bg-green-100 text-green-700'
                }`}>
                  {conversation.type}
                </span>
              </div>
              <p className="text-slate-700 whitespace-pre-wrap">{conversation.message}</p>
              {conversation.response && (
                <div className="mt-2 pl-4 border-l-2 border-slate-200">
                  <p className="text-slate-600">{conversation.response}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      <div className="mt-4 flex justify-center">
        <button
          onClick={fetchHistory}
          className="text-indigo-600 hover:text-indigo-700 text-sm font-medium"
        >
          Refresh History
        </button>
      </div>
    </div>
  );
}

export default ConversationHistory;
