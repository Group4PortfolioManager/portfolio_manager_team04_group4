const API_BASE_URL = 'http://127.0.0.1:5000';

/*GET METHOD*/
async function fetchJson(url) {
  const response = await fetch(url);
  const data = await response.json();
  return { response, data };
}

async function getPortfolio(portfolioId) {
  return fetchJson(`${API_BASE_URL}/portfolios/${portfolioId}`);
}

async function getHoldings(portfolioId) {
  return fetchJson(`${API_BASE_URL}/portfolios/${portfolioId}/holdings`);
}

async function getHolding(holdingId) {
  return fetchJson(`${API_BASE_URL}/holdings/${holdingId}`);
}

async function getAssets() {
  return fetchJson(`${API_BASE_URL}/assets`);
}

async function getStockHistory(ticker, startDate, endDate, interval = '1d') {
  return fetchJson(`${API_BASE_URL}/stocks/${ticker}/history?start_date=${startDate}&end_date=${endDate}&interval=${interval}`);
}

async function buyHolding(portfolioId, ticker, shares, price) {
  return fetch(`${API_BASE_URL}/portfolios/${portfolioId}/buy`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ticker, shares, price })
  }).then(async (response) => ({ response, data: await response.json() }));
}

async function sellHolding(portfolioId, ticker, shares, price) {
  return fetch(`${API_BASE_URL}/portfolios/${portfolioId}/sell`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ticker, shares, price })
  }).then(async (response) => ({ response, data: await response.json() }));
}