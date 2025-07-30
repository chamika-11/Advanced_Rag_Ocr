import React, { useState } from 'react';
import { useAPI, Alert } from '../hooks/useAPI';

function AgentRAGChat() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState(null);
  const { loading, error, callAPI } = useAPI();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    try {
      const formData = new FormData();
      formData.append('question', question);
      
      const result = await callAPI('/agentic-chat/', 'POST', formData);
      
      if (result && typeof result === 'object') {
        // Check if there's an error in the response
        if (result.error) {
          throw new Error(result.error);
        }
        
        setAnswer({
          answer: result.answer || '',
          sources: Array.isArray(result.sources) ? result.sources : [],
          confidence: typeof result.confidence === 'number' ? result.confidence : null,
          query_type: result.query_type || 'unknown',
          timestamp: result.timestamp || new Date().toISOString()
        });
        setQuestion('');
      }
    } catch (err) {
      console.error('Error in handleSubmit:', err);
      // Let the useAPI hook handle the error display
    }
  };

  return (
    <div className="bg-white shadow-lg rounded-xl p-6 transition-all duration-300 hover:shadow-xl">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-indigo-100 rounded-lg">
          <svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
        </div>
        <h2 className="text-2xl font-bold text-slate-800">Ask a Question</h2>
      </div>

      {error && <Alert type="error" message={error.message || 'An error occurred'} />}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="relative">
          <label 
            htmlFor="question" 
            className="absolute -top-2.5 left-3 bg-white px-1 text-sm font-medium text-slate-600"
          >
            Your Question
          </label>
          <textarea
            id="question"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            className="w-full px-4 py-3 border-2 border-slate-200 rounded-xl shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200"
            rows="4"
            placeholder="Ask anything about your documents..."
          />
        </div>

        <button
          type="submit"
          disabled={loading || !question.trim()}
          className={`w-full flex justify-center items-center gap-2 py-3 px-4 rounded-xl text-sm font-semibold text-white 
            ${loading || !question.trim() 
              ? "bg-slate-400 cursor-not-allowed" 
              : "bg-indigo-600 hover:bg-indigo-700 hover:scale-[1.02] active:scale-[0.98]"}
            shadow-sm transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500`}
        >
          {loading ? (
            <>
              <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Processing...
            </>
          ) : (
            <>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 5l7 7-7 7M5 5l7 7-7 7" />
              </svg>
              Ask Question
            </>
          )}
        </button>
      </form>

      {answer && (
        <div className="mt-8 space-y-6">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-lg font-bold text-slate-800">Answer</h3>
          </div>

          <div className="bg-gradient-to-r from-slate-50 to-white rounded-xl p-5 border border-slate-200 shadow-sm">
            <p className="text-slate-700 whitespace-pre-wrap leading-relaxed">
              {typeof answer.answer === 'string' ? answer.answer : JSON.stringify(answer.answer)}
            </p>

            {answer.sources && answer.sources.length > 0 && (
              <div className="mt-6 pt-4 border-t border-slate-200">
                <h4 className="text-sm font-semibold text-slate-600 mb-3 flex items-center gap-2">
                  <svg className="w-4 h-4 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                  </svg>
                  Sources
                </h4>
                <ul className="space-y-2">
                  {answer.sources.map((source, index) => (
                    <li 
                      key={index}
                      className="flex items-center gap-2 text-sm text-slate-600 bg-white p-2 rounded-lg border border-slate-200"
                    >
                      <svg className="w-4 h-4 text-indigo-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span className="truncate">{source}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {answer.confidence && (
              <div className="mt-4 flex items-center gap-2">
                <span className="text-sm text-slate-500">Confidence:</span>
                <div className="flex-1 h-2 bg-slate-200 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-indigo-600 rounded-full transition-all duration-500"
                    style={{ width: `${answer.confidence * 100}%` }}
                  />
                </div>
                <span className="text-sm font-medium text-slate-700">
                  {(answer.confidence * 100).toFixed(0)}%
                </span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default AgentRAGChat;
