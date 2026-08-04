import { useState } from "react";

function CashModal({
  isOpen,
  mode,
  onClose,
  onSubmit,
  currentBalance,
}) {
  const [amount, setAmount] = useState("");
  const [localError, setLocalError] = useState(null);

  if (!isOpen) {
    return null;
  }

  const isDeposit = mode === "deposit";
  const title = isDeposit ? "Deposit Cash" : "Withdraw Cash";

  const resetForm = () => {
    setAmount("");
    setLocalError(null);
  };

  const handleClose = () => {
    resetForm();
    onClose();
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLocalError(null);

    const amountValue = Number.parseFloat(amount);

    if (Number.isNaN(amountValue) || amountValue <= 0) {
      setLocalError("Please enter an amount greater than zero.");
      return;
    }

    if (!isDeposit && amountValue > currentBalance) {
      setLocalError("Withdrawal amount exceeds current cash balance.");
      return;
    }

    try {
      await onSubmit(amountValue);
      resetForm();
    } catch {
      // Parent component handles server-side errors.
    }
  };

  return (
    <div
      className="modal-backdrop"
      onClick={handleClose}
    >
      <div
        className="modal"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="modal-header">
          <h3>{title}</h3>

          <button
            type="button"
            className="close-btn"
            onClick={handleClose}
            aria-label={`Close ${title.toLowerCase()} modal`}
          >
            ×
          </button>
        </div>

        <form
          onSubmit={handleSubmit}
          className="modal-form"
        >
          <div className="form-group">
            <label>Current Cash Balance</label>
            <input
              type="text"
              value={`$${Number(currentBalance || 0).toLocaleString("en-US", {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              })}`}
              readOnly
            />
          </div>

          <div className="form-group">
            <label htmlFor="cashAmount">Amount</label>
            <input
              id="cashAmount"
              type="number"
              step="0.01"
              min="0.01"
              value={amount}
              onChange={(event) => setAmount(event.target.value)}
              placeholder={isDeposit ? "500.00" : "200.00"}
              required
            />
          </div>

          {localError && (
            <div className="modal-error">
              {localError}
            </div>
          )}

          <div className="modal-footer">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={handleClose}
            >
              Cancel
            </button>

            <button
              type="submit"
              className="btn btn-primary"
            >
              {isDeposit ? "Deposit" : "Withdraw"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default CashModal;
