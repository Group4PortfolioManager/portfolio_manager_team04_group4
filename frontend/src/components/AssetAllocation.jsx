import { useEffect, useState } from "react";
import { PieChart, Pie, Cell, Tooltip } from "recharts";
import { getHoldings } from "../services/api";

const COLORS = ["#3b82f6", "#22d3ee", "#f59e0b", "#a78bfa"];

function AssetAllocation() {
  const [allocation, setAllocation] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchAllocation() {
      try {
        setLoading(true);
        setError("");

        const { response, data } = await getHoldings(1);
        if (!response.ok) {
          throw new Error("Unable to load asset allocation");
        }

        const holdings = Array.isArray(data) ? data : [];
        const totalValue = holdings.reduce((sum, holding) => sum + Number(holding.market_value || 0), 0);

        if (totalValue === 0) {
          setAllocation([]);
          return;
        }

        const grouped = holdings.reduce((acc, holding) => {
          const type = holding.asset_type || "Stocks";
          const value = Number(holding.market_value || 0);

          if (!acc[type]) {
            acc[type] = {
              type,
              value: 0,
              color: COLORS[Object.keys(acc).length % COLORS.length],
            };
          }

          acc[type].value += value;
          return acc;
        }, {});

        const computedAllocation = Object.values(grouped).map((item) => ({
          ...item,
          percentage: Math.round((item.value / totalValue) * 10000) / 100,
        }));

        setAllocation(computedAllocation);
      } catch (err) {
        setError(err.message || "Unable to load asset allocation");
        setAllocation([]);
      } finally {
        setLoading(false);
      }
    }

    fetchAllocation();
  }, []);

  if (loading) {
    return <div className="panel"><h2>Asset Allocation</h2><p>Loading...</p></div>;
  }

  if (error) {
    return <div className="panel"><h2>Asset Allocation</h2><p>{error}</p></div>;
  }

  if (!allocation.length) {
    return <div className="panel"><h2>Asset Allocation</h2><p>No allocation data available.</p></div>;
  }

  return (
    <div className="panel">
      <h2>Asset Allocation</h2>

      <div className="donut-row">
        <PieChart width={220} height={220}>
          <Pie
            data={allocation}
            dataKey="percentage"
            nameKey="type"
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={100}
          >
            {allocation.map((entry) => (
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
          {allocation.map((asset) => (
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
