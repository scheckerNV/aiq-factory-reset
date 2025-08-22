'use client';

import React from 'react';
import { ToolExecution as ToolExecutionType } from '../types';
import { formatDistanceToNow } from 'date-fns';
import {
  Play,
  CheckCircle,
  XCircle,
  Clock,
  Terminal,
  Zap
} from 'lucide-react';

interface ToolExecutionProps {
  execution: ToolExecutionType;
  isActive?: boolean;
}

export const ToolExecution: React.FC<ToolExecutionProps> = ({ execution, isActive = false }) => {
  const getStatusIcon = () => {
    switch (execution.status) {
      case 'started':
        return <Play className="h-4 w-4 text-blue-500 animate-pulse" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'error':
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-400" />;
    }
  };

  const getStatusColor = () => {
    switch (execution.status) {
      case 'started':
        return 'border-blue-200 bg-blue-50';
      case 'completed':
        return 'border-green-200 bg-green-50';
      case 'error':
        return 'border-red-200 bg-red-50';
      default:
        return 'border-gray-200 bg-gray-50';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      return formatDistanceToNow(date, { addSuffix: true });
    } catch {
      return 'just now';
    }
  };

  return (
    <div className={`
      border-l-4 pl-4 py-2 mb-2 transition-all duration-300
      ${getStatusColor()}
      ${isActive ? 'shadow-sm scale-102' : ''}
    `}>
      <div className="flex items-center gap-2 mb-1">
        {getStatusIcon()}
        <div className="flex items-center gap-2">
          <Terminal className="h-3 w-3 text-gray-600" />
          <span className="font-medium text-sm text-gray-800">
            {execution.tool_name}
          </span>
        </div>
        <span className="text-xs text-gray-500 ml-auto">
          {formatTimestamp(execution.timestamp)}
        </span>
      </div>

      {execution.status === 'started' && (
        <div className="text-xs text-blue-600 flex items-center gap-1">
          <Zap className="h-3 w-3 animate-bounce" />
          Executing...
        </div>
      )}

      {execution.input && (
        <div className="mt-2">
          <details className="text-xs">
            <summary className="cursor-pointer text-gray-600 hover:text-gray-800">
              Input parameters
            </summary>
            <pre className="mt-1 p-2 bg-gray-100 rounded text-xs overflow-x-auto">
              {JSON.stringify(execution.input, null, 2)}
            </pre>
          </details>
        </div>
      )}

      {execution.output && execution.status === 'completed' && (
        <div className="mt-2">
          <details className="text-xs">
            <summary className="cursor-pointer text-green-700 hover:text-green-800">
              Output result
            </summary>
            <div className="mt-1 p-2 bg-green-100 rounded text-xs">
              {typeof execution.output === 'string'
                ? execution.output
                : JSON.stringify(execution.output, null, 2)
              }
            </div>
          </details>
        </div>
      )}

      {execution.status === 'error' && (
        <div className="mt-1 text-xs text-red-600 p-2 bg-red-100 rounded">
          Tool execution failed
        </div>
      )}
    </div>
  );
};
