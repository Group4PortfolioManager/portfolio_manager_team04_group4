import { useState } from "react";

function AddAssetModal({ isOpen, onClose, onSubmit }) {
  const [assetId, setAssetId] = useState(1);
  const [ticker, setTicker] = useState("");
  const [shares, setShares] = useState("");

  if (!isOpen) {
    return null;
  }

  const resetForm = () => {
    setAssetId(1);
    setTicker("");
    setShares("");
  };

  const handleClose = () => {
    resetForm();
    onClose();
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    const sharesValue = Number.parseFloat(shares);
    const cleanedTicker = ticker.trim().toUpperCase();

    if (
      !cleanedTicker ||
      Number.isNaN(sharesValue) ||
      sharesValue <= 0
    ) {
      return;
    }

    await onSubmit({
      asset_id: assetId,
      ticker: cleanedTicker,
      shares: sharesValue,
    });

    resetForm();
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
          <h3>Add Asset</h3>

          <button
            type="button"
            className="close-btn"
            onClick={handleClose}
            aria-label="Close add asset modal"
          >
            ×
          </button>
        </div>

        <form
          onSubmit={handleSubmit}
          className="modal-form"
        >
          <div className="form-group">
            <label htmlFor="assetType">
              Asset Type
            </label>

            <select
              id="assetType"
              value={assetId}
              onChange={(event) =>
                setAssetId(Number(event.target.value))
              }
            >
              <option value={1}>Stock</option>
              <option value={2}>Bond</option>
              <option value={3}>Crypto</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="ticker">
              Ticker
            </label>

            <input
              id="ticker"
              type="text"
              value={ticker}
              onChange={(event) =>
                setTicker(event.target.value)
              }
              placeholder="AAPL"
              autoComplete="off"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="shares">
              Shares
            </label>

            <input
              id="shares"
              type="number"
              step="0.0001"
              min="0.0001"
              value={shares}
              onChange={(event) =>
                setShares(event.target.value)
              }
              placeholder="25"
              required
            />
          </div>

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
              Submit
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default AddAssetModal;