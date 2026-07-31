import { useEffect, useState } from "react";
import AssetAllocation from "../components/AssetAllocation";
import PerformanceChart from "../components/PerformanceChart";
import HoldingsTable from "../components/HoldingsTable";
import StatTile from "../components/StatTile";
import { getPortfolio } from "../services/api";

function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    getPortfolio(1)
      .then((result) => {
        if (result.response.ok) {
          setSummary(result.data);
        } else {
          setError(result.data?.error || "Failed to load portfolio summary.");
        }
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

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
