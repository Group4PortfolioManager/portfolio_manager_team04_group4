import { useState, useEffect, useMemo } from "react";
import { getHolding, getStock } from "../services/api";

function HoldingRow({ holding, holdingId }) {
  const [fetchedData, setFetchedData] = useState(null);
  const [livePrice, setLivePrice] = useState(null);
  const [loading, setLoading] = useState(!holding && !!holdingId);

  useEffect(() => {
    let isMounted = true;
    if (holdingId && !holding) {
      getHolding(holdingId).then((result) => {
        if (isMounted) {
          const fetched = Array.isArray(result.data) ? result.data[0] : result.data;
          setFetchedData(fetched);
          setLoading(false);
        }
      });
    }
    return () => {
      isMounted = false;
    };
  }, [holdingId, holding]);

  const data = useMemo(() => holding || fetchedData || null, [holding, fetchedData]);

  useEffect(() => {
    if (!data || !data.ticker) return;
    let isMounted = true;
    getStock(data.ticker)
      .then((result) => {
        if (isMounted) {
          const stockData = result?.data || {};
          const fetchedPrice = parseFloat(stockData.price);
          if (!Number.isNaN(fetchedPrice)) {
            setLivePrice(fetchedPrice);
          } else {
            setLivePrice(null);
          }
        }
      })
      .catch(() => {
        if (isMounted) setLivePrice(null);
      });
    return () => {
      isMounted = false;
    };
  }, [data && data.ticker]);

  if (loading || !data) {
    return (
      <tr>
        <td colSpan="7">Loading...</td>
      </tr>
    );
  }

  const currentPrice = Number(livePrice ?? data.current_price ?? 0);
  const shares = Number(data.shares) || 0;
  const costBasis = Number(data.cost_basis) || 0;
  const marketValue = +(shares * currentPrice).toFixed(2);
  const profitLoss = +(marketValue - costBasis * shares).toFixed(2);
  const totalCost = costBasis * shares;
  const profitLossPct = totalCost !== 0 ? (profitLoss / totalCost) * 100 : 0;

  return (
    <tr>
      <td className="ticker-symbol">{data.ticker}</td>
      <td>{data.company_name}</td>
      <td className="mono">{shares.toLocaleString("en-US", {
        maximumFractionDigits: 2
      })}</td>
      <td className="mono">${currentPrice.toLocaleString("en-US", {
        maximumFractionDigits: 2
      })}</td>
      <td className="mono">${costBasis.toLocaleString("en-US", {
        maximumFractionDigits: 2
      })}</td>
      <td className="mono">${marketValue.toLocaleString("en-US", {
        maximumFractionDigits: 2
      })}</td>

      <td className={profitLoss >= 0 ? "positive" : "negative"}>
        {profitLoss >= 0 ? "+" : "-"}$
        {Math.abs(profitLoss).toLocaleString("en-US", {
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