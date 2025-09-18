import { useParserStore } from '../store';

export const useStartParser = () => {
  const { startParser, startBulkParser } = useParserStore();

  return {
    startParser,
    startBulkParser,
  };
};