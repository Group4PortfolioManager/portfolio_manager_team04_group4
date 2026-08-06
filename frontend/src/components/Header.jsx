function Header({
  portfolioId,
  portfolioName,
  onAddAsset,
  onRemoveAsset,
  onDepositCash,
  onWithdrawCash,
  summary,
}) {
  const totalValue = Number(summary?.total_value ?? 0);
  const totalReturn = Number(summary?.total_return ?? 0);
  const costBasis = Number(summary?.cost_basis_total ?? 0);
  const totalReturnPercent =
    costBasis !== 0
      ? (totalReturn / costBasis) * 100
      : 0;

  const daysGain = Number(summary?.day_gain ?? 0);
  const daysGainPercent = Number(
    summary?.day_gain_percent ?? 0
  );

  const formatMoney = (value) =>
    Math.abs(value).toLocaleString("en-US", {
      maximumFractionDigits: 2,
    });

  return (
    <header className="topbar">
      <div className="topbar-left">
        <h1>Portfolio Manager</h1>

        <span className="live-dot">
          {portfolioName ||
            `Portfolio #${portfolioId}`}{" "}
          | Live market data
        </span>
      </div>

      <div className="topbar-stats">
        <span className="stat-pill">
          Total Portfolio Value

          <strong>
            $
            {totalValue.toLocaleString("en-US", {
              maximumFractionDigits: 2,
            })}
          </strong>
        </span>

        <span className="stat-pill">
          Total Return

          <strong
            className={
              totalReturn >= 0
                ? "positive"
                : "negative"
            }
          >
            {totalReturn >= 0 ? "+" : "-"}$
            {formatMoney(totalReturn)}

            <span
              className={`stat-pct ${
                totalReturnPercent >= 0
                  ? "positive"
                  : "negative"
              }`}
            >
              {" "}
              (
              {totalReturnPercent >= 0
                ? "+"
                : "-"}
              {Math.abs(
                totalReturnPercent
              ).toFixed(1)}
              %)
            </span>
          </strong>
        </span>

        <span className="stat-pill">
          Day&apos;s Gain

          <strong
            className={
              daysGain >= 0
                ? "positive"
                : "negative"
            }
          >
            {daysGain >= 0 ? "+" : "-"}$
            {formatMoney(daysGain)}

            <span
              className={`stat-pct ${
                daysGainPercent >= 0
                  ? "positive"
                  : "negative"
              }`}
            >
              {" "}
              (
              {daysGainPercent >= 0
                ? "+"
                : "-"}
              {Math.abs(
                daysGainPercent
              ).toFixed(1)}
              %)
            </span>
          </strong>
        </span>
      </div>

      <div className="topbar-actions">
        <button
          type="button"
          className="btn btn-secondary"
          onClick={onDepositCash}
        >
          Deposit Cash
        </button>

        <button
          type="button"
          className="btn btn-secondary"
          onClick={onWithdrawCash}
        >
          Withdraw Cash
        </button>

        <button
          type="button"
          className="btn btn-primary"
          onClick={onAddAsset}
        >
          + Add Asset
        </button>

        <button
          type="button"
          className="btn btn-secondary"
          onClick={onRemoveAsset}
        >
          Remove Asset
        </button>
      </div>
    </header>
  );
}

export default Header;