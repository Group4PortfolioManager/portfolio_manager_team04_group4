import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import {
  getHoldings,
  getStock,
} from "../services/api";

import { useDataRefresh } from "../services/refreshStore";
import HoldingRow from "./HoldingRow";


function HoldingsTable({ showLink = false }) {
  const [holdings, setHoldings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const refreshKey = useDataRefresh();
  const sectionTitle = showLink
    ? "Top Holdings"
    : "Your Holdings";

  useEffect(() => {
    let isActive = true;

    const loadHoldings = async () => {
      setLoading(true);
      setError(null);

      try {
        const result = await getHoldings(1);

        if (!result.response.ok) {
          throw new Error(
            result.data?.error ||
              "Failed to load holdings."
          );
        }

        const holdingsData = Array.isArray(result.data)
          ? result.data
          : [];

        const enrichedHoldings = await Promise.all(
          holdingsData.map(async (holding) => {
            try {
              const stockResult = await getStock(
                holding.ticker
              );

              if (!stockResult.response.ok) {
                throw new Error(
                  stockResult.data?.error ||
                    "Unable to load current price."
                );
              }

              const currentPrice = Number(
                stockResult.data?.price ?? 0
              );

              const shares = Number(
                holding.shares ?? 0
              );

              const costBasis = Number(
                holding.cost_basis ?? 0
              );

              const marketValue =
                shares * currentPrice;

              const profitLoss =
                marketValue -
                shares * costBasis;

              const totalCost =
                shares * costBasis;

              const profitLossPercent =
                totalCost > 0
                  ? (profitLoss / totalCost) * 100
                  : 0;

              return {
                ...holding,
                current_price: currentPrice,
                market_value: marketValue,
                profit_loss: profitLoss,
                profit_loss_percent:
                  profitLossPercent,
              };
            } catch {
              return {
                ...holding,
                current_price: 0,
                market_value: 0,
                profit_loss: 0,
                profit_loss_percent: 0,
              };
            }
          })
        );

        if (isActive) {
          setHoldings(enrichedHoldings);
        }
      } catch (err) {
        if (isActive) {
          setError(
            err.message ||
              "Failed to load holdings."
          );
        }
      } finally {
        if (isActive) {
          setLoading(false);
        }
      }
    };

    loadHoldings();

    return () => {
      isActive = false;
    };
  }, [refreshKey]);

  const displayedHoldings = showLink
    ? [...holdings]
        .sort(
          (firstHolding, secondHolding) =>
            Number(
              secondHolding.market_value ?? 0
            ) -
            Number(
              firstHolding.market_value ?? 0
            )
        )
        .slice(0, 4)
    : holdings;

  if (loading) {
    return (
      <div className="panel panel-holdings">
        <h2>{sectionTitle}</h2>
        <p>Loading holdings...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="panel panel-holdings">
        <h2>{sectionTitle}</h2>
        <p>Error loading holdings: {error}</p>
      </div>
    );
  }

  if (holdings.length === 0) {
    return (
      <div className="panel panel-holdings">
        <h2>{sectionTitle}</h2>
        <p>No holdings for the moment.</p>
      </div>
    );
  }

  return (
    <div className="panel panel-holdings">
      <h2>{sectionTitle}</h2>

      <table>
        <thead>
          <tr>
            <th>Ticker</th>
            <th>Company Name</th>
            <th>Shares</th>
            <th>Current Price</th>
            <th>Cost Basis</th>
            <th>Market Value</th>
            <th>P/L</th>
          </tr>
        </thead>

        <tbody>
          {displayedHoldings.map((holding) => (
            <HoldingRow
              key={
                holding.holding_id ??
                holding.ticker
              }
              holding={holding}
            />
          ))}
        </tbody>
      </table>

      {showLink && (
        <Link
          to="/holdings"
          className="text-link"
        >
          View All Holdings
        </Link>
      )}
    </div>
  );
}

export default HoldingsTable;