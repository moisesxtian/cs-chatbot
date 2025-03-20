import { useState, useEffect, useRef } from 'react';
import './App.css';
import { CopyToClipboard } from 'react-copy-to-clipboard';
import { Copy } from 'lucide-react';

function App() {
  const [userInput, setUserInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  // Unique session ID (will persist per session)
  const [sessionId] = useState(() => {
    return crypto.randomUUID();
  });

  // Initial welcome message from AI
  useEffect(() => {
    setMessages([
      {
        sender: 'ai',
        text: '👋 Hi there! How can I assist you today?',
      },
    ]);
  }, []);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!userInput.trim()) return;

    setMessages((prev) => [...prev, { sender: 'user', text: userInput }]);
    setUserInput('');

    setIsTyping(true);
    setMessages((prev) => [...prev, { sender: 'ai', text: '...' }]);

    try {
      const response = await fetch('http://127.0.0.1:8000/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userInput, session_id: sessionId }),
      });

      const data = await response.json();
      setMessages((prev) => {
        const updated = prev.slice(0, -1); // Remove "..."
        return [...updated, { sender: 'ai', text: data.response }];
      });
    } catch (error) {
      console.error('Error:', error);
      setMessages((prev) => {
        const updated = prev.slice(0, -1); // Remove "..."
        return [...updated, { sender: 'ai', text: '⚠️ Failed to fetch response.' }];
      });
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="flex items-center justify-center h-screen">
      <div className="bg-gray-900 shadow-xl rounded-2xl w-full max-w-lg flex flex-col overflow-hidden border border-gray-700">
        <header className="bg-gray-800 text-white text-center p-4 text-xl font-semibold rounded-t-2xl">
          💬 Customer Service Chatbot
        </header>

        <div className="flex-1 p-4 space-y-4 overflow-y-auto max-h-[60vh] custom-scrollbar">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`relative flex p-4 rounded-2xl ${
                msg.sender === 'user'
                  ? 'bg-gray-700 self-end ml-auto text-white'
                  : 'bg-gray-800 self-start mr-auto text-gray-200 border border-gray-700'
              } max-w-[80%]`}
            >
              <p className="whitespace-pre-wrap break-words">
                {msg.text === '...' && isTyping ? (
                  <span className="animate-pulse">AI is typing...</span>
                ) : (
                  msg.text
                )}
              </p>
              {msg.sender === 'ai' && msg.text !== '...' && (
                <CopyToClipboard text={msg.text}>
                  <button className="absolute top-2 right-2 text-gray-400 hover:text-white">
                    <Copy size={16} />
                  </button>
                </CopyToClipboard>
              )}
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSubmit} className="flex p-4 bg-gray-800 border-t border-gray-700">
          <input
            type="text"
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            placeholder="Type your message..."
            className="flex-1 rounded-l-xl p-3 outline-none bg-gray-700 text-white placeholder-gray-400 focus:ring-2 focus:ring-gray-500 border border-gray-600"
          />
          <button
            type="submit"
            className="bg-green-500 hover:bg-green-600 text-white px-4 rounded-r-xl"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}

export default App;
