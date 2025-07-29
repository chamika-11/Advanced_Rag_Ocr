import React, { useEffect, useState } from 'react';
import { useAPI, Alert } from '../hooks/useAPI';

function QueryExamples() {
  const [examples, setExamples] = useState([]);
  const { loading, error, callAPI } = useAPI();

  useEffect(() => {
    fetchExamples();
  }, []);

  const fetchExamples = async () => {
    try {
      const result = await callAPI('/query-examples/');
      setExamples(result.examples || []);
    } catch (err) {
      // Error handled by useAPI hook
    }
  };

  if (loading) {
    return (
      <div className="bg-white shadow-md rounded-lg p-6">
        <h2 className="text-2xl font-semibold text-slate-800 mb-4">Query Examples</h2>
        <div className="text-center py-4">
          <p className="text-slate-600">Loading examples...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white shadow-md rounded-lg p-6">
      <h2 className="text-2xl font-semibold text-slate-800 mb-4">Query Examples</h2>

      {error && <Alert type="error" message={error} />}

      <div className="grid gap-4 md:grid-cols-2">
        {examples.map((example, index) => (
          <div
            key={index}
            className="bg-slate-50 p-4 rounded-lg border border-slate-200 hover:border-indigo-200 transition-colors"
          >
            <h3 className="font-medium text-slate-800 mb-2">{example.title}</h3>
            <p className="text-slate-600 text-sm mb-3">{example.description}</p>
            <div className="bg-white p-3 rounded border border-slate-200">
              <code className="text-sm text-indigo-600 whitespace-pre-wrap">
                {example.query}
              </code>
            </div>
            {example.expected_output && (
              <div className="mt-2 text-sm text-slate-500">
                <span className="font-medium">Expected:</span> {example.expected_output}
              </div>
            )}
            {example.tags && (
              <div className="mt-2 flex flex-wrap gap-2">
                {example.tags.map((tag, tagIndex) => (
                  <span
                    key={tagIndex}
                    className="px-2 py-1 text-xs bg-indigo-100 text-indigo-700 rounded-full"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      {examples.length === 0 && (
        <div className="text-center py-4">
          <p className="text-slate-600">No example queries available.</p>
        </div>
      )}
    </div>
  );
}

export default QueryExamples;
