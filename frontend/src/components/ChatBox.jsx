import React, { useState } from 'react';
import axios from 'axios';

function RagChat() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');

  const handleAskQuestion = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post(
        'http://localhost:8000/chat/',
        new URLSearchParams({ question }),
        {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        }
      );
      setAnswer(res.data.answer);
    } catch (err) {
      console.error('RAG question failed:', err);
    }
  };

  const styles = {
    form: {
      marginTop: '2rem',
      display: 'flex',
      alignItems: 'center',
      gap: '1rem',
    },
    input: {
      width: '60%',
      padding: '0.5rem',
      borderRadius: '5px',
      border: '1px solid #ccc',
    },
    button: {
      padding: '0.5rem 1rem',
      backgroundColor: '#28A745',
      color: 'white',
      border: 'none',
      borderRadius: '5px',
      cursor: 'pointer',
    },
    answerBox: {
      marginTop: '1rem',
      background: '#e9f7ef',
      padding: '1rem',
      borderRadius: '5px',
      border: '1px solid #c3e6cb',
    },
  };

  return (
    <div>
      <form onSubmit={handleAskQuestion} style={styles.form}>
        <h3>❓ Ask a Question:</h3>
        <input
          type="text"
          placeholder="Type your question here..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          style={styles.input}
        />
        <button type="submit" style={styles.button}>
          Ask
        </button>
      </form>

      {answer && (
        <div style={styles.answerBox}>
          <h4>💬 Answer:</h4>
          <p>{answer}</p>
        </div>
      )}
    </div>
  );
}

export default RagChat;
