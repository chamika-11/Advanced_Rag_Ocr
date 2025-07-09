import React, { useState } from 'react';
import axios from 'axios';

function OcrUpload({ onResults }) {
  const [files, setFiles] = useState([]);
  const [docType, setDocType] = useState('');
  const [results, setResults] = useState([]);

  const handleFileChange = (e) => {
    setFiles(e.target.files);
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    for (const file of files) {
      formData.append('files', file);
    }
    formData.append('document_type', docType);

    try {
      const res = await axios.post('http://localhost:8000/upload-document/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      const data = res.data.results || [];
      setResults(data);
      onResults(data); 
    } catch (err) {
      console.error('Upload failed:', err);
    }
  };

  const styles = {
    form: {
      marginBottom: '2rem',
      display: 'flex',
      alignItems: 'center',
      gap: '1rem',
    },
    input: {
      padding: '0.5rem',
      borderRadius: '5px',
      border: '1px solid #ccc',
      width: '250px',
    },
    button: {
      padding: '0.5rem 1rem',
      backgroundColor: '#007BFF',
      color: 'white',
      border: 'none',
      borderRadius: '5px',
      cursor: 'pointer',
    },
    listItem: {
      background: '#f8f9fa',
      border: '1px solid #ccc',
      borderRadius: '6px',
      padding: '1rem',
      marginBottom: '1rem',
    },
    pre: {
      background: '#f0f0f0',
      padding: '0.75rem',
      borderRadius: '4px',
      overflowX: 'auto',
    },
  };

  return (
    <div>
      <form onSubmit={handleUpload} style={styles.form}>
        <input type="file" multiple onChange={handleFileChange} />
        <input
          type="text"
          placeholder="Document Type (e.g., Salary Slip, Loan Form)"
          value={docType}
          onChange={(e) => setDocType(e.target.value)}
          style={styles.input}
        />
        <button type="submit" style={styles.button}>
          Upload & Process
        </button>
      </form>

      {results.length > 0 && (
        <div>
          <h3>📄 Processed Document Results</h3>
          <ul>
            {results.map((r, idx) => (
              <li key={idx} style={styles.listItem}>
                <strong>File:</strong> {r.file}<br />
                <strong>Detected Type:</strong> {r.document_type}<br />
                <strong>Structured Data:</strong>
                <pre style={styles.pre}>
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
