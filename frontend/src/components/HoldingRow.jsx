import { useState, useEffect } from "react";
import { getHolding } from "../services/api";

function HoldingRow({ holding, holdingId }) {
  const [data, setData] = useState(holding || null);
  const [loading, setLoading] = useState(!holding && !!holdingId);

  useEffect(() => {
    let isMounted = true;
    if (holdingId && !holding) {
      setLoading(true);
      getHolding(holdingId).then((result) => {
        if (isMounted) {
          const fetched = Array.isArray(result.data) ? result.data[0] : result.data;
          setData(fetched);
          setLoading(false);
        }
      });
    }
    return () => {
      isMounted = false;
    };
  }, [holdingId, holding]);

  if (loading || !data) {
    return (
      <tr>
        <td colSpan="7">Loading...</td>
      </tr>
    );
  }

  const totalCost = data.cost_basis * data.shares;
  const profitLossPct = totalCost !== 0 ? (data.profit_loss / totalCost) * 100 : 0;

  return (
    <tr>
      <td className="ticker-symbol">{data.ticker}</td>
      <td>{data.company_name}</td>
      <td className="mono">{data.shares.toLocaleString("en-US", {
        maximumFractionDigits: 2
      })}</td>
      <td className="mono">${data.current_price.toLocaleString("en-US", {
        maximumFractionDigits: 2
      })}</td>
      <td className="mono">${data.cost_basis.toLocaleString("en-US", {
        maximumFractionDigits: 2
      })}</td>
      <td className="mono">${data.market_value.toLocaleString("en-US", {
        maximumFractionDigits: 2
      })}</td>

      <td className={data.profit_loss >= 0 ? "positive" : "negative"}>
        {data.profit_loss >= 0 ? "+" : "-"}$
        {Math.abs(data.profit_loss).toLocaleString("en-US", {
          maximumFractionDigits: 2
        })}
        {" "}
        ({profitLossPct >= 0 ? "+" : "-"}
        {Math.abs(profitLossPct).toFixed(2)}%)
      </td>
    </tr>
  );
}

export default HoldingRow;