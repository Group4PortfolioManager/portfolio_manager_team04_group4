import { useEffect, useState } from "react";
import { getHoldings, getStock, sellHolding } from "../services/api";

function RemoveAssetModal({ isOpen, onClose, onSubmit }) {
  const [holdings, setHoldings] = useState([]);
  const [selectedTicker, setSelectedTicker] = useState("");
  const [sharesToSell, setSharesToSell] = useState("");
  const [price, setPrice] = useState("");
  const [livePrice, setLivePrice] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!isOpen) {
      return;
    }

    setLoading(true);
    getHoldings(1)
      .then((result) => {
        const holdingsData = Array.isArray(result.data) ? result.data : [];
        setHoldings(holdingsData);
        if (holdingsData.length > 0) {
          setSelectedTicker(holdingsData[0].ticker);
          setSharesToSell(holdingsData[0].shares);
        }
      })
      .catch((err) => setError(err.message || "Failed to load holdings."))
      .finally(() => setLoading(false));
  }, [isOpen]);

  useEffect(() => {
    if (!selectedTicker || holdings.length === 0) {
      return;
    }

    const selectedHolding = holdings.find((h) => h.ticker === selectedTicker);
    if (selectedHolding) {
      setSharesToSell(selectedHolding.shares);
      setPrice("");
      setLivePrice(null);

      getStock(selectedTicker)
        .then((result) => {
          const stockData = result?.data || {};
          const fetchedPrice = parseFloat(stockData.price);
          if (!Number.isNaN(fetchedPrice)) {
            setLivePrice(fetchedPrice);
            setPrice(fetchedPrice.toString());
          } else {
            setLivePrice(selectedHolding.current_price);
            setPrice(selectedHolding.current_price?.toString() || "");
          }
        })
        .catch(() => {
          setLivePrice(selectedHolding.current_price);
          setPrice(selectedHolding.current_price?.toString() || "");
        });
    }
  }, [selectedTicker, holdings]);

  if (!isOpen) {
    return null;
  }

  const selectedHolding = holdings.find((holding) => holding.ticker === selectedTicker);
  const currentPrice = selectedHolding ? (livePrice ?? selectedHolding.current_price) : 0;
  const selectedShares = selectedHolding ? parseFloat(selectedHolding.shares) || 0 : 0;
  const selectedCostBasis = selectedHolding ? parseFloat(selectedHolding.cost_basis) || 0 : 0;
  const sellSharesValue = parseFloat(sharesToSell) || 0;
  const sellPriceValue = parseFloat(price);
  const previewPrice = !Number.isNaN(sellPriceValue) && sellPriceValue > 0 ? sellPriceValue : currentPrice;
  const remainingShares = Math.max(0, selectedShares - sellSharesValue);
  const remainingMarketValue = +(remainingShares * currentPrice).toFixed(2);
  const remainingProfitLoss = +((remainingMarketValue - selectedCostBasis * remainingShares).toFixed(2));
  const isNoHoldings = !loading && holdings.length === 0;

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!selectedHolding) {
      setError("Please select a ticker.");
      return;
    }

    const sharesValue = parseFloat(sharesToSell);
    const priceValue = parseFloat(price);

    if (Number.isNaN(sharesValue) || sharesValue <= 0 || sharesValue > selectedHolding.shares) {
      setError("Enter a valid quantity to sell.");
      return;
    }

    if (Number.isNaN(priceValue) || priceValue <= 0) {
      setError("Enter a valid price.");
      return;
    }

    const result = await sellHolding(1, selectedHolding.ticker, sharesValue, priceValue);
    onSubmit(result);
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(event) => event.stopPropagation()}>
        <div className="modal-header">
          <h3>Remove Asset</h3>
          <button type="button" className="close-btn" onClick={onClose}>
            ×
          </button>
        </div>

        {loading ? (
          <p>Loading holdings...</p>
        ) : isNoHoldings ? (
          <p>No holdings available to remove.</p>
        ) : (
          <form onSubmit={handleSubmit} className="modal-form">
            <div className="modal-body">
              <div className="modal-body-columns">
                <div className="left-fields">
                  <div className="form-group">
                    <label htmlFor="ticker">Ticker</label>
                    <select
                      id="ticker"
                      value={selectedTicker}
                      onChange={(event) => setSelectedTicker(event.target.value)}
                      required
                    >
                      {holdings.map((holding) => (
                        <option key={holding.ticker} value={holding.ticker}>
                          {holding.ticker}
                        </option>
                      ))}
                    </select>
                  </div>

                  {selectedHolding && (
                    <>
                      <div className="form-group">
                        <label>Company Name</label>
                        <input type="text" value={selectedHolding.company_name} readOnly />
                      </div>

                      <div className="form-group">
                        <label>Owned Shares</label>
                        <input type="text" value={selectedHolding.shares} readOnly />
                      </div>

                      <div className="form-group">
                        <label>Current Price</label>
                        <input type="text" value={`$${livePrice ?? selectedHolding.current_price}`} readOnly />
                      </div>

                      <div className="form-group">
                        <label>Cost Basis</label>
                        <input type="text" value={`$${selectedHolding.cost_basis}`} readOnly />
                      </div>

                      <div className="form-group">
                        <label>Market Value</label>
                        <input
                          type="text"
                          value={`$${((parseFloat(selectedHolding.shares) || 0) * currentPrice).toFixed(2)}`}
                          readOnly
                        />
                      </div>

                      <div className="form-group">
                        <label>P/L</label>
                        <input
                          type="text"
                          value={`$${(
                            ((parseFloat(selectedHolding.shares) || 0) * currentPrice) -
                            ((parseFloat(selectedHolding.cost_basis) || 0) * (parseFloat(selectedHolding.shares) || 0))
                          ).toFixed(2)}`}
                          readOnly
                        />
                      </div>
                    </>
                  )}

                  <div className="form-group">
                    <label htmlFor="sharesToSell">Shares to Sell</label>
                    <input
                      id="sharesToSell"
                      type="number"
                      step="0.01"
                      min="0"
                      max={selectedHolding?.shares || 0}
                      value={sharesToSell}
                      onChange={(event) => setSharesToSell(event.target.value)}
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
                      required
                    />
                  </div>
                </div>

                {selectedHolding && (
                  <div className="sale-preview">
                    <h4>Sale Preview</h4>
                    <div className="form-group">
                      <label>Remaining Shares</label>
                      <input type="text" value={remainingShares.toFixed(4)} readOnly />
                    </div>
                    <div className="form-group">
                      <label>Remaining Market Value</label>
                      <input type="text" value={`$${remainingMarketValue.toFixed(2)}`} readOnly />
                    </div>
                    <div className="form-group">
                      <label>Remaining P/L</label>
                      <input type="text" value={`$${remainingProfitLoss.toFixed(2)}`} readOnly />
                    </div>
                  </div>
                )}
              </div>

              {error && <div className="modal-error">{error}</div>}
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
        )}
      </div>
    </div>
  );
}

export default RemoveAssetModal;
