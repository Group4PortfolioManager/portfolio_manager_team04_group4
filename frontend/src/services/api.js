const API_BASE_URL = "http://127.0.0.1:5000";

/* GET METHOD */
async function fetchJson(url) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 100000);

  try {
    const response = await fetch(url, {
      signal: controller.signal,
    });

    let data = null;

    try {
      data = await response.json();
    } catch {
      data = null;
    }

    return { response, data };
  } finally {
    clearTimeout(timeoutId);
  }
}

async function fetchWithJsonFallback(url, options) {
  const response = await fetch(url, options);
  const contentType =
    response.headers.get("content-type") || "";

  let data;

  if (contentType.includes("application/json")) {
    try {
      data = await response.json();
    } catch {
      data = null;
    }
  } else {
    const text = await response.text();

    data = {
      error: response.ok
        ? "Unexpected non-JSON response from server."
        : text ||
          "Server returned a non-JSON error response.",
    };
  }

  return { response, data };
}

async function getPortfolio(portfolioId) {
  return fetchJson(
    `${API_BASE_URL}/portfolios/${portfolioId}`
  );
}

async function getPortfolios() {
  return fetchJson(`${API_BASE_URL}/portfolios`);
}

async function createPortfolio(portfolioName) {
  return fetchWithJsonFallback(
    `${API_BASE_URL}/portfolios`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        portfolio_name: portfolioName,
      }),
    }
  );
}

async function deletePortfolio(portfolioId) {
  return fetchWithJsonFallback(
    `${API_BASE_URL}/portfolios/${portfolioId}`,
    {
      method: "DELETE",
    }
  );
}

async function getHoldings(portfolioId) {
  return fetchJson(
    `${API_BASE_URL}/portfolios/${portfolioId}/holdings`
  );
}

async function getPortfolioPerformance(
  portfolioId,
  windowType = "months",
  windowSize = 12
) {
  return fetchJson(
    `${API_BASE_URL}/portfolios/${portfolioId}/performance?window_type=${windowType}&window_size=${windowSize}`
  );
}

async function getHolding(holdingId) {
  return fetchJson(
    `${API_BASE_URL}/holdings/${holdingId}`
  );
}

async function getAssets() {
  return fetchJson(`${API_BASE_URL}/assets`);
}

async function getStockHistory(
  ticker,
  startDate,
  endDate,
  interval = "1d"
) {
  return fetchJson(
    `${API_BASE_URL}/stocks/${ticker}/history?start_date=${startDate}&end_date=${endDate}&interval=${interval}`
  );
}

async function getStock(ticker) {
  return fetchJson(
    `${API_BASE_URL}/stocks/${ticker}`
  );
}

async function buyHolding(
  portfolioId,
  assetId,
  ticker,
  shares
) {
  return fetchWithJsonFallback(
    `${API_BASE_URL}/portfolios/${portfolioId}/buy`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        asset_id: assetId,
        ticker,
        shares,
      }),
    }
  );
}

async function sellHolding(
  portfolioId,
  ticker,
  shares
) {
  return fetchWithJsonFallback(
    `${API_BASE_URL}/portfolios/${portfolioId}/sell`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        ticker,
        shares,
      }),
    }
  );
}

async function depositCash(
  portfolioId,
  amount
) {
  return fetchWithJsonFallback(
    `${API_BASE_URL}/portfolios/${portfolioId}/cash/deposit`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ amount }),
    }
  );
}

async function withdrawCash(
  portfolioId,
  amount
) {
  return fetchWithJsonFallback(
    `${API_BASE_URL}/portfolios/${portfolioId}/cash/withdraw`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ amount }),
    }
  );
}

export {
  fetchJson,
  getPortfolios,
  createPortfolio,
  deletePortfolio,
  getPortfolio,
  getPortfolioPerformance,
  getHoldings,
  getHolding,
  getAssets,
  getStockHistory,
  getStock,
  buyHolding,
  sellHolding,
  depositCash,
  withdrawCash,
};