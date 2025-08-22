'use client';

import React from 'react';
import { ChatMessage as ChatMessageType } from '../types';
import { ToolExecution } from './ToolExecution';
import { formatDistanceToNow } from 'date-fns';
import {
  User,
  Bot,
  Clock,
  Cpu,
  Zap
} from 'lucide-react';

interface ChatMessageProps {
  message: ChatMessageType;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user';

  const formatExecutionTime = (seconds: number) => {
    if (seconds < 1) {
      return `${Math.round(seconds * 1000)}ms`;
    }
    return `${seconds.toFixed(2)}s`;
  };

  return (
    <div className={`message-enter w-full mb-6 ${isUser ? 'flex justify-end' : 'flex justify-start'}`}>
      <div className={`max-w-4xl w-full ${isUser ? 'flex justify-end' : ''}`}>
        <div className={`
          flex gap-3 p-4 rounded-lg shadow-sm
          ${isUser
            ? 'bg-blue-500 text-white flex-row-reverse'
            : 'bg-white border border-gray-200'
          }
        `}>
          {/* Avatar */}
          <div className={`
            flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center
            ${isUser ? 'bg-blue-600' : 'bg-nvidia-green'}
          `}>
            {isUser ? (
              <User className="h-4 w-4 text-white" />
            ) : (
              <Bot className="h-4 w-4 text-white" />
            )}
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            {/* Message header */}
            <div className={`flex items-center gap-2 mb-2 ${isUser ? 'flex-row-reverse' : ''}`}>
              <span className={`font-medium text-sm ${isUser ? 'text-blue-100' : 'text-gray-800'}`}>
                {isUser ? 'You' : 'DCGM Agent'}
              </span>
              <span className={`text-xs ${isUser ? 'text-blue-200' : 'text-gray-500'}`}>
                {formatDistanceToNow(message.timestamp, { addSuffix: true })}
              </span>
              {message.total_time && (
                <div className={`flex items-center gap-1 text-xs ${isUser ? 'text-blue-200' : 'text-gray-500'}`}>
                  <Clock className="h-3 w-3" />
                  {formatExecutionTime(message.total_time)}
                </div>
              )}
            </div>

            {/* Message content */}
            <div className={`${isUser ? 'text-right' : 'text-left'}`}>
              <div className={`whitespace-pre-wrap ${isUser ? 'text-white' : 'text-gray-800'}`}>
                {message.content}
              </div>
            </div>

            {/* Tool executions */}
            {!isUser && message.tool_executions && message.tool_executions.length > 0 && (
              <div className="mt-4 p-3 bg-gray-50 rounded-lg border">
                <div className="flex items-center gap-2 mb-3">
                  <Cpu className="h-4 w-4 text-gray-600" />
                  <span className="font-medium text-sm text-gray-800">Tool Executions</span>
                  <span className="text-xs bg-gray-200 text-gray-600 px-2 py-1 rounded-full">
                    {message.tool_executions.length}
                  </span>
                </div>
                <div className="space-y-1">
                  {message.tool_executions.map((execution, index) => (
                    <ToolExecution
                      key={execution.execution_id}
                      execution={execution}
                    />
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
