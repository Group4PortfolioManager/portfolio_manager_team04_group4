import {
  useEffect,
  useSyncExternalStore,
} from "react";

import { getPortfolio } from "./api";
import { useDataRefresh } from "./refreshStore";

const listeners = new Set();
const summaryStateByPortfolio = new Map();
const pendingSummaryRequests = new Map();
const DEFAULT_SUMMARY_STATE = {
  summary: null,
  loading: true,
  error: null,
};

function emitChange() {
  listeners.forEach((listener) => listener());
}

function subscribe(listener) {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

function getSummaryState(portfolioId) {
  return (
    summaryStateByPortfolio.get(portfolioId) ||
    DEFAULT_SUMMARY_STATE
  );
}

function setSummaryState(portfolioId, nextState) {
  const currentState = getSummaryState(portfolioId);

  if (
    currentState.summary === nextState.summary &&
    currentState.loading === nextState.loading &&
    currentState.error === nextState.error
  ) {
    return;
  }

  summaryStateByPortfolio.set(portfolioId, nextState);
  emitChange();
}

async function loadPortfolioSummary(
  portfolioId,
  { force = false } = {}
) {
  const currentState = getSummaryState(portfolioId);

  if (!force && currentState.summary) {
    return currentState;
  }

  const existingRequest = pendingSummaryRequests.get(
    portfolioId
  );

  if (existingRequest) {
    return existingRequest;
  }

  setSummaryState(portfolioId, {
    ...currentState,
    loading: true,
    error: null,
  });

  const request = getPortfolio(portfolioId)
    .then((result) => {
      if (!result.response.ok) {
        throw new Error(
          result.data?.error ||
            "Failed to load portfolio summary."
        );
      }

      const nextState = {
        summary: result.data ?? null,
        loading: false,
        error: null,
      };

      setSummaryState(portfolioId, nextState);
      return nextState;
    })
    .catch((error) => {
      const nextState = {
        ...currentState,
        loading: false,
        error:
          error.message ||
          "Failed to load portfolio summary.",
      };

      setSummaryState(portfolioId, nextState);
      return nextState;
    })
    .finally(() => {
      pendingSummaryRequests.delete(portfolioId);
    });

  pendingSummaryRequests.set(portfolioId, request);
  return request;
}

export function usePortfolioSummary(portfolioId = 1) {
  const refreshKey = useDataRefresh();
  const snapshot = useSyncExternalStore(
    subscribe,
    () => getSummaryState(portfolioId),
    () => getSummaryState(portfolioId)
  );

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      loadPortfolioSummary(portfolioId, {
        force: refreshKey > 0,
      });
    }, 0);

    return () => clearTimeout(timeoutId);
  }, [portfolioId, refreshKey]);

  return snapshot;
}