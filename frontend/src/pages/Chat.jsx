import { useState } from "react";
import { useParams } from "react-router-dom";

import { askDocument } from "../services/documents";

function Chat() {

  const { documentId } = useParams();

  const [question, setQuestion] = useState("");
  const [asking, setAsking] = useState(false);

  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Hello! Ask me anything about your document."
    }
  ]);

  const handleSubmit = async (e) => {

    e.preventDefault();

    const trimmedQuestion = question.trim();

    if (!trimmedQuestion || asking) {
      return;
    }

    const userMessage = {
      role: "user",
      content: trimmedQuestion
    };

    setMessages((prev) => [
      ...prev,
      userMessage
    ]);

    setQuestion("");
    setAsking(true);

    try {
      const response = await askDocument(documentId, trimmedQuestion);

      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: response.answer }
      ]);
    } catch (err) {
      const detail = err.response?.data?.detail || "Something went wrong. Please try again.";

      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: detail }
      ]);
    } finally {
      setAsking(false);
    }
  };

  return (
    <div className="chat-page">

      <header className="chat-header">

        <div>
          <h1>Document Chat</h1>

          <p>
            Ask questions about your document
          </p>
        </div>

      </header>

      <main className="chat-container">

        <div className="messages">

          {messages.map((message, index) => (

            <div
              key={index}
              className={`message ${message.role}`}
            >
              <div className="message-content">
                {message.content}
              </div>
            </div>

          ))}

          {asking && (
            <div className="message assistant">
              <div className="message-content">
                Thinking...
              </div>
            </div>
          )}

        </div>

        <form
          className="chat-input"
          onSubmit={handleSubmit}
        >

          <input
            type="text"
            placeholder="Ask a question..."
            value={question}
            onChange={(e) =>
              setQuestion(e.target.value)
            }
            disabled={asking}
          />

          <button type="submit" disabled={asking}>
            Send
          </button>

        </form>

      </main>

    </div>
  );
}

export default Chat;
