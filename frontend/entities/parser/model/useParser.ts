import { useEffect } from 'react';
import { useParserStore } from '../store';

export const useParser = (refetchInterval: number = 0) => {
  const store = useParserStore();

  useEffect(() => {
    // Initial fetch
    store.refetch();

    // Set up interval if provided
    if (refetchInterval > 0) {
      const interval = setInterval(() => {
        store.refetch();
      }, refetchInterval);

      return () => clearInterval(interval);
    }

    return undefined;
  }, [refetchInterval, store.refetch]);

  return {
    ...store,
  };
};