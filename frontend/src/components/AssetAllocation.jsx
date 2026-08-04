import { useState, useEffect } from "react";
import { getPortfolio, getHoldings, getStock } from "../services/api";
import { useDataRefresh } from "../services/refreshStore";
import { PieChart, Pie, Cell, Tooltip } from "recharts";

const COLORS = {
  'Stock': '#3b82f6',
  'Bond': '#22d3ee',
  'Crypto': '#f59e0b',
  'Cash': '#a78bfa'
};



function AssetAllocation() {
  const [values, setValues] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const refreshKey = useDataRefresh();

  useEffect(() => {
    let isMounted = true;

    async function loadAllocation() {
      try {
        const [portfolioResult, holdingsResult] = await Promise.all([
          getPortfolio(1),
          getHoldings(1),
        ]);

        if (!portfolioResult.response.ok) {
          throw new Error(portfolioResult.data?.error || "Failed to load portfolio.");
        }

        const holdings = Array.isArray(holdingsResult.data) ? holdingsResult.data : [];
        const totals = { Stock: 0, Bond: 0, Crypto: 0, Cash: 0 };

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
            const type = holding.asset_type || "Stock";
            const label = type === "Stock" ? "Stock" : type === "Bond" ? "Bond" : type === "Crypto" ? "Crypto" : "Cash";
            totals[label] += marketValue;
          })
        );

        totals.Cash = parseFloat(portfolioResult.data?.cash_balance) || 0;

        if (isMounted) {
          setValues(totals);
          setLoading(false);
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message);
          setLoading(false);
        }
      }
    }

    loadAllocation();
    return () => {
      isMounted = false;
    };
  }, [refreshKey]);

  if (loading) {
    return (
      <div className="panel">
        <h2>Asset Allocation</h2>
        <p>Loading...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="panel">
        <h2>Asset Allocation</h2>
        <p>Error loading assets: {error}</p>
      </div>
    );
  }

  const total = values ? Object.values(values).reduce((sum, value) => sum + value, 0) : 0;

  if (!values || total === 0) {
    return (
      <div className="panel">
        <h2>Asset Allocation</h2>
        <p>No assets for the moment</p>
      </div>
    );
  }

  const data = Object.entries(values)
    .filter(([, value]) => value > 0)
    .map(([type, value]) => ({
      type,
      percentage: Math.round((value / total) * 100),
      color: COLORS[type] || '#8891a3'
    }));

  return (
    <div className="panel">
      <h2>Asset Allocation</h2>

      <div className="donut-row">
        <PieChart width={220} height={220}>
          <Pie
            data={data}
            dataKey="percentage"
            nameKey="type"
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={100}
          >
            {data.map((entry) => (
              <Cell key={entry.type} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip
            formatter={(value) => [`${value}%`, "Allocation"]}
            contentStyle={{ background: "#131824", border: "1px solid #232a3a", borderRadius: 8, color: "#e7e9ee" }}
            labelStyle={{ color: "#8891a3" }}
          />
        </PieChart>

        <ul className="legend">
          {data.map((asset) => (
            <li key={asset.type}>
              <span className="legend-dot" style={{ backgroundColor: asset.color }} />
              {asset.type}
              <span className="legend-percentage">{asset.percentage}%</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default AssetAllocation;
