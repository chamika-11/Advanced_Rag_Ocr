import './App.css';
import React, { useState } from "react";
import DocumentUploader from "./components/DocumentUploader";
import RAGChat from "./components/AgenRAGChat";
import SystemStatus from "./components/SystemStatus";


function App() {
  return (
    <div className="min-h-screen bg-gray-100 text-gray-900">
      <div className="max-w-5xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-6 text-center">Agentic RAG System</h1>
        <SystemStatus />
        <DocumentUploader />
        <RAGChat />
      </div>
    </div>
  );
}

export default App;
