import { useEffect, useState } from "react";
import {
  getHoldings,
  getStock,
  sellHolding,
} from "../services/api";

function RemoveAssetModal({
  isOpen,
  onClose,
  onSubmit,
}) {
  const [holdings, setHoldings] = useState([]);
  const [selectedTicker, setSelectedTicker] =
    useState("");
  const [sharesToSell, setSharesToSell] =
    useState("");
  const [livePrice, setLivePrice] =
    useState(null);
  const [loading, setLoading] =
    useState(true);
  const [priceLoading, setPriceLoading] =
    useState(false);
  const [error, setError] =
    useState(null);

  useEffect(() => {
    if (!isOpen) {
      return;
    }

    setLoading(true);
    setError(null);
    setLivePrice(null);

    getHoldings(1)
      .then((result) => {
        if (!result.response.ok) {
          throw new Error(
            result.data?.error ||
              "Failed to load holdings."
          );
        }

        const holdingsData = Array.isArray(
          result.data
        )
          ? result.data
          : [];

        setHoldings(holdingsData);

        if (holdingsData.length > 0) {
          setSelectedTicker(
            holdingsData[0].ticker
          );
          setSharesToSell("");
        } else {
          setSelectedTicker("");
          setSharesToSell("");
        }
      })
      .catch((err) => {
        setError(
          err.message ||
            "Failed to load holdings."
        );
      })
      .finally(() => {
        setLoading(false);
      });
  }, [isOpen]);

  useEffect(() => {
    if (
      !selectedTicker ||
      holdings.length === 0
    ) {
      return;
    }

    const selectedHolding = holdings.find(
      (holding) =>
        holding.ticker === selectedTicker
    );

    if (!selectedHolding) {
      return;
    }

    setSharesToSell("");
    setLivePrice(null);
    setPriceLoading(true);
    setError(null);

    getStock(selectedTicker)
      .then((result) => {
        if (!result.response.ok) {
          throw new Error(
            result.data?.error ||
              "Unable to load current price."
          );
        }

        const fetchedPrice =
          Number.parseFloat(
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
        setError(
          err.message ||
            "Unable to load the current market price."
        );
      })
      .finally(() => {
        setPriceLoading(false);
      });
  }, [selectedTicker, holdings]);

  if (!isOpen) {
    return null;
  }

  const selectedHolding = holdings.find(
    (holding) =>
      holding.ticker === selectedTicker
  );

  const selectedShares = selectedHolding
    ? Number.parseFloat(
        selectedHolding.shares
      ) || 0
    : 0;

  const selectedCostBasis = selectedHolding
    ? Number.parseFloat(
        selectedHolding.cost_basis
      ) || 0
    : 0;

  const sellSharesValue =
    Number.parseFloat(sharesToSell) || 0;

  const currentPrice = livePrice ?? 0;

  const remainingShares = Math.max(
    0,
    selectedShares - sellSharesValue
  );

  const currentMarketValue =
    selectedShares * currentPrice;

  const currentProfitLoss =
    currentMarketValue -
    selectedCostBasis * selectedShares;

  const estimatedSaleProceeds =
    sellSharesValue * currentPrice;

  const remainingMarketValue =
    remainingShares * currentPrice;

  const remainingProfitLoss =
    remainingMarketValue -
    selectedCostBasis * remainingShares;

  const isNoHoldings =
    !loading && holdings.length === 0;

  const formatMoney = (value) =>
    Number(value).toLocaleString("en-US", {
      maximumFractionDigits: 2,
    });

  const formatShares = (value) =>
    Number(value).toLocaleString("en-US", {
      maximumFractionDigits: 4,
    });

  const handleClose = () => {
    setHoldings([]);
    setSelectedTicker("");
    setSharesToSell("");
    setLivePrice(null);
    setError(null);
    onClose();
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError(null);

    if (!selectedHolding) {
      setError(
        "Please select a ticker."
      );
      return;
    }

    const sharesValue =
      Number.parseFloat(sharesToSell);

    if (
      Number.isNaN(sharesValue) ||
      sharesValue <= 0 ||
      sharesValue > selectedShares
    ) {
      setError(
        "Enter a valid quantity to sell."
      );
      return;
    }

    try {
      const result = await sellHolding(
        1,
        selectedHolding.ticker,
        sharesValue
      );

      await onSubmit(result);
    } catch (err) {
      setError(
        err.message ||
          "Unable to sell holding."
      );
    }
  };

  return (
    <div
      className="modal-backdrop"
      onClick={handleClose}
    >
      <div
        className="modal"
        onClick={(event) =>
          event.stopPropagation()
        }
      >
        <div className="modal-header">
          <h3>Remove Asset</h3>

          <button
            type="button"
            className="close-btn"
            onClick={handleClose}
            aria-label="Close remove asset modal"
          >
            ×
          </button>
        </div>

        {loading ? (
          <p>Loading holdings...</p>
        ) : isNoHoldings ? (
          <p>
            No holdings available to remove.
          </p>
        ) : (
          <form
            onSubmit={handleSubmit}
            className="modal-form"
          >
            <div className="modal-body">
              <div className="modal-body-columns">
                <div className="left-fields">
                  <div className="form-group">
                    <label htmlFor="ticker">
                      Ticker
                    </label>

                    <select
                      id="ticker"
                      value={selectedTicker}
                      onChange={(event) =>
                        setSelectedTicker(
                          event.target.value
                        )
                      }
                      required
                    >
                      {holdings.map(
                        (holding) => (
                          <option
                            key={
                              holding.holding_id ??
                              holding.ticker
                            }
                            value={
                              holding.ticker
                            }
                          >
                            {holding.ticker}
                          </option>
                        )
                      )}
                    </select>
                  </div>

                  {selectedHolding && (
                    <>
                      <div className="form-group">
                        <label>
                          Company Name
                        </label>

                        <input
                          type="text"
                          value={
                            selectedHolding.company_name ||
                            ""
                          }
                          readOnly
                        />
                      </div>

                      <div className="form-group">
                        <label>
                          Owned Shares
                        </label>

                        <input
                          type="text"
                          value={formatShares(
                            selectedShares
                          )}
                          readOnly
                        />
                      </div>

                      <div className="form-group">
                        <label>
                          Current Price
                        </label>

                        <input
                          type="text"
                          value={
                            priceLoading
                              ? "Loading..."
                              : livePrice !==
                                  null
                                ? `$${formatMoney(
                                    livePrice
                                  )}`
                                : "Unavailable"
                          }
                          readOnly
                        />
                      </div>

                      <div className="form-group">
                        <label>
                          Cost Basis
                        </label>

                        <input
                          type="text"
                          value={`$${formatMoney(
                            selectedCostBasis
                          )}`}
                          readOnly
                        />
                      </div>

                      <div className="form-group">
                        <label>
                          Market Value
                        </label>

                        <input
                          type="text"
                          value={`$${formatMoney(
                            currentMarketValue
                          )}`}
                          readOnly
                        />
                      </div>

                      <div className="form-group">
                        <label>P/L</label>

                        <input
                          type="text"
                          value={`$${formatMoney(
                            currentProfitLoss
                          )}`}
                          readOnly
                        />
                      </div>
                    </>
                  )}

                  <div className="form-group">
                    <label htmlFor="sharesToSell">
                      Shares to Sell
                    </label>

                    <input
                      id="sharesToSell"
                      type="number"
                      step="0.0001"
                      min="0.0001"
                      max={selectedShares}
                      value={sharesToSell}
                      onChange={(event) =>
                        setSharesToSell(
                          event.target.value
                        )
                      }
                      placeholder="Enter shares"
                      required
                    />
                  </div>
                </div>

                {selectedHolding && (
                  <div className="sale-preview">
                    <h4>Sale Preview</h4>

                    <div className="form-group">
                      <label>
                        Estimated Sale Proceeds
                      </label>

                      <input
                        type="text"
                        value={`$${formatMoney(
                          estimatedSaleProceeds
                        )}`}
                        readOnly
                      />
                    </div>

                    <div className="form-group">
                      <label>
                        Remaining Shares
                      </label>

                      <input
                        type="text"
                        value={formatShares(
                          remainingShares
                        )}
                        readOnly
                      />
                    </div>

                    <div className="form-group">
                      <label>
                        Remaining Market Value
                      </label>

                      <input
                        type="text"
                        value={`$${formatMoney(
                          remainingMarketValue
                        )}`}
                        readOnly
                      />
                    </div>

                    <div className="form-group">
                      <label>
                        Remaining P/L
                      </label>

                      <input
                        type="text"
                        value={`$${formatMoney(
                          remainingProfitLoss
                        )}`}
                        readOnly
                      />
                    </div>
                  </div>
                )}
              </div>

              {error && (
                <div className="modal-error">
                  {error}
                </div>
              )}
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
                disabled={
                  priceLoading ||
                  livePrice === null ||
                  !selectedHolding ||
                  sellSharesValue <= 0 ||
                  sellSharesValue >
                    selectedShares
                }
              >
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