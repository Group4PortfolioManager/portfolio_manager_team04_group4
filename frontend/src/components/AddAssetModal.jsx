import { useEffect, useState } from "react";
import { getHoldings, getStock } from "../services/api";

const ASSET_TYPE_BY_ID = {
  1: "Stock",
  2: "Bond",
  3: "Crypto",
};

function AddAssetModal({ isOpen, onClose, onSubmit }) {
  const [assetId, setAssetId] = useState(1);
  const [ticker, setTicker] = useState("");
  const [holdings, setHoldings] = useState([]);
  const [shares, setShares] = useState("");
  const [livePrice, setLivePrice] = useState(null);
  const [priceLoading, setPriceLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!isOpen) {
      return;
    }

    getHoldings(1)
      .then((result) => {
        if (!result.response.ok) {
          return;
        }

        const holdings = Array.isArray(result.data)
          ? result.data
          : [];

        setHoldings(holdings);
      })
      .catch(() => {
        setHoldings([]);
      });
  }, [isOpen]);

  useEffect(() => {
    const cleanedTicker = ticker.trim().toUpperCase();

    if (!isOpen || !cleanedTicker) {
      setLivePrice(null);
      setError(null);
      return;
    }

    const timeoutId = setTimeout(() => {
      setPriceLoading(true);
      setError(null);

      getStock(cleanedTicker)
        .then((result) => {
          if (!result.response.ok) {
            throw new Error(
              result.data?.error ||
                "Unable to retrieve the current price."
            );
          }

          const fetchedPrice = Number.parseFloat(
            result.data?.price
          );

          if (
            Number.isNaN(fetchedPrice) ||
            fetchedPrice <= 0
          ) {
            throw new Error(
              "A valid current price was not returned."
            );
          }

          setLivePrice(fetchedPrice);
        })
        .catch((err) => {
          setLivePrice(null);
          setError(
            err.message ||
              "Unable to retrieve the current price."
          );
        })
        .finally(() => {
          setPriceLoading(false);
        });
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [ticker, isOpen]);

  if (!isOpen) {
    return null;
  }

  const sharesValue = Number.parseFloat(shares) || 0;

  const totalCost =
    livePrice !== null
      ? sharesValue * livePrice
      : 0;

  const normalizedTicker = ticker
    .trim()
    .toUpperCase();

  const selectedAssetType = ASSET_TYPE_BY_ID[assetId];

  const matchingHoldings = holdings.filter(
    (holding) => {
      const sameType =
        holding.asset_type === selectedAssetType;

      if (!sameType) {
        return false;
      }

      if (!normalizedTicker) {
        return true;
      }

      return String(holding.ticker || "")
        .toUpperCase()
        .includes(normalizedTicker);
    }
  );

  const resetForm = () => {
    setAssetId(1);
    setTicker("");
    setShares("");
    setLivePrice(null);
    setPriceLoading(false);
    setError(null);
  };

  const handleClose = () => {
    resetForm();
    onClose();
  };

  const handleAssetTypeChange = (event) => {
    setAssetId(Number(event.target.value));
    setTicker("");
    setLivePrice(null);
    setPriceLoading(false);
    setError(null);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError(null);

    const cleanedTicker = ticker.trim().toUpperCase();

    if (!cleanedTicker) {
      setError("Ticker is required.");
      return;
    }

    if (sharesValue <= 0) {
      setError("Shares must be greater than zero.");
      return;
    }

    if (livePrice === null) {
      setError(
        "A current market price must be available before submitting."
      );
      return;
    }

    try {
      await onSubmit({
        asset_id: assetId,
        ticker: cleanedTicker,
        shares: sharesValue,
      });

      resetForm();
    } catch (err) {
      setError(err.message || "Unable to add asset.");
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
              onChange={handleAssetTypeChange}
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
              list="ownedTickerOptions"
              onChange={(event) =>
                setTicker(event.target.value)
              }
              placeholder="Select or enter a ticker"
              autoComplete="off"
              required
            />

            <datalist id="ownedTickerOptions">
              {matchingHoldings.map((holding) => (
                <option
                  key={holding.holding_id ?? holding.ticker}
                  value={holding.ticker}
                >
                  {holding.company_name}
                </option>
              ))}
            </datalist>
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

          <div className="price-preview">
            <div className="price-preview-card">
              <span className="price-preview-label">
                Price Per Share
              </span>

              <span className="price-preview-value">
                {priceLoading
                  ? "Loading..."
                  : livePrice !== null
                    ? `$${livePrice.toLocaleString(
                        "en-US",
                        {
                          minimumFractionDigits: 2,
                          maximumFractionDigits: 2,
                        }
                      )}`
                    : "—"}
              </span>
            </div>

            <div className="price-preview-card">
              <span className="price-preview-label">
                Estimated Total Cost
              </span>

              <span className="price-preview-value">
                {livePrice !== null
                  ? `$${totalCost.toLocaleString(
                      "en-US",
                      {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      }
                    )}`
                  : "—"}
              </span>
            </div>
          </div>

          {error && (
            <div className="modal-error">
              {error}
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
              disabled={
                priceLoading ||
                livePrice === null ||
                sharesValue <= 0
              }
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