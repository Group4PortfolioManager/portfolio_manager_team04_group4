function HoldingRow({ holding }) {
  const totalCost = holding.cost_basis * holding.shares;
  const profitLossPct = totalCost !== 0 ? (holding.profit_loss / totalCost) * 100 : 0;

  return (
    <tr>
      <td className="ticker-symbol">{holding.ticker}</td>
      <td>{holding.company_name}</td>
      <td className="mono">{holding.shares.toLocaleString("en-US", {
        maximumFractionDigits: 2
      })}</td>
      <td className="mono">${holding.current_price.toLocaleString("en-US", {
        maximumFractionDigits: 2
      })}</td>
      <td className="mono">${holding.cost_basis.toLocaleString("en-US", {
        maximumFractionDigits: 2
      })}</td>
      <td className="mono">${holding.market_value.toLocaleString("en-US", {
        maximumFractionDigits: 2
      })}</td>
 

      <td className={holding.profit_loss >= 0 ? "positive" : "negative"}>
        {holding.profit_loss >= 0 ? "+" : "-"}$
        {Math.abs(holding.profit_loss).toLocaleString("en-US", {
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