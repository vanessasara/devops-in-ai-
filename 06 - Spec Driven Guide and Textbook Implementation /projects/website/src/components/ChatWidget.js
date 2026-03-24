/**
 * Chat Widget Component
 * RAG-powered chatbot for textbook questions
 */

import React, { useState, useRef, useEffect } from 'react';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: Citation[];
  timestamp: Date;
}

interface Citation {
  chapterSlug: string;
  sectionTitle: string;
  chunkText: string;
}

interface ChatWidgetProps {
  apiBaseUrl?: string;
  placeholder?: string;
}

export default function ChatWidget({
  apiBaseUrl = 'http://localhost:8000',
  placeholder = 'Ask a question about the textbook...',
}: ChatWidgetProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Focus input when chat opens
  useEffect(() => {
    if (isOpen) {
      inputRef.current?.focus();
    }
  }, [isOpen]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${apiBaseUrl}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage.content }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();

      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.answer,
        sources: data.sources || [],
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  return (
    <div className="chat-widget-container">
      {/* Chat toggle button */}
      <button
        className="chat-toggle-button"
        onClick={toggleChat}
        aria-label={isOpen ? 'Close chat' : 'Open chat'}
        aria-expanded={isOpen}
      >
        {isOpen ? '✕' : '💬'}
      </button>

      {/* Chat panel */}
      {isOpen && (
        <div className="chat-panel">
          {/* Header */}
          <div className="chat-header">
            <h3>Textbook Assistant</h3>
            <p className="chat-subtitle">Ask questions about Agentic AI in DevOps</p>
          </div>

          {/* Messages */}
          <div className="chat-messages">
            {messages.length === 0 && (
              <div className="chat-welcome">
                <p>👋 Hi! I can help you understand the textbook content.</p>
                <p>Ask me anything about Agentic AI, patterns, tools, or implementation.</p>
              </div>
            )}

            {messages.map((message) => (
              <div
                key={message.id}
                className={`chat-message ${message.role}`}
              >
                <div className="message-content">
                  {message.content}
                </div>

                {/* Citations */}
                {message.sources && message.sources.length > 0 && (
                  <div className="message-sources">
                    <span className="sources-label">Sources:</span>
                    {message.sources.map((source, index) => (
                      <a
                        key={index}
                        href={`/docs/${source.chapterSlug}`}
                        className="citation-link"
                        title={source.chunkText}
                      >
                        [{source.chapterSlug}: {source.sectionTitle}]
                      </a>
                    ))}
                  </div>
                )}
              </div>
            ))}

            {isLoading && (
              <div className="chat-message assistant loading">
                <div className="loading-spinner" />
                <span>Thinking...</span>
              </div>
            )}

            {error && (
              <div className="chat-error">
                ⚠️ {error}
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="chat-input">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={placeholder}
              disabled={isLoading}
              aria-label="Chat input"
            />
            <button
              onClick={sendMessage}
              disabled={!input.trim() || isLoading}
              aria-label="Send message"
            >
              Send
            </button>
          </div>
        </div>
      )}
    </div>
  );
}