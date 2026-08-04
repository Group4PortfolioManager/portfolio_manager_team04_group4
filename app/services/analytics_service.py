from datetime import date, datetime, timedelta

from app.services.database_service import DataBaseService


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


def _coerce_snapshot_date(value):
	if isinstance(value, datetime):
		return value.date()

	if isinstance(value, str):
		try:
			return datetime.strptime(
				value,
				"%Y-%m-%d",
			).date()
		except ValueError:
			return None

	return value


def get_portfolio_performance_history(portfolio_id, window_type="months", window_size=12):
	"""
	Build a time-window performance curve from saved
	daily portfolio snapshots.

	Returns a list of points: [{"date": "YYYY-MM-DD", "label": "Mon", "value": 1234.56}, ...]
	"""
	db_service = DataBaseService()

	portfolio = db_service.get_portfolio_by_id(portfolio_id)
	if not portfolio:
		return None

	points = _build_points(window_type=window_type, window_size=window_size)
	start_date = points[0]
	end_date = points[-1]

	# Update today's snapshot before reading the requested window.
	db_service.upsert_portfolio_snapshot(portfolio_id)

	seed_snapshot = db_service.get_latest_portfolio_snapshot_before(
		portfolio_id,
		start_date,
	)

	snapshots = db_service.get_portfolio_snapshots(
		portfolio_id,
		start_date=start_date,
		end_date=end_date,
	)

	if not snapshots:
		summary = db_service.get_portfolio_summary(portfolio_id)
		fallback_value = float(
			(summary or {}).get("total_value") or 0
		)

		return [
			{
				"date": point.isoformat(),
				"label": _format_label(point, window_type=window_type),
				"value": round(fallback_value, 2),
			}
			for point in points
		]

	snapshot_values = {}
	if seed_snapshot:
		seed_day = _coerce_snapshot_date(
			seed_snapshot.get("snapshot_date")
		)

		if seed_day is not None:
			snapshot_values[seed_day] = float(
				seed_snapshot.get("portfolio_value") or 0
			)

	for row in snapshots:
		snapshot_day = _coerce_snapshot_date(
			row.get("snapshot_date")
		)

		if snapshot_day is None:
			continue

		snapshot_values[snapshot_day] = float(
			row.get("portfolio_value") or 0
		)

	sorted_snapshot_days = sorted(snapshot_values.keys())
	latest_value = float(portfolio.get("cash_balance") or 0)
	day_index = 0

	history = []
	for point in points:
		while (
			day_index < len(sorted_snapshot_days)
			and sorted_snapshot_days[day_index] <= point
		):
			latest_value = snapshot_values[
				sorted_snapshot_days[day_index]
			]
			day_index += 1

		history.append(
			{
				"date": point.isoformat(),
				"label": _format_label(point, window_type=window_type),
				"value": round(latest_value, 2),
			}
		)

	return history
