import { useState, useEffect, useRef } from 'react';
import './App.css';
import { CopyToClipboard } from 'react-copy-to-clipboard';
import { Copy, Moon, Sun } from 'lucide-react';

function App() {
  const [userInput, setUserInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [darkMode, setDarkMode] = useState(true);
  const messagesEndRef = useRef(null);
  const [sessionId] = useState(() => crypto.randomUUID());

  useEffect(() => {
    setMessages([{ sender: 'ai', text: '👋 Hi there! How can I assist you today?' }]);
  }, []);

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
      const response = await fetch('cs-chatbot-psi.vercel.app/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userInput, session_id: sessionId }),
      });
      const data = await response.json();
      setMessages((prev) => {
        const updated = prev.slice(0, -1);
        return [...updated, { sender: 'ai', text: data.response }];
      });
    } catch (error) {
      console.error('Error:', error);
      setMessages((prev) => {
        const updated = prev.slice(0, -1);
        return [...updated, { sender: 'ai', text: '⚠️ Failed to fetch response.' }];
      });
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className={`${darkMode ? 'bg-gray-800 text-white' : 'bg-gray-100 text-gray-900'} w-full h-screen flex items-center justify-center`}>
      <div className="w-full max-w-2xl h-[90vh] bg-white dark:bg-gray-700 rounded-2xl shadow-lg flex flex-col overflow-hidden">
        
        {/* Header */}
        <header className="flex items-center justify-between px-6 py-4 border-b border-gray-300 dark:border-gray-700 bg-gray-100 dark:bg-gray-900">
          <h1 className="text-xl font-semibold flex items-center gap-2">
            <span>💬 Chatbot</span>
          </h1>
          <button
            onClick={() => setDarkMode(!darkMode)}
            className="p-2 rounded-full bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
          >
            {darkMode ? <Sun size={20} /> : <Moon size={20} />}
          </button>
        </header>

        {/* Chat messages */}
        <div className="flex-1 p-4 space-y-4 overflow-y-auto custom-scrollbar">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`relative max-w-[75%] p-4 pr-10 rounded-2xl ${
                msg.sender === 'user'
                  ? 'bg-blue-600 text-white self-end ml-auto'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-100 self-start'
              }`}
            >
              <p className="break-words whitespace-pre-wrap">
                {msg.text === '...' && isTyping ? (
                  <span className="animate-pulse">AI is typing...</span>
                ) : (
                  msg.text
                )}
              </p>
              {msg.sender === 'ai' && msg.text !== '...' && (
                <CopyToClipboard text={msg.text}>
                  <button className="absolute top-2 right-2 bg-gray-400 dark:bg-gray-600 hover:bg-gray-500 dark:hover:bg-gray-500 rounded-full p-1 text-white">
                    <Copy size={12} />
                  </button>
                </CopyToClipboard>
              )}
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="flex border-t border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 px-4 py-3">
          <input
            type="text"
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            placeholder="Type your message..."
            className="flex-1 px-4 py-2 rounded-l-lg outline-none bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-100"
          />
          <button
            type="submit"
            className="px-6 py-2 bg-green-500 hover:bg-green-600 text-white font-semibold rounded-r-lg"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}

export default App;
