import { useEffect, useRef, useState, useCallback } from 'react';
import type { MarketQuote, MarketTick } from '../types';

export type WebSocketStatus = 'connecting' | 'connected' | 'disconnected' | 'error';

export interface UseMarketWebSocketResult {
  status: WebSocketStatus;
  isConnected: boolean;
  liveQuote: MarketQuote | null;
  lastTick: MarketTick | null;
  priceDirection: 'up' | 'down' | 'neutral';
  subscribe: (symbol: string) => void;
}

export function useMarketWebSocket(symbol?: string, enabled = true): UseMarketWebSocketResult {
  const [status, setStatus] = useState<WebSocketStatus>('disconnected');
  const [liveQuote, setLiveQuote] = useState<MarketQuote | null>(null);
  const [lastTick, setLastTick] = useState<MarketTick | null>(null);
  const [priceDirection, setPriceDirection] = useState<'up' | 'down' | 'neutral'>('neutral');

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const pingIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const reconnectAttemptsRef = useRef<number>(0);
  const activeSymbolRef = useRef<string | undefined>(symbol);
  const connectRef = useRef<() => void>(() => {});

  useEffect(() => {
    activeSymbolRef.current = symbol;
  }, [symbol]);

  const connect = useCallback(() => {
    if (!enabled || !symbol) return;

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    setStatus('connecting');

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const wsUrl = `${protocol}//${host}/ws/market/${symbol.toUpperCase()}`;

    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setStatus('connected');
        reconnectAttemptsRef.current = 0;

        // Periodic heartbeat
        if (pingIntervalRef.current) clearInterval(pingIntervalRef.current);
        pingIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ action: 'ping' }));
          }
        }, 30000);
      };

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          if (msg.type === 'snapshot' && msg.data) {
            setLiveQuote(msg.data);
          } else if (msg.type === 'tick') {
            const tick = msg as MarketTick;
            setLastTick(tick);
            setLiveQuote((prev) => {
              if (prev) {
                const prevPrice = prev.price;
                if (tick.price > prevPrice) {
                  setPriceDirection('up');
                } else if (tick.price < prevPrice) {
                  setPriceDirection('down');
                }
                return {
                  ...prev,
                  price: tick.price,
                  change: tick.change,
                  change_percent: tick.change_percent,
                  volume: tick.volume,
                  day_high: Math.max(prev.day_high || tick.price, tick.price),
                  day_low: Math.min(prev.day_low || tick.price, tick.price),
                  updated_at: tick.timestamp,
                };
              } else {
                return {
                  symbol: tick.symbol,
                  price: tick.price,
                  previous_close: tick.price - tick.change,
                  change: tick.change,
                  change_percent: tick.change_percent,
                  day_high: tick.price,
                  day_low: tick.price,
                  volume: tick.volume,
                  currency: 'USD',
                  updated_at: tick.timestamp,
                };
              }
            });
          }
        } catch {
          // ignore non-json frames
        }
      };

      ws.onerror = () => {
        setStatus('error');
      };

      ws.onclose = () => {
        setStatus('disconnected');
        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current);
          pingIntervalRef.current = null;
        }

        // Exponential backoff reconnect
        if (enabled && activeSymbolRef.current) {
          const timeout = Math.min(1000 * Math.pow(1.5, reconnectAttemptsRef.current), 10000);
          reconnectAttemptsRef.current += 1;
          reconnectTimeoutRef.current = setTimeout(() => {
            connectRef.current();
          }, timeout);
        }
      };
    } catch {
      setStatus('error');
    }
  }, [symbol, enabled]);

  useEffect(() => {
    connectRef.current = connect;
  }, [connect]);

  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      if (pingIntervalRef.current) clearInterval(pingIntervalRef.current);
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      setStatus('disconnected');
    };
  }, [connect]);

  const subscribe = useCallback((newSymbol: string) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action: 'subscribe', symbol: newSymbol.toUpperCase() }));
    }
  }, []);

  return {
    status,
    isConnected: status === 'connected',
    liveQuote,
    lastTick,
    priceDirection,
    subscribe,
  };
}
