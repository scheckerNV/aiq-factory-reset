'use client';

import React from 'react';
import { ToolInfo, ToolExecution as ToolExecutionType } from '../types';
import { ToolExecution } from './ToolExecution';
import {
  Wrench,
  Activity,
  Zap,
  CheckCircle,
  XCircle,
  Clock
} from 'lucide-react';

interface ToolPanelProps {
  availableTools: ToolInfo[];
  currentExecutions: ToolExecutionType[];
  isConnected: boolean;
}

export const ToolPanel: React.FC<ToolPanelProps> = ({
  availableTools,
  currentExecutions,
  isConnected
}) => {
  const getToolIcon = (toolName: string) => {
    const iconMap: Record<string, React.ReactNode> = {
      'gpu_status': <Activity className="h-4 w-4" />,
      'gpu_run_diagnostics': <Zap className="h-4 w-4" />,
      'gpu_enable_health': <CheckCircle className="h-4 w-4" />,
      'gpu_nvlink_status': <Activity className="h-4 w-4" />,
      'prom_stack_start': <Clock className="h-4 w-4" />,
      'prom_query': <Activity className="h-4 w-4" />,
      'grafana_create_dashboard': <Activity className="h-4 w-4" />,
    };

    return iconMap[toolName] || <Wrench className="h-4 w-4" />;
  };

  const getExecutionStats = () => {
    const stats = {
      running: currentExecutions.filter(e => e.status === 'started').length,
      completed: currentExecutions.filter(e => e.status === 'completed').length,
      errors: currentExecutions.filter(e => e.status === 'error').length
    };
    return stats;
  };

  const stats = getExecutionStats();

  return (
    <div className="w-80 bg-white border-l border-gray-200 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center gap-2 mb-2">
          <Wrench className="h-5 w-5 text-nvidia-green" />
          <h2 className="font-semibold text-gray-800">Tools & Monitoring</h2>
        </div>
        <div className={`flex items-center gap-2 text-sm ${
          isConnected ? 'text-green-600' : 'text-red-600'
        }`}>
          <div className={`w-2 h-2 rounded-full ${
            isConnected ? 'bg-green-500' : 'bg-red-500'
          }`} />
          {isConnected ? 'Connected' : 'Disconnected'}
        </div>
      </div>

      {/* Current executions */}
      {currentExecutions.length > 0 && (
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-medium text-gray-800">Active Tools</h3>
            <div className="flex items-center gap-2 text-xs">
              {stats.running > 0 && (
                <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded">
                  {stats.running} running
                </span>
              )}
              {stats.errors > 0 && (
                <span className="bg-red-100 text-red-700 px-2 py-1 rounded">
                  {stats.errors} errors
                </span>
              )}
            </div>
          </div>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {currentExecutions.map((execution) => (
              <ToolExecution
                key={execution.execution_id}
                execution={execution}
                isActive={execution.status === 'started'}
              />
            ))}
          </div>
        </div>
      )}

      {/* Available tools */}
      <div className="flex-1 p-4">
        <h3 className="font-medium text-gray-800 mb-3">
          Available Tools ({availableTools.length})
        </h3>
        <div className="space-y-2">
          {availableTools.map((tool) => (
            <div
              key={tool.name}
              className="p-3 bg-gray-50 rounded-lg border border-gray-100 hover:border-gray-200 transition-colors"
            >
              <div className="flex items-center gap-2 mb-1">
                <div className="text-nvidia-green">
                  {getToolIcon(tool.name)}
                </div>
                <span className="font-medium text-sm text-gray-800">
                  {tool.name}
                </span>
                <span className="text-xs bg-gray-200 text-gray-600 px-2 py-1 rounded-full ml-auto">
                  {tool.type}
                </span>
              </div>
              <p className="text-xs text-gray-600">
                {tool.description}
              </p>
            </div>
          ))}
        </div>

        {availableTools.length === 0 && (
          <div className="text-center text-gray-500 py-8">
            <Wrench className="h-8 w-8 mx-auto mb-2 opacity-50" />
            <p className="text-sm">No tools available</p>
            <p className="text-xs text-gray-400 mt-1">
              Check your agent configuration
            </p>
          </div>
        )}
      </div>

      {/* Footer info */}
      <div className="p-4 border-t border-gray-200 bg-gray-50">
        <div className="text-xs text-gray-600">
          <div className="flex justify-between items-center">
            <span>DCGM Agent UI</span>
            <span className="text-nvidia-green">v1.0.0</span>
          </div>
          <div className="mt-1 text-gray-500">
            Real-time GPU monitoring
          </div>
        </div>
      </div>
    </div>
  );
};
