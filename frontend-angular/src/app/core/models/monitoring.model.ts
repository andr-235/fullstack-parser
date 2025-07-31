export interface SystemMetrics {
  cpu: {
    usage_percent: number;
    cores: number;
    temperature?: number;
  };
  memory: {
    total_gb: number;
    used_gb: number;
    available_gb: number;
    usage_percent: number;
  };
  disk: {
    total_gb: number;
    used_gb: number;
    available_gb: number;
    usage_percent: number;
  };
  network: {
    bytes_sent: number;
    bytes_received: number;
    packets_sent: number;
    packets_received: number;
  };
  uptime: {
    system_uptime_seconds: number;
    application_uptime_seconds: number;
  };
}

export interface ParserMetrics {
  is_running: boolean;
  total_groups: number;
  active_groups: number;
  last_parse_time?: string;
  parse_queue_length: number;
  errors_count: number;
  success_rate: number;
  average_parse_time_seconds: number;
}

export interface DatabaseMetrics {
  total_records: number;
  groups_count: number;
  keywords_count: number;
  comments_count: number;
  database_size_mb: number;
  connection_pool_size: number;
  active_connections: number;
  slow_queries_count: number;
  average_query_time_ms: number;
}

export interface ActivityLog {
  id: number;
  timestamp: string;
  level: 'info' | 'warning' | 'error' | 'debug';
  category: string;
  message: string;
  details?: any;
  user_id?: number;
  ip_address?: string;
}
