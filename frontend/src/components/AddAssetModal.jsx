import { useState } from "react";
import { buyHolding } from "../services/api";

function AddAssetModal({ isOpen, onClose, onSubmit }) {
  const [ticker, setTicker] = useState("");
  const [shares, setShares] = useState("");
  const [price, setPrice] = useState("");

  if (!isOpen) {
    return null;
  }

  const handleSubmit = async (event) => {
    event.preventDefault();
    const sharesValue = parseFloat(shares);
    const priceValue = parseFloat(price);
    if (!ticker || Number.isNaN(sharesValue) || Number.isNaN(priceValue)) {
      return;
    }

    const result = await buyHolding(1, ticker.toUpperCase(), sharesValue, priceValue);
    onSubmit(result);
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(event) => event.stopPropagation()}>
        <div className="modal-header">
          <h3>Add Asset</h3>
          <button type="button" className="close-btn" onClick={onClose}>
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} className="modal-form">
          <div className="form-group">
            <label htmlFor="ticker">Ticker</label>
            <input
              id="ticker"
              type="text"
              value={ticker}
              onChange={(event) => setTicker(event.target.value)}
              placeholder="AAPL"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="shares">Shares</label>
            <input
              id="shares"
              type="number"
              step="0.01"
              min="0"
              value={shares}
              onChange={(event) => setShares(event.target.value)}
              placeholder="25"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="price">Price</label>
            <input
              id="price"
              type="number"
              step="0.01"
              min="0"
              value={price}
              onChange={(event) => setPrice(event.target.value)}
              placeholder="225.50"
              required
            />
          </div>

          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary">
              Submit
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default AddAssetModal;
