import { useEffect, useState } from "react";
import AssetAllocation from "../components/AssetAllocation";
import PerformanceChart from "../components/PerformanceChart";
import HoldingsTable from "../components/HoldingsTable";
import StatTile from "../components/StatTile";
import { getPortfolio, getHoldings, getStock } from "../services/api";

const ASSET_TYPE_LABELS = {
  Stock: "stocks_value",
  Bond: "bonds_value",
  Crypto: "crypto_value",
};
import { useDataRefresh } from "../services/refreshStore";

const ASSET_TYPE_LABELS = {
  Stock: "stocks_value",
  Bond: "bonds_value",
  Crypto: "crypto_value",
};

function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const refreshKey = useDataRefresh();

  useEffect(() => {
    let isMounted = true;

    async function loadSummary() {
      try {
        const [portfolioResult, holdingsResult] = await Promise.all([
          getPortfolio(1),
          getHoldings(1),
        ]);

        if (!portfolioResult.response.ok) {
          throw new Error(portfolioResult.data?.error || "Failed to load portfolio summary.");
        }

        const holdings = Array.isArray(holdingsResult.data) ? holdingsResult.data : [];
        const totals = { stocks_value: 0, bonds_value: 0, crypto_value: 0 };

        await Promise.all(
          holdings.map(async (holding) => {
            const shares = parseFloat(holding.shares) || 0;
            let price = 0;
            try {
              const stockResult = await getStock(holding.ticker);
              price = stockResult.data?.price ?? 0;
            } catch {
              price = 0;
            }
            const marketValue = shares * price;
            const key = ASSET_TYPE_LABELS[holding.asset_type] || "stocks_value";
            totals[key] += marketValue;
          })
        );

        if (isMounted) {
          setSummary({
            ...totals,
            cash_balance: portfolioResult.data?.cash_balance ?? 0,
          });
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

      <AssetAllocation />
      <PerformanceChart />

      <div className="span-2">
        <HoldingsTable showLink />
      </div>
    </div>
  );
}

export default Dashboard;
