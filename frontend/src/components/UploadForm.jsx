import React, { useState } from 'react';
import axios from 'axios';

function OcrUpload({ onResults }) {
  const [files, setFiles] = useState([]);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setFiles(e.target.files);
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    for (const file of files) {
      formData.append('files', file);
    }

    try {
      setLoading(true);
      const res = await axios.post('http://localhost:8000/upload-document/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      const data = res.data.results || [];
      setResults(data);
      onResults(data);
    } catch (err) {
      console.error('Upload failed:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto p-6 mt-10 bg-white shadow-md rounded-xl">
      <h2 className="text-2xl font-bold mb-6 text-gray-800 text-center">Upload Document</h2>

      <form onSubmit={handleUpload} className="flex flex-col sm:flex-row gap-4 mb-6">
        <input
          type="file"
          multiple
          onChange={handleFileChange}
          className="w-full sm:w-1/2 border border-gray-300 px-4 py-2 rounded-lg"
        />
        <button
          type="submit"
          disabled={loading}
          className={`w-full sm:w-auto px-6 py-2 rounded-lg font-semibold text-white transition 
            ${loading ? 'bg-gray-500 cursor-not-allowed' : 'bg-green-600 hover:bg-green-700'}`}
        >
          {loading ? 'Uploading...' : 'Upload & Process'}
        </button>
      </form>

      {results.length > 0 && (
        <div className="mt-6">
          <h3 className="text-xl font-semibold mb-4 text-gray-700">📄 Processed Document Results</h3>
          <ul className="space-y-4">
            {results.map((r, idx) => (
              <li key={idx} className="bg-green-50 border border-green-200 p-4 rounded-lg shadow-sm">
                <p><strong>File:</strong> {r.file}</p>
                <p><strong>Detected Type:</strong> {r.document_type}</p>
                <p className="mt-2"><strong>Structured Data:</strong></p>
                <pre className="bg-gray-100 p-3 rounded-lg overflow-x-auto text-sm">
                  {JSON.stringify(r.structured_data, null, 2)}
                </pre>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default OcrUpload;
