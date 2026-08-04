import {
  startTransition,
  useEffect,
  useState,
} from "react";
import AssetAllocation from "../components/AssetAllocation";
import PerformanceChart from "../components/PerformanceChart";
import HoldingsTable from "../components/HoldingsTable";
import StatTile from "../components/StatTile";
import { getPortfolio } from "../services/api";
import { useDataRefresh } from "../services/refreshStore";

function scheduleDeferredHoldingsLoad(callback) {
  if (typeof window !== "undefined" && "requestIdleCallback" in window) {
    return window.requestIdleCallback(callback, {
      timeout: 1200,
    });
  }

  return window.setTimeout(callback, 250);
}

function cancelDeferredHoldingsLoad(handle) {
  if (typeof window !== "undefined" && "cancelIdleCallback" in window) {
    window.cancelIdleCallback(handle);
    return;
  }

  clearTimeout(handle);
}

function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showHoldings, setShowHoldings] = useState(false);
  const refreshKey = useDataRefresh();

  useEffect(() => {
    let isMounted = true;

    async function loadSummary() {
      setLoading(true);
      setError(null);

      try {
        const portfolioResult = await getPortfolio(1);

        if (!portfolioResult.response.ok) {
          throw new Error(
            portfolioResult.data?.error ||
              "Failed to load portfolio summary."
          );
        }

        if (isMounted) {
          setSummary(portfolioResult.data ?? null);
          setLoading(false);
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message);
          setLoading(false);
        }
      }
    }

    loadSummary();
    return () => {
      isMounted = false;
    };
  }, [refreshKey]);

  useEffect(() => {
    if (loading || showHoldings) {
      return;
    }

    const deferredLoadHandle = scheduleDeferredHoldingsLoad(() => {
      startTransition(() => {
        setShowHoldings(true);
      });
    });

    return () => cancelDeferredHoldingsLoad(deferredLoadHandle);
  }, [loading, showHoldings]);

  useEffect(() => {
    const resetHandle = window.setTimeout(() => {
      startTransition(() => {
        setShowHoldings(false);
      });
    }, 0);

    return () => clearTimeout(resetHandle);
  }, [refreshKey]);

  const holdingsSummary = [
    { label: "Stocks Value", value: summary?.stocks_value ?? 0 },
    { label: "Bonds Value", value: summary?.bonds_value ?? 0 },
    { label: "Crypto Value", value: summary?.crypto_value ?? 0 },
    { label: "Cash Balance", value: summary?.cash_balance ?? 0 },
  ];

  return (
    <div className="dashboard-grid">
      <div className="stat-tile-row span-2">
        {holdingsSummary.map((asset) => (
          <StatTile
            key={asset.label}
            label={asset.label}
            value={`$${asset.value.toLocaleString()}`}
          />
        ))}
      </div>

      <AssetAllocation
        summary={summary}
        loading={loading}
        error={error}
      />
      <PerformanceChart />

      <div className="span-2">
        {showHoldings ? (
          <HoldingsTable showLink />
        ) : (
          <div className="panel panel-holdings">
            <h2>Top Holdings</h2>
            <p>Loading holdings...</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default Dashboard;
