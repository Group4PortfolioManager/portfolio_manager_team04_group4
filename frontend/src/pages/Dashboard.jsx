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

    const timeoutId = setTimeout(() => {
      startTransition(() => {
        setShowHoldings(true);
      });
    }, 0);

    return () => clearTimeout(timeoutId);
  }, [loading, showHoldings]);

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
