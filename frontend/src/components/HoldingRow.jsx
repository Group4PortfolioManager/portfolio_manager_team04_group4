import { useEffect, useMemo, useState } from "react";
import { getHolding } from "../services/api";

function HoldingRow({ holding, holdingId }) {
  const [fetchedData, setFetchedData] = useState(null);
  const [loading, setLoading] = useState(
    !holding && Boolean(holdingId)
  );
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;

    if (!holdingId || holding) {
      return () => {
        isMounted = false;
      };
    }

    setLoading(true);
    setError(null);

    getHolding(holdingId)
      .then((result) => {
        if (!isMounted) {
          return;
        }

        if (!result.response.ok) {
          throw new Error(
            result.data?.error ||
              "Unable to load holding."
          );
        }

        const fetched = Array.isArray(result.data)
          ? result.data[0]
          : result.data;

        setFetchedData(fetched);
      })
      .catch((err) => {
        if (isMounted) {
          setError(
            err.message || "Unable to load holding."
          );
        }
      })
      .finally(() => {
        if (isMounted) {
          setLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [holdingId, holding]);

  const data = useMemo(
    () => holding || fetchedData || null,
    [holding, fetchedData]
  );

  if (loading) {
    return (
      <tr>
        <td colSpan="7">Loading...</td>
      </tr>
    );
  }

  if (error) {
    return (
      <tr>
        <td colSpan="7">
          Error loading holding: {error}
        </td>
      </tr>
    );
  }

  if (!data) {
    return null;
  }

  const currentPrice = Number(
    data.current_price ?? 0
  );

  const shares = Number(
    data.shares ?? 0
  );

  const costBasis = Number(
    data.cost_basis ?? 0
  );

  const marketValue = Number(
    data.market_value ??
      shares * currentPrice
  );

  const profitLoss = Number(
    data.profit_loss ??
      marketValue - costBasis * shares
  );

  const totalCost = costBasis * shares;

  const profitLossPct = Number(
    data.profit_loss_percent ??
      (
        totalCost > 0
          ? (profitLoss / totalCost) * 100
          : 0
      )
  );

  return (
    <tr>
      <td className="ticker-symbol">
        {data.ticker}
      </td>

      <td>
        {data.company_name}
      </td>

      <td className="mono">
        {shares.toLocaleString("en-US", {
          maximumFractionDigits: 4,
        })}
      </td>

      <td className="mono">
        $
        {currentPrice.toLocaleString("en-US", {
          maximumFractionDigits: 2,
        })}
      </td>

      <td className="mono">
        $
        {costBasis.toLocaleString("en-US", {
          maximumFractionDigits: 2,
        })}
      </td>

      <td className="mono">
        $
        {marketValue.toLocaleString("en-US", {
          maximumFractionDigits: 2,
        })}
      </td>

      <td
        className={
          profitLoss >= 0
            ? "positive"
            : "negative"
        }
      >
        {profitLoss >= 0 ? "+" : "-"}$
        {Math.abs(profitLoss).toLocaleString(
          "en-US",
          {
            maximumFractionDigits: 2,
          }
        )}
        {" "}
        (
        {profitLossPct >= 0 ? "+" : "-"}
        {Math.abs(profitLossPct).toFixed(2)}
        %)
      </td>
    </tr>
  );
}

export default HoldingRow;