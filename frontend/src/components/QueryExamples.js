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

  return (
    <div className="bg-white shadow-lg rounded-xl p-6 transition-all duration-300 hover:shadow-xl">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-gradient-to-br from-indigo-100 to-purple-50 rounded-lg shadow-sm">
          <svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        </div>
        <div>
          <h2 className="text-2xl font-bold text-slate-800">Query Examples</h2>
          <p className="text-sm text-slate-500 mt-1">Example questions to help you get started</p>
        </div>
      </div>

      {error && <Alert type="error" message={error} />}

      {loading ? (
        <div className="flex flex-col items-center justify-center py-12">
          <div className="w-16 h-16 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin mb-4" />
          <p className="text-slate-600">Loading examples...</p>
        </div>
      ) : examples.length === 0 ? (
        <div className="text-center py-12 bg-gradient-to-b from-slate-50 to-white rounded-xl border border-slate-200">
          <svg className="w-16 h-16 mx-auto text-slate-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
          <p className="text-slate-600 text-lg font-medium">No examples available</p>
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {examples.map((example, index) => (
            <div
              key={index}
              className="group bg-gradient-to-br from-slate-50 to-white p-5 rounded-xl border border-slate-200 
                hover:border-indigo-200 hover:shadow-md transition-all duration-200 relative overflow-hidden"
            >
              <div className="absolute inset-0 bg-gradient-to-br from-indigo-50 to-transparent opacity-0 
                group-hover:opacity-100 transition-opacity duration-200" 
              />
              
              <div className="relative">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold text-slate-800 group-hover:text-indigo-700 
                    transition-colors duration-200">{example.title}</h3>
                  <div className="p-1.5 bg-indigo-50 rounded-lg">
                    <svg className="w-4 h-4 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                </div>

                <p className="text-slate-600 text-sm mb-4 line-clamp-2">{example.description}</p>

                <div className="bg-white p-4 rounded-lg border border-slate-200 group-hover:border-indigo-100 
                  shadow-sm transition-all duration-200 mb-4">
                  <code className="text-sm text-indigo-600 font-medium whitespace-pre-wrap">
                    {example.query}
                  </code>
                </div>

                {example.expected_output && (
                  <div className="flex items-center gap-2 mb-4">
                    <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <p className="text-sm text-slate-600">
                      <span className="font-medium text-slate-700">Expected:</span>{' '}
                      {example.expected_output}
                    </p>
                  </div>
                )}

                {example.tags && (
                  <div className="flex flex-wrap gap-2">
                    {example.tags.map((tag, tagIndex) => (
                      <span
                        key={tagIndex}
                        className="px-2.5 py-1 text-xs font-medium bg-gradient-to-r from-indigo-50 to-purple-50 
                          text-indigo-700 rounded-full border border-indigo-100 shadow-sm"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default QueryExamples;
