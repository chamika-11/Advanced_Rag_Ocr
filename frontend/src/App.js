import './App.css';
import UploadForm from './components/UploadForm';
import ChatBox from './components/ChatBox';


function App() {
  return (
    <div className="container mt-5">
      <h1>Document OCR & Chatbot</h1>
      <UploadForm/>
      <hr />
      <ChatBox />
    </div>
  );
}

export default App;
