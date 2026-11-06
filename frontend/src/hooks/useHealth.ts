import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import { useAppStore } from '../store/useAppStore';
import { useEffect } from 'react';

export function useHealth() {
  const setHealth = useAppStore((s) => s.setHealth);

  const query = useQuery({
    queryKey: ['system-health'],
    queryFn: api.getHealth,
    refetchInterval: 5000,
    retry: 2,
    staleTime: 3000,
  });

  useEffect(() => {
    if (query.data) {
      setHealth(query.data);
    }
  }, [query.data, setHealth]);

  return query;
}

