import React, { useState } from 'react';
import { useAPI, Alert } from '../hooks/useAPI';

function EvaluateAnswer() {
  const [formData, setFormData] = useState({
    question: '',
    answer: '',
    context: ''
  });
  const [evaluation, setEvaluation] = useState(null);
  const { loading, error, callAPI } = useAPI();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const result = await callAPI('/evaluate-answer/', 'POST', formData);
      setEvaluation(result);
    } catch (err) {
      // Error handled by useAPI hook
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  return (
    <div className="bg-white shadow-md rounded-lg p-6">
      <h2 className="text-2xl font-semibold text-slate-800 mb-4">Evaluate Answer</h2>

      {error && <Alert type="error" message={error} />}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="question" className="block text-sm font-medium text-slate-700 mb-1">
            Question
          </label>
          <input
            type="text"
            id="question"
            name="question"
            value={formData.question}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            placeholder="Enter the question..."
          />
        </div>

        <div>
          <label htmlFor="answer" className="block text-sm font-medium text-slate-700 mb-1">
            Answer to Evaluate
          </label>
          <textarea
            id="answer"
            name="answer"
            value={formData.answer}
            onChange={handleChange}
            rows="3"
            className="w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            placeholder="Enter the answer to evaluate..."
          />
        </div>

        <div>
          <label htmlFor="context" className="block text-sm font-medium text-slate-700 mb-1">
            Context (Optional)
          </label>
          <textarea
            id="context"
            name="context"
            value={formData.context}
            onChange={handleChange}
            rows="3"
            className="w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            placeholder="Enter any relevant context..."
          />
        </div>

        <button
          type="submit"
          disabled={loading || !formData.question || !formData.answer}
          className={`w-full py-2 px-4 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 ${
            loading || !formData.question || !formData.answer ? 'opacity-50 cursor-not-allowed' : ''
          }`}
        >
          {loading ? 'Evaluating...' : 'Evaluate'}
        </button>
      </form>

      {evaluation && (
        <div className="mt-6">
          <h3 className="text-lg font-medium text-slate-800 mb-3">Evaluation Results</h3>
          <div className="bg-slate-50 rounded-lg p-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm font-medium text-slate-600">Accuracy Score</p>
                <p className="text-2xl font-bold text-indigo-600">
                  {(evaluation.accuracy * 100).toFixed(1)}%
                </p>
              </div>
              <div>
                <p className="text-sm font-medium text-slate-600">Relevance Score</p>
                <p className="text-2xl font-bold text-indigo-600">
                  {(evaluation.relevance * 100).toFixed(1)}%
                </p>
              </div>
            </div>
            {evaluation.feedback && (
              <div className="mt-4">
                <p className="text-sm font-medium text-slate-600 mb-2">Feedback</p>
                <p className="text-slate-700">{evaluation.feedback}</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default EvaluateAnswer;
