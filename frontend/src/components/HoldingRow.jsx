import { useState, useEffect } from "react";
import { getHolding, getStock } from "../services/api";
// import SellHoldingModal from "./SellHoldingModal";

function HoldingRow({ holding, holdingId }) {
  const [data, setData] = useState(holding || null);
  const [loading, setLoading] = useState(!holding && !!holdingId);
  // const [isSellOpen, setIsSellOpen] = useState(false);
  // const [sellError, setSellError] = useState(null);

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

  useEffect(() => {
    // When we have basic holding data, fetch live price and compute derived values
    let isMounted = true;
    async function enrichWithLivePrice(base) {
      if (!base || !base.ticker) return;
      try {
        const res = await getStock(base.ticker);
        const info = res && res.data ? res.data : {};
        const livePrice = info.price ?? base.current_price ?? 0;
        const shares = parseFloat(base.shares) || 0;
        const market_value = +(shares * livePrice).toFixed(2);
        const cost_basis = parseFloat(base.cost_basis) || 0;
        const profit_loss = +(market_value - cost_basis * shares).toFixed(2);
        if (isMounted) {
          setData({ ...base, current_price: livePrice, market_value, profit_loss });
        }
      } catch (err) {
        // ignore live-price failure and keep existing values
        if (isMounted) setData(base);
      }
    }

    if (data) {
      enrichWithLivePrice(data);
    }

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

  const shares = Number(data.shares) || 0;
  const costBasis = Number(data.cost_basis) || 0;
  const currentPrice = Number(data.current_price) || 0;
  const marketValue = Number(data.market_value) || 0;
  const profitLoss = Number(data.profit_loss) || 0;
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