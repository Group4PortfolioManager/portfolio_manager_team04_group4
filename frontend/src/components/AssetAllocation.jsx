import { assetAllocation } from "../data/mockData";
import { PieChart, Pie, Cell, Tooltip } from "recharts";

function AssetAllocation() {
  return (
    <div className="panel">
      <h2>Asset Allocation</h2>

      <div className="donut-row">
        <PieChart width={220} height={220}>
          <Pie
            data={assetAllocation}
            dataKey="percentage"
            nameKey="type"
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={100}
          >
            {assetAllocation.map((entry) => (
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
          {assetAllocation.map((asset) => (
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
