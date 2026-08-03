import { useSyncExternalStore } from "react";

const listeners = new Set();
let refreshNonce = 0;

function subscribe(callback) {
  listeners.add(callback);
  return () => listeners.delete(callback);
}

function getSnapshot() {
  return refreshNonce;
}

export function useDataRefresh() {
  return useSyncExternalStore(subscribe, getSnapshot, getSnapshot);
}

export function refreshData() {
  refreshNonce += 1;
  listeners.forEach((listener) => listener());
}
