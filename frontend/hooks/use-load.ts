"use client";
import { useEffect, useState, useSyncExternalStore } from "react";

/** Loads async data; state is only set from promise callbacks (no cascading renders). */
export function useLoad<T>(fn: (() => Promise<T>) | null, deps: unknown[]) {
  const [state, setState] = useState<{ data: T | null; error: boolean }>({ data: null, error: false });
  const [nonce, setNonce] = useState(0);
  useEffect(() => {
    if (!fn) return;
    let live = true;
    fn().then((data) => live && setState({ data, error: false })).catch(() => live && setState((s) => ({ ...s, error: true })));
    return () => { live = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, nonce]);
  return { data: state.data, error: state.error, retry: () => { setState((s) => ({ ...s, error: false })); setNonce((n) => n + 1); } };
}

const noop = () => () => {};
/** true after hydration (for values that only exist in the browser, e.g. localStorage). */
export function useMounted() {
  return useSyncExternalStore(noop, () => true, () => false);
}
