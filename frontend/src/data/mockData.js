export const holdings = [
  {
    ticker: "AAPL",
    company_name: "Apple Inc.",
    shares: 25,
    current_price: 225.50,
    cost_basis: 250.00,
    market_value: 5637.50,
    profit_loss: -612.50
  },
  {
    ticker: "MSFT",
    company_name: "Microsoft Corp.",
    shares: 15,
    current_price: 520.00,
    cost_basis: 400.00,
    market_value: 7800.00,
    profit_loss: 1800.00
  },
  {
    ticker: "NVDA",
    company_name: "NVIDIA Corp.",
    shares: 20,
    current_price: 170.00,
    cost_basis: 110.00,
    market_value: 3400.00,
    profit_loss: 1200.00
  },
  {
    ticker: "TSLA",
    company_name: "Tesla Inc.",
    shares: 10.2,
    current_price: 350.00,
    cost_basis: 300.00,
    market_value: 3500.00,
    profit_loss: 500.00
  }
];


export const portfolioSummary = {
  total_value: 20337.50,
  total_return: 4637.50
};


export const assetAllocation = [
  {
    type: "Stocks",
    percentage: 75,
    color: "#3b82f6"
  },
  {
    type: "Bonds",
    percentage: 5,
    color: "#22d3ee"
  },
  {
    type: "Crypto",
    percentage: 10,
    color: "#f59e0b"
  },
  {
    type: "Cash",
    percentage: 10,
    color: "#a78bfa"
  }
].map((asset) => ({
  ...asset,
  value: Math.round(portfolioSummary.total_value * (asset.percentage / 100) * 100) / 100
}));


export const performanceHistory = [
  { label: "Apr", value: 15600 },
  { label: "Apr", value: 15950 },
  { label: "May", value: 15700 },
  { label: "May", value: 16400 },
  { label: "May", value: 16150 },
  { label: "Jun", value: 14000 },
  { label: "Jun", value: 17300 },
  { label: "Jun", value: 17050 },
  { label: "Jul", value: 17800 },
  { label: "Jul", value: 18400 },
  { label: "Jul", value: 18150 },
  { label: "Jul", value: 20337.5 }
];