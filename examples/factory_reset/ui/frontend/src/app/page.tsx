'use client';

import React, { useEffect, useRef, useState } from 'react';
import { useChat } from '../hooks/useChat';
import { ChatMessage } from '../components/ChatMessage';
import { ToolPanel } from '../components/ToolPanel';
import { ToolExecution } from '../components/ToolExecution';
import {
  Send,
  Trash2,
  AlertCircle,
  Loader2,
  MessageCircle,
  Activity
} from 'lucide-react';

export default function ChatPage() {
  const {
    messages,
    isConnected,
    isLoading,
    sessionId,
    availableTools,
    currentToolExecutions,
    error,
    sendMessage,
    clearMessages
  } = useChat();

  const [inputMessage, setInputMessage] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, currentToolExecutions]);

  // Focus input on load
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const message = inputMessage.trim();
    setInputMessage('');
    await sendMessage(message);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const exampleQueries = [
    "Show me the current GPU status",
    "Run a quick diagnostic on all GPUs",
    "Check NVLink connectivity",
    "Start the monitoring stack",
    "Create a Grafana dashboard"
  ];

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Main chat area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-nvidia-green rounded-lg flex items-center justify-center">
                <Activity className="h-5 w-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-800">DCGM Agent Chat</h1>
                <p className="text-sm text-gray-600">
                  Interactive GPU monitoring and management
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              {sessionId && (
                <span className="text-xs text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
                  Session: {sessionId}
                </span>
              )}
              <button
                onClick={clearMessages}
                className="text-gray-600 hover:text-red-600 p-2 hover:bg-gray-100 rounded-lg transition-colors"
                title="Clear chat"
              >
                <Trash2 className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Error banner */}
        {error && (
          <div className="bg-red-50 border-l-4 border-red-400 p-4 m-4">
            <div className="flex items-center">
              <AlertCircle className="h-5 w-5 text-red-400 mr-2" />
              <p className="text-red-700">{error}</p>
            </div>
          </div>
        )}

        {/* Messages area */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="w-16 h-16 bg-nvidia-green rounded-full flex items-center justify-center mb-4">
                <MessageCircle className="h-8 w-8 text-white" />
              </div>
              <h2 className="text-xl font-semibold text-gray-800 mb-2">
                Welcome to DCGM Agent Chat
              </h2>
              <p className="text-gray-600 mb-6 max-w-md">
                Ask questions about your GPUs, run diagnostics, or set up monitoring.
                The agent will use the appropriate tools to help you.
              </p>

              <div className="w-full max-w-md">
                <h3 className="font-medium text-gray-800 mb-3">Try these examples:</h3>
                <div className="space-y-2">
                  {exampleQueries.map((query, index) => (
                    <button
                      key={index}
                      onClick={() => setInputMessage(query)}
                      className="w-full text-left p-3 bg-white border border-gray-200 rounded-lg hover:border-nvidia-green hover:bg-green-50 transition-colors text-sm"
                    >
                      "{query}"
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <>
              {messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}

              {/* Current tool executions */}
              {currentToolExecutions.length > 0 && (
                <div className="mb-6">
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-3">
                      <Loader2 className="h-4 w-4 text-blue-600 animate-spin" />
                      <span className="font-medium text-blue-800">Agent is working...</span>
                    </div>
                    <div className="space-y-2">
                      {currentToolExecutions.map((execution) => (
                        <ToolExecution
                          key={execution.execution_id}
                          execution={execution}
                          isActive={true}
                        />
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input area */}
        <div className="bg-white border-t border-gray-200 px-6 py-4">
          <form onSubmit={handleSubmit} className="flex gap-3">
            <div className="flex-1 relative">
              <textarea
                ref={inputRef}
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about GPU status, run diagnostics, or set up monitoring..."
                className="w-full resize-none rounded-lg border border-gray-300 px-4 py-3 pr-12 focus:border-nvidia-green focus:ring-2 focus:ring-green-500 focus:ring-opacity-20 outline-none"
                rows={inputMessage.split('\n').length || 1}
                maxLength={2000}
                disabled={isLoading || !isConnected}
              />
              <div className="absolute bottom-2 right-2 text-xs text-gray-400">
                {inputMessage.length}/2000
              </div>
            </div>
            <button
              type="submit"
              disabled={!inputMessage.trim() || isLoading || !isConnected}
              className="px-6 py-3 bg-nvidia-green text-white rounded-lg hover:bg-green-600 focus:ring-2 focus:ring-green-500 focus:ring-opacity-20 outline-none disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
            >
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
              <span className="hidden sm:inline">
                {isLoading ? 'Processing...' : 'Send'}
              </span>
            </button>
          </form>
          <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
            <span>
              Press Enter to send, Shift+Enter for new line
            </span>
            <span className={isConnected ? 'text-green-600' : 'text-red-600'}>
              {isConnected ? '● Connected' : '● Disconnected'}
            </span>
          </div>
        </div>
      </div>

      {/* Tool panel */}
      <ToolPanel
        availableTools={availableTools}
        currentExecutions={currentToolExecutions}
        isConnected={isConnected}
      />
    </div>
  );
}
