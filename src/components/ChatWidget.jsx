import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const ChatWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [panelSize, setPanelSize] = useState({ width: 360, height: 420 });
  const [isResizing, setIsResizing] = useState(false);
  const [isPinned, setIsPinned] = useState(false);
  const messagesEndRef = useRef(null);
  const containerRef = useRef(null);
  const toggleButtonRef = useRef(null);

  const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize with a welcome message
  useEffect(() => {
    if (isOpen && messages.length === 0) {
      setMessages([
        {
          id: 1,
          text: "Hello! I'm your travel assistant. How can I help you today?",
          sender: 'bot',
          timestamp: new Date()
        }
      ]);
    }
  }, [isOpen, messages.length]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!inputValue.trim()) return;

    // Add user message to chat
    const userMessage = {
      id: Date.now(),
      text: inputValue,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Build optional context from app state if accessible
      let page = undefined;
      let formSummary = undefined;
      try {
        // Attempt to read minimal context from window if App provides it
        page = window?.appCurrentView;
        formSummary = window?.appFormSummary;
      } catch (_) {}

      // Prefer streaming endpoint; fall back to non-streaming
      let lastResults = undefined;
      try {
        lastResults = window?.appLastResults || undefined;
      } catch (_) {}

      const payload = { message: inputValue, page, formSummary, lastResults, includeUserContext: true };

      try {
        const token = localStorage.getItem('token');
        const resp = await fetch(`${API_BASE_URL}/api/chat/stream`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) },
          body: JSON.stringify(payload)
        });

        if (!resp.body || !resp.ok) throw new Error('No stream');

        const reader = resp.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let buffer = '';
        let accumulated = '';
        let tempId = Date.now() + 1;

        // Insert a placeholder bot message to update progressively
        setMessages(prev => [...prev, { id: tempId, text: '', sender: 'bot', timestamp: new Date() }]);

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });
          let idx;
          while ((idx = buffer.indexOf('\n')) >= 0) {
            const line = buffer.slice(0, idx).trim();
            buffer = buffer.slice(idx + 1);
            if (!line) continue;
            try {
              const json = JSON.parse(line);
              if (json && typeof json.reply === 'string') {
                accumulated += json.reply;
                // Update the last bot message
                setMessages(prev => prev.map(m => m.id === tempId ? { ...m, text: accumulated } : m));
              }
            } catch (_) {
              // ignore parse errors for partial lines
            }
          }
        }

        // Finalize timestamp
        setMessages(prev => prev.map(m => m.id === tempId ? { ...m, timestamp: new Date() } : m));
      } catch (_) {
        // Fallback to non-streaming via axios
        const token2 = localStorage.getItem('token');
        const response = await axios.post(`${API_BASE_URL}/api/chat`, payload, { headers: token2 ? { Authorization: `Bearer ${token2}` } : {} });
        const botMessage = {
          id: Date.now() + 1,
          text: response.data.reply,
          sender: 'bot',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, botMessage]);
      }
    } catch (error) {
      // Add error message to chat
      const errorMessage = {
        id: Date.now() + 1,
        text: "Sorry, I'm having trouble responding right now. Please try again later.",
        sender: 'bot',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  // Resize handlers
  useEffect(() => {
    const handleMove = (e) => {
      if (!isResizing) return;
      const deltaX = e.movementX;
      const deltaY = e.movementY;
      setPanelSize((prev) => {
        const nextWidth = Math.min(Math.max(prev.width + deltaX, 300), 520);
        const nextHeight = Math.min(Math.max(prev.height + deltaY, 360), 700);
        return { width: nextWidth, height: nextHeight };
      });
    };
    const handleUp = () => setIsResizing(false);
    window.addEventListener('mousemove', handleMove);
    window.addEventListener('mouseup', handleUp);
    return () => {
      window.removeEventListener('mousemove', handleMove);
      window.removeEventListener('mouseup', handleUp);
    };
  }, [isResizing]);

  // Close when clicking outside or pressing Escape
  useEffect(() => {
    if (!isOpen) return;

    const handleClickOutside = (e) => {
      const containerEl = containerRef.current;
      const toggleEl = toggleButtonRef.current;
      if (!containerEl) return;
      const clickedInside = containerEl.contains(e.target);
      const clickedToggle = toggleEl && toggleEl.contains(e.target);
      if (!clickedInside && !clickedToggle) {
        if (isPinned) return; // respect pin
        setIsOpen(false);
      }
    };
    const handleEscape = (e) => {
      if (e.key === 'Escape') setIsOpen(false);
    };

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('touchstart', handleClickOutside);
    document.addEventListener('keyup', handleEscape);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('touchstart', handleClickOutside);
      document.removeEventListener('keyup', handleEscape);
    };
  }, [isOpen, isPinned]);

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {isOpen ? (
        <div
          ref={containerRef}
          className="bg-white rounded-lg shadow-xl border border-gray-200 flex flex-col relative"
          style={{ width: panelSize.width, height: panelSize.height }}
        >
          {/* Chat Header */}
          <div className="bg-blue-600 text-white p-4 rounded-t-lg flex justify-between items-center">
            <h3 className="font-semibold">Travel Assistant</h3>
            <div className="flex items-center space-x-3">
              <button
                type="button"
                onClick={() => setIsPinned(p => !p)}
                className={`text-white hover:text-gray-200 focus:outline-none ${isPinned ? 'opacity-100' : 'opacity-80'}`}
                title={isPinned ? 'Unpin chat' : 'Pin chat'}
                aria-label={isPinned ? 'Unpin chat' : 'Pin chat'}
              >
                {isPinned ? (
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M6.5 2a1 1 0 00-.894.553l-1.5 3A1 1 0 003 6.382V9a1 1 0 001 1h3.586l-4.293 4.293a1 1 0 101.414 1.414L9 11.414V15a1 1 0 001 1h2.618a1 1 0 1 0 0-2H11v-3a1 1 0 00-1-1H7V6.382a1 1 0 00-.106-.447l1.5-3A1 1 0 006.5 2z" />
                  </svg>
                ) : (
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M6 2a1 1 0 00-.894.553l-1.5 3A1 1 0 003 6.382V9a1 1 0 001 1h4v4a1 1 0 001 1h2.618a1 1 0 100-2H11v-3a1 1 0 00-1-1H7V6.382a1 1 0 00-.106-.447l1.5-3A1 1 0 006 2z" />
                  </svg>
                )}
              </button>
              <button 
                onClick={toggleChat}
                className="text-white hover:text-gray-200 focus:outline-none"
                aria-label="Close chat"
                title="Close"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </button>
            </div>
          </div>

          {/* Messages Container */}
          <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex mb-3 ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[75%] px-4 py-2 rounded-lg space-y-1 ${
                    message.sender === 'user'
                      ? 'bg-blue-500 text-white rounded-br-none'
                      : 'bg-gray-200 text-gray-800 rounded-bl-none'
                  }`}
                >
                  <div className="text-sm leading-relaxed">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}
                      components={{
                        ul: ({node, ...props}) => <ul className="list-disc pl-5 space-y-1" {...props} />,
                        ol: ({node, ...props}) => <ol className="list-decimal pl-5 space-y-1" {...props} />,
                        li: ({node, ...props}) => <li className="mb-0" {...props} />,
                        p: ({node, ...props}) => <p className="mb-2 last:mb-0" {...props} />,
                        strong: ({node, ...props}) => <strong className="font-semibold" {...props} />,
                        a: ({node, ...props}) => <a className="underline" {...props} />,
                      }}
                    >
                      {message.text}
                    </ReactMarkdown>
                  </div>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start mb-3">
                <div className="bg-gray-200 text-gray-800 px-4 py-2 rounded-lg rounded-bl-none">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <form onSubmit={handleSendMessage} className="border-t border-gray-200 p-3">
            <div className="flex">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Type your message..."
                className="flex-1 border border-gray-300 rounded-l-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={isLoading}
              />
              <button
                type="submit"
                className="bg-blue-600 text-white px-4 py-2 rounded-r-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                disabled={isLoading || !inputValue.trim()}
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
                </svg>
              </button>
            </div>
          </form>

          {/* Resize handle */}
          <div
            className="absolute bottom-2 right-2 w-5 h-5 cursor-se-resize flex items-end justify-end"
            onMouseDown={() => setIsResizing(true)}
            title="Drag to resize"
          >
            <div className="pointer-events-none text-gray-400">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4">
                <path d="M3 21h2v-2H3v2zm4 0h2v-4H7v4zm4 0h2v-6h-2v6zm4 0h2v-8h-2v8zm4 0h2v-10h-2v10z" />
              </svg>
            </div>
          </div>
        </div>
      ) : (
        // Chat Icon Button
        <button
          onClick={toggleChat}
          ref={toggleButtonRef}
          className="bg-blue-600 text-white rounded-full p-3 shadow-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all duration-200"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
        </button>
      )}
    </div>
  );
};

export default ChatWidget;