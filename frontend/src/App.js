import './App.css';
import DocumentUploader from "./components/DocumentUploader";
import RAGChat from "./components/AgentRAGChat";
import SystemStatus from "./components/SystemStatus";

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-gray-100 to-blue-50">
      <div className="max-w-6xl mx-auto px-4 py-8 space-y-8">
        <header className="text-center space-y-4">
          <h1 className="text-4xl font-bold text-slate-800 bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600">
            Document Analysing System
          </h1>
        </header>
        <br/>
        <div className="grid gap-8">
          <RAGChat />
          <div className="grid md:grid-cols-2 gap-8">
            <DocumentUploader />
            <SystemStatus />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
