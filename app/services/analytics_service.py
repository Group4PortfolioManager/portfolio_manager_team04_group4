from bisect import bisect_right
from datetime import date, datetime, timedelta

from app.services.database_service import DataBaseService
from app.services.yahoo_service import get_historical_data


def _month_end_dates(window_size=12):
	"""Return chronological month-end dates including current month."""
	today = date.today()
	year = today.year
	month = today.month
	points = []

	for offset in range(window_size - 1, -1, -1):
		m = month - offset
		y = year
		while m <= 0:
			m += 12
			y -= 1

		next_month = m + 1
		next_year = y
		if next_month == 13:
			next_month = 1
			next_year += 1

		month_end = date(next_year, next_month, 1) - timedelta(days=1)
		if month_end > today:
			month_end = today

		points.append(month_end)

	return points


def _day_points(window_size=12):
	"""Return chronological day points including today."""
	today = date.today()
	start = today - timedelta(days=window_size - 1)
	return [start + timedelta(days=offset) for offset in range(window_size)]


def _build_points(window_type="months", window_size=12):
	if window_type == "days":
		return _day_points(window_size)

	return _month_end_dates(window_size)


def _format_label(point_date, window_type="months"):
	if window_type == "days":
		return point_date.strftime("%d %b")

	return point_date.strftime("%b")


def _extract_price_series(frame):
	"""Return sorted trading dates and close prices from yfinance dataframe."""
	if frame is None or frame.empty or "Close" not in frame:
		return [], []

	dates = []
	prices = []
	for idx, row in frame.iterrows():
		close_value = row.get("Close")
		if close_value is None:
			continue

		dates.append(idx.date())
		prices.append(float(close_value))

	return dates, prices


def _latest_price_on_or_before(point_date, trading_dates, trading_prices):
	if not trading_dates:
		return None

	position = bisect_right(trading_dates, point_date) - 1
	if position < 0:
		return None

	return trading_prices[position]


def get_portfolio_performance_history(portfolio_id, window_type="months", window_size=12):
	"""
	Build a time-window performance curve using:
	- Current cash balance from portfolio
	- Holdings from database
	- Historical close prices from Yahoo by day

	Returns a list of points: [{"date": "YYYY-MM-DD", "label": "Mon", "value": 1234.56}, ...]
	"""
	db_service = DataBaseService()

	portfolio = db_service.get_portfolio_by_id(portfolio_id)
	if not portfolio:
		return None

	holdings = db_service.get_portfolio_holdings(portfolio_id) or []
	cash_balance = float(portfolio.get("cash_balance") or 0)

	# When there are no holdings, the portfolio value is flat at cash balance.
	if not holdings:
		points = _build_points(window_type=window_type, window_size=window_size)
		return [
			{
				"date": point.isoformat(),
				"label": _format_label(point, window_type=window_type),
				"value": round(cash_balance, 2),
			}
			for point in points
		]

	points = _build_points(window_type=window_type, window_size=window_size)
	start_date = points[0]
	end_date = points[-1] + timedelta(days=1)

	# Map: ticker -> (trading_dates[], trading_prices[])
	ticker_price_series = {}
	for holding in holdings:
		ticker = (holding.get("ticker") or "").strip().upper()
		if not ticker:
			continue

		try:
			frame = get_historical_data(
				ticker=ticker,
				start_date=datetime.combine(start_date, datetime.min.time()),
				end_date=datetime.combine(end_date, datetime.min.time()),
				interval="1d",
			)
		except Exception:
			frame = None

		ticker_price_series[ticker] = _extract_price_series(frame)

	history = []
	for point in points:
		total_value = cash_balance

		for holding in holdings:
			purchase_date = holding.get("purchase_date")
			if purchase_date is None:
				continue

			if isinstance(purchase_date, datetime):
				purchase_day = purchase_date.date()
			else:
				purchase_day = purchase_date

			# Exclude holdings not yet purchased at this point in time.
			if purchase_day > point:
				continue

			ticker = (holding.get("ticker") or "").strip().upper()
			shares = float(holding.get("shares") or 0)
			cost_basis = float(holding.get("cost_basis") or 0)

			trading_dates, trading_prices = ticker_price_series.get(ticker, ([], []))
			price = _latest_price_on_or_before(point, trading_dates, trading_prices)
			if price is None:
				price = cost_basis

			total_value += shares * price

		history.append(
			{
				"date": point.isoformat(),
				"label": _format_label(point, window_type=window_type),
				"value": round(total_value, 2),
			}
		)

	return history
