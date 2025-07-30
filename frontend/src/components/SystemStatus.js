import React, { useEffect, useState } from "react";
import axios from "axios";

function SystemStatus() {
  const [status, setStatus] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setIsLoading(true);
    axios.get("http://localhost:8000/system-status/")
      .then((res) => {
        setStatus(res.data);
        setIsLoading(false);
      })
      .catch(() => {
        setStatus(null);
        setIsLoading(false);
      });
  }, []);

  return (
    <div className="bg-white shadow-lg rounded-xl p-6 mb-6 transition-all duration-300 hover:shadow-xl">
      <div className="flex items-center gap-3 mb-4">
        <div className="p-2 bg-gradient-to-br from-emerald-100 to-teal-50 rounded-lg shadow-sm">
          <svg className="w-5 h-5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h2 className="text-xl font-bold text-slate-800">System Status</h2>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-8">
          <div className="w-8 h-8 border-3 border-emerald-200 border-t-emerald-600 rounded-full animate-spin" />
        </div>
      ) : status ? (
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="bg-gradient-to-br from-slate-50 to-white p-4 rounded-lg border border-slate-200 
            shadow-sm transition-all duration-200 hover:shadow-md">
            <div className="flex items-center gap-2 mb-2">
              <div className={`w-2 h-2 rounded-full ${status.system_initialized ? 'bg-emerald-500' : 'bg-red-500'}`} />
              <span className="font-medium text-slate-700">System Status</span>
            </div>
            <p className="text-sm text-slate-600">
              {status.system_initialized ? 'System is initialized and running' : 'System needs initialization'}
            </p>
          </div>

          <div className="bg-gradient-to-br from-slate-50 to-white p-4 rounded-lg border border-slate-200 
            shadow-sm transition-all duration-200 hover:shadow-md">
            <div className="flex items-center gap-2 mb-2">
              <svg className="w-4 h-4 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              <span className="font-medium text-slate-700">Documents</span>
            </div>
            <p className="text-sm text-slate-600">{status.total_documents} documents processed</p>
          </div>

          <div className="bg-gradient-to-br from-slate-50 to-white p-4 rounded-lg border border-slate-200 
            shadow-sm transition-all duration-200 hover:shadow-md">
            <div className="flex items-center gap-2 mb-2">
              <div className={`w-2 h-2 rounded-full ${status.memory_active ? 'bg-emerald-500' : 'bg-amber-500'}`} />
              <span className="font-medium text-slate-700">Memory Status</span>
            </div>
            <p className="text-sm text-slate-600">
              {status.memory_active ? 'Memory system is active' : 'Memory system is inactive'}
            </p>
          </div>

          <div className="bg-gradient-to-br from-slate-50 to-white p-4 rounded-lg border border-slate-200 
            shadow-sm transition-all duration-200 hover:shadow-md">
            <div className="flex items-center gap-2 mb-2">
              <svg className="w-4 h-4 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 4a2 2 0 114 0v1a1 1 0 001 1h3a1 1 0 011 1v3a1 1 0 01-1 1h-1a2 2 0 100 4h1a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-1a2 2 0 10-4 0v1a1 1 0 01-1 1H7a1 1 0 01-1-1v-3a1 1 0 00-1-1H4a2 2 0 110-4h1a1 1 0 001-1V7a1 1 0 011-1h3a1 1 0 001-1V4z" />
              </svg>
              <span className="font-medium text-slate-700">Available Tools</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {status.available_tools.map((tool, index) => (
                <span key={index} className="px-2 py-1 text-xs font-medium bg-gradient-to-r from-indigo-50 
                  to-purple-50 text-indigo-700 rounded-full border border-indigo-100 shadow-sm">
                  {tool}
                </span>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center py-8 bg-red-50 rounded-lg border border-red-100">
          <svg className="w-12 h-12 text-red-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <p className="text-red-600 font-medium">Failed to load system status</p>
          <p className="text-red-500 text-sm mt-1">Please check your connection and try again</p>
        </div>
      )}
    </div>
  );
}

export default SystemStatus;
