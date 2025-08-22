'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { ChatMessage, ToolExecution, ToolInfo, WebSocketMessage } from '../types';

export const useChat = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string>('');
  const [availableTools, setAvailableTools] = useState<ToolInfo[]>([]);
  const [currentToolExecutions, setCurrentToolExecutions] = useState<ToolExecution[]>([]);
  const [error, setError] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();

  // Generate session ID
  useEffect(() => {
    setSessionId(Math.random().toString(36).substr(2, 9));
  }, []);

  // WebSocket connection management
  const connectWebSocket = useCallback(() => {
    if (!sessionId) return;

    try {
      const ws = new WebSocket(`ws://localhost:8000/ws/${sessionId}`);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        setError(null);
        console.log('WebSocket connected');
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          handleWebSocketMessage(message);
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        console.log('WebSocket disconnected');

        // Attempt to reconnect after 3 seconds
        reconnectTimeoutRef.current = setTimeout(() => {
          if (!wsRef.current || wsRef.current.readyState === WebSocket.CLOSED) {
            connectWebSocket();
          }
        }, 3000);
      };

      ws.onerror = (error) => {
        setError('WebSocket connection error');
        console.error('WebSocket error:', error);
      };

    } catch (err) {
      setError('Failed to create WebSocket connection');
      console.error('WebSocket connection error:', err);
    }
  }, [sessionId]);

  const handleWebSocketMessage = (message: WebSocketMessage) => {
    switch (message.type) {
      case 'connected':
        setAvailableTools(message.data.available_tools || []);
        break;

      case 'tool_execution':
        const toolExecution: ToolExecution = message.data;
        setCurrentToolExecutions(prev => {
          const existing = prev.find(t => t.execution_id === toolExecution.execution_id);
          if (existing) {
            return prev.map(t => t.execution_id === toolExecution.execution_id ? toolExecution : t);
          }
          return [...prev, toolExecution];
        });
        break;

      case 'response_complete':
        const { response, tool_executions, total_time } = message.data;
        const newMessage: ChatMessage = {
          id: Math.random().toString(36).substr(2, 9),
          content: response,
          role: 'assistant',
          timestamp: new Date(),
          tool_executions,
          total_time
        };
        setMessages(prev => [...prev, newMessage]);
        setCurrentToolExecutions([]);
        setIsLoading(false);
        break;

      case 'status':
        // Handle status updates if needed
        break;

      case 'error':
        setError(message.data.message);
        setIsLoading(false);
        break;
    }
  };

  // Connect WebSocket when session ID is available
  useEffect(() => {
    if (sessionId) {
      connectWebSocket();
    }

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [sessionId, connectWebSocket]);

  // Fetch available tools
  const fetchTools = useCallback(async () => {
    try {
      const response = await fetch('/api/tools');
      const data = await response.json();
      setAvailableTools(data.tools || []);
    } catch (err) {
      console.error('Failed to fetch tools:', err);
    }
  }, []);

  // Send message
  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim()) return;

    const userMessage: ChatMessage = {
      id: Math.random().toString(36).substr(2, 9),
      content,
      role: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);
    setCurrentToolExecutions([]);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: content,
          session_id: sessionId
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // The response will be handled via WebSocket
    } catch (err) {
      setError('Failed to send message');
      setIsLoading(false);
      console.error('Failed to send message:', err);
    }
  }, [sessionId]);

  // Clear messages
  const clearMessages = useCallback(() => {
    setMessages([]);
    setCurrentToolExecutions([]);
    setError(null);
  }, []);

  return {
    messages,
    isConnected,
    isLoading,
    sessionId,
    availableTools,
    currentToolExecutions,
    error,
    sendMessage,
    clearMessages,
    fetchTools
  };
};
