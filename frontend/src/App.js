import './App.css';
import UploadForm from './components/UploadForm';
import ChatBox from './components/ChatBox';


function App() {
  return (
    <div className="container mt-5">
      <h1 className="text-4xl font-bold text-center text-blue-700 mt-8 mb-6 underline decoration-green-400">Document Chatbot</h1>
      <hr />
      <ChatBox />
      <br/>
      <UploadForm/>
    </div>
  );
}

export default App;
