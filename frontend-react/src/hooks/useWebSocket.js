import { useEffect, useRef, useState } from "react";

export function useWebSocket(path, { token, onMessage } = {}) {
  const [connected, setConnected] = useState(false);
  const wsRef = useRef(null);
  const retryRef = useRef(0);

  useEffect(() => {
    let cancelled = false;

    const connect = () => {
      if (cancelled) return;
      const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
      const url = `${proto}//${window.location.host}${path}${token ? `?token=${token}` : ""}`;
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        setConnected(true);
        retryRef.current = 0;
      };
      ws.onmessage = (e) => {
        try { onMessage?.(JSON.parse(e.data)); }
        catch { onMessage?.(e.data); }
      };
      ws.onclose = () => {
        setConnected(false);
        // Exponential backoff reconnect
        const delay = Math.min(30000, 1000 * 2 ** retryRef.current++);
        setTimeout(connect, delay);
      };
      ws.onerror = () => ws.close();
    };

    connect();
    return () => {
      cancelled = true;
      wsRef.current?.close();
    };
  }, [path, token]);

  return { connected, send: (m) => wsRef.current?.send(typeof m === "string" ? m : JSON.stringify(m)) };
}