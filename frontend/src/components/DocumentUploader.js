import React, { useState } from "react";
import { useAPI, Alert } from '../hooks/useAPI';

function DocumentUploader() {
  const [files, setFiles] = useState([]);
  const [result, setResult] = useState(null);
  const { loading, error, callAPI } = useAPI();

  const upload = async () => {
    if (files.length === 0) return;

    const formData = new FormData();
    for (const file of files) {
      formData.append("files", file);
    }

    try {
      const response = await callAPI('/upload-document/', 'POST', formData);
      setResult(response);
      setFiles([]);
    } catch (err) {
      // Error handled by useAPI hook
    }
  };

  const handleFileChange = (e) => {
    const selectedFiles = [...e.target.files];
    setFiles(selectedFiles);
  };

  return (
    <div className="bg-white shadow-lg rounded-xl p-6 transition-all duration-300 hover:shadow-xl">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
          <svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          Upload Documents
        </h2>
        {files.length > 0 && (
          <span className="bg-indigo-100 text-indigo-800 text-xs font-medium px-2.5 py-1 rounded-full">
            {files.length} file{files.length > 1 ? 's' : ''} selected
          </span>
        )}
      </div>

      {error && <Alert type="error" message={error} />}

      <div className="space-y-6">
        <div 
          className="border-2 border-dashed border-slate-300 rounded-xl p-8 text-center transition-all duration-300 hover:border-indigo-400 hover:bg-indigo-50/50 group relative"
        >
          <input
            type="file"
            multiple
            onChange={handleFileChange}
            className="hidden"
            id="file-upload"
            accept=".pdf,.png,.jpg,.jpeg"
          />
          <label
            htmlFor="file-upload"
            className="cursor-pointer text-slate-600 hover:text-indigo-600 block"
          >
            <div className="space-y-4">
              <div className="transform transition-transform duration-300 group-hover:scale-110">
                <svg
                  className="mx-auto h-16 w-16 text-slate-400 group-hover:text-indigo-500"
                  stroke="currentColor"
                  fill="none"
                  viewBox="0 0 48 48"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8 14v20c0 4.418 3.582 8 8 8h16c4.418 0 8-3.582 8-8V14m-18 0l6-6m0 0l6 6m-6-6v29"
                  />
                </svg>
              </div>
              <div className="text-base">
                <span className="text-indigo-600 font-semibold hover:text-indigo-500">
                  Click to upload
                </span>{" "}
                or drag and drop
              </div>
              <p className="text-sm text-slate-500">
                PDF, PNG, JPG, JPEG (max. 10MB each)
              </p>
            </div>
          </label>
        </div>

        {files.length > 0 && (
          <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
            <h3 className="text-sm font-semibold text-slate-700 mb-3 flex items-center gap-2">
              <svg className="w-4 h-4 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Selected Files
            </h3>
            <ul className="space-y-2">
              {Array.from(files).map((file, index) => (
                <li
                  key={index}
                  className="flex items-center justify-between text-sm bg-white p-3 rounded-lg border border-slate-200 hover:border-indigo-200 hover:shadow-sm transition-all duration-200"
                >
                  <div className="flex items-center gap-2">
                    <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                    </svg>
                    <span className="text-slate-700">{file.name}</span>
                  </div>
                  <span className="text-xs font-medium px-2 py-1 bg-slate-100 text-slate-600 rounded-full">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}

        <button
          onClick={upload}
          disabled={loading || files.length === 0}
          className={`w-full flex justify-center items-center gap-2 py-3 px-4 border border-transparent rounded-xl text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-all duration-300 ${
            loading || files.length === 0 ? "opacity-50 cursor-not-allowed" : "hover:scale-[1.02]"
          }`}
        >
          {loading ? (
            <>
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Uploading...
            </>
          ) : (
            <>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
              </svg>
              Upload Documents
            </>
          )}
        </button>
      </div>

      {result && (
        <div className="mt-8">
          <h3 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
            <svg className="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            Upload Results
          </h3>
          <div className="bg-slate-50 rounded-xl p-5 border border-slate-200">
            <div className="space-y-4">
              {result.processed_files?.map((file, index) => (
                <div
                  key={index}
                  className="bg-white p-5 rounded-xl border border-slate-200 hover:border-indigo-200 transition-all duration-200 hover:shadow-md"
                >
                  <h4 className="font-semibold text-slate-700 mb-3 flex items-center gap-2">
                    <svg className="w-4 h-4 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                    </svg>
                    {file.filename}
                  </h4>
                  <div className="grid grid-cols-2 gap-6">
                    <div className="bg-slate-50 p-3 rounded-lg">
                      <p className="text-sm text-slate-600 mb-1">Pages Processed</p>
                      <p className="text-lg font-semibold text-slate-800">{file.pages_processed}</p>
                    </div>
                    <div className="bg-slate-50 p-3 rounded-lg">
                      <p className="text-sm text-slate-600 mb-1">Status</p>
                      <p className={`text-lg font-semibold flex items-center gap-1 ${
                        file.success ? "text-green-600" : "text-red-600"
                      }`}>
                        {file.success ? (
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                          </svg>
                        ) : (
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        )}
                        {file.success ? "Success" : "Failed"}
                      </p>
                    </div>
                  </div>
                  {file.error && (
                    <div className="mt-3 p-3 bg-red-50 border border-red-100 rounded-lg">
                      <p className="text-sm text-red-600 flex items-center gap-2">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        {file.error}
                      </p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default DocumentUploader;
