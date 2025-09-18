// Parser API
import { httpClient } from '@/shared/lib';
import type {
  ParserState,
  ParserStats,
  ParserTask,
  StartParserRequest,
  StartBulkParserRequest,
  ParserResponse
} from './types';

export const parserApi = {
  // Get parser state
  getState: async (): Promise<ParserState> => {
    return await httpClient.get('/parser/state');
  },

  // Get parser stats
  getStats: async (): Promise<ParserStats> => {
    return await httpClient.get('/parser/stats');
  },

  // Get parser tasks
  getTasks: async (): Promise<ParserTask[]> => {
    return await httpClient.get('/parser/tasks');
  },

  // Start parser
  startParser: async (data: StartParserRequest): Promise<ParserResponse> => {
    return await httpClient.post('/parser/start', data);
  },

  // Start bulk parser
  startBulkParser: async (data: StartBulkParserRequest): Promise<ParserResponse> => {
    return await httpClient.post('/parser/start-bulk', data);
  },

  // Stop parser
  stopParser: async (): Promise<ParserResponse> => {
    return await httpClient.post('/parser/stop');
  },
};