export interface ToolExecution {
  tool_name: string;
  status: 'started' | 'completed' | 'error';
  input?: any;
  output?: any;
  timestamp: string;
  execution_id: string;
}

export interface ChatMessage {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  tool_executions?: ToolExecution[];
  total_time?: number;
}

export interface ToolInfo {
  name: string;
  type: string;
  description: string;
}

export interface WebSocketMessage {
  type: 'connected' | 'tool_execution' | 'response_complete' | 'status' | 'error' | 'pong';
  data: any;
}

export interface ChatResponse {
  response: string;
  session_id: string;
  tool_executions: ToolExecution[];
  total_time: number;
}
