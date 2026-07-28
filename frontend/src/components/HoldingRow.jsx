function HoldingRow({ holding }) {
  return (
    <tr>
      <td className="ticker-symbol">{holding.ticker}</td>
      <td>{holding.company_name}</td>
      <td className="mono">{holding.shares}</td>
      <td className="mono">${holding.current_price}</td>
      <td className="mono">${holding.cost_basis}</td>
      <td className="mono">${holding.market_value}</td>

      <td className={holding.profit_loss >= 0 ? "positive" : "negative"}>
        {holding.profit_loss >= 0 ? "+" : ""}${holding.profit_loss}
      </td>

    </tr>
  );
}

export default HoldingRow;