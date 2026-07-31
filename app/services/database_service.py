from decimal import Decimal, InvalidOperation

from app.database import get_db_connection
from app.services.yahoo_service import get_info


class DataBaseService:
    def __init__(self):
        self._db = None

    @property
    def db(self):
        # Create a connection if one does not exist or was disconnected.
        if self._db is None or not self._db.is_connected():
            self._db = get_db_connection()

        return self._db

    # Portfolio Read Methods

    def get_all_portfolios(self):
        cursor = self.db.cursor(dictionary=True)

        try:
            cursor.execute(
                "SELECT * FROM portfolio;"
            )

            return cursor.fetchall()

        finally:
            cursor.close()

    def get_portfolio_by_id(self, portfolio_id):
        cursor = self.db.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT *
                FROM portfolio
                WHERE portfolio_id = %s;
                """,
                (portfolio_id,),
            )

            # One ID should return one object, not a list.
            return cursor.fetchone()

        finally:
            cursor.close()

    # Holding Read Methods

    def get_portfolio_holdings(self, portfolio_id):
        cursor = self.db.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT
                    h.holding_id,
                    h.portfolio_id,
                    h.asset_id,
                    a.asset_type,
                    h.ticker,
                    h.company_name,
                    h.shares,
                    h.cost_basis,
                    h.purchase_date
                FROM holdings AS h
                INNER JOIN asset AS a
                    ON h.asset_id = a.asset_id
                WHERE h.portfolio_id = %s
                ORDER BY h.ticker;
                """,
                (portfolio_id,),
            )

            return cursor.fetchall()

        finally:
            cursor.close()

    def get_holding_by_id(self, holding_id):
        cursor = self.db.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT
                    h.holding_id,
                    h.portfolio_id,
                    h.asset_id,
                    a.asset_type,
                    h.ticker,
                    h.company_name,
                    h.shares,
                    h.cost_basis,
                    h.purchase_date
                FROM holdings AS h
                INNER JOIN asset AS a
                    ON h.asset_id = a.asset_id
                WHERE h.holding_id = %s;
                """,
                (holding_id,),
            )

            # One ID should return one object, not a list.
            return cursor.fetchone()

        finally:
            cursor.close()

    def get_holding_by_ticker(self, portfolio_id, ticker):
        """
        Look up a ticker inside a specific portfolio.

        portfolio_id is needed because the unique database
        constraint applies to portfolio_id and ticker together.
        """
        cursor = self.db.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT
                    h.holding_id,
                    h.portfolio_id,
                    h.asset_id,
                    a.asset_type,
                    h.ticker,
                    h.company_name,
                    h.shares,
                    h.cost_basis,
                    h.purchase_date
                FROM holdings AS h
                INNER JOIN asset AS a
                    ON h.asset_id = a.asset_id
                WHERE h.portfolio_id = %s
                  AND h.ticker = %s;
                """,
                (
                    portfolio_id,
                    ticker.strip().upper(),
                ),
            )

            return cursor.fetchone()

        finally:
            cursor.close()

    # Asset Read Methods

    def get_all_assets(self):
        cursor = self.db.cursor(dictionary=True)

        try:
            cursor.execute(
                "SELECT * FROM asset;"
            )

            return cursor.fetchall()

        finally:
            cursor.close()

    def get_asset_by_id(self, asset_id):
        cursor = self.db.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT *
                FROM asset
                WHERE asset_id = %s;
                """,
                (asset_id,),
            )

            # One ID should return one object, not a list.
            return cursor.fetchone()

        finally:
            cursor.close()

    # Portfolio Create Method

    def add_portfolio(self, portfolio):
        cursor = self.db.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO portfolio (
                    portfolio_name,
                    cash_balance,
                    created_at
                )
                VALUES (%s, %s, NOW());
                """,
                (
                    portfolio["portfolio_name"],
                    portfolio["cash_balance"],
                ),
            )

            self.db.commit()

            return {
                "portfolio_id": cursor.lastrowid,
                "portfolio_name": portfolio["portfolio_name"],
                "cash_balance": portfolio["cash_balance"],
            }

        except Exception:
            self.db.rollback()
            raise

        finally:
            cursor.close()

    # Holoding Create / Buy Method

    def add_holding(self, holding):
        """
        Expected holding data:

        {
            "portfolio_id": 1,
            "asset_id": 1,
            "ticker": "AAPL",
            "company_name": "Apple Inc.",
            "shares": 10,
            "purchase_price": 210.00,
            "purchase_date": "2026-07-31"
        }

        purchase_price is the price paid for this purchase.

        For a new ticker, purchase_price becomes cost_basis.

        If the ticker already exists in the portfolio, the shares
        and average cost basis are updated.
        """

        required_fields = [
            "portfolio_id",
            "asset_id",
            "ticker",
            "company_name",
            "shares",
            "purchase_price",
            "purchase_date",
        ]

        missing_fields = [
            field
            for field in required_fields
            if field not in holding or holding[field] in (None, "")
        ]

        if missing_fields:
            raise ValueError(
                "Missing required fields: "
                + ", ".join(missing_fields)
            )

        try:
            shares_bought = Decimal(str(holding["shares"]))
            purchase_price = Decimal(
                str(holding["purchase_price"])
            )

        except (InvalidOperation, TypeError, ValueError) as exc:
            raise ValueError(
                "shares and purchase_price must be valid numbers."
            ) from exc

        if shares_bought <= 0:
            raise ValueError(
                "shares must be greater than zero."
            )

        if purchase_price < 0:
            raise ValueError(
                "purchase_price cannot be negative."
            )

        portfolio_id = holding["portfolio_id"]
        asset_id = holding["asset_id"]
        ticker = holding["ticker"].strip().upper()
        company_name = holding["company_name"].strip()
        purchase_date = holding["purchase_date"]

        cursor = self.db.cursor(dictionary=True)

        try:
            # Check whether the portfolio already owns this ticker.
            cursor.execute(
                """
                SELECT
                    holding_id,
                    shares,
                    cost_basis,
                    purchase_date
                FROM holdings
                WHERE portfolio_id = %s
                  AND ticker = %s
                FOR UPDATE;
                """,
                (
                    portfolio_id,
                    ticker,
                ),
            )

            existing_holding = cursor.fetchone()

            # Update the existing row when the ticker already exists.
            if existing_holding:
                old_shares = Decimal(
                    str(existing_holding["shares"])
                )

                old_cost_basis = Decimal(
                    str(existing_holding["cost_basis"])
                )

                new_total_shares = (
                    old_shares + shares_bought
                )

                # Weighted-average cost basis.
                # No Python round() or quantize() is used.
                new_average_cost = (
                    (old_shares * old_cost_basis)
                    + (shares_bought * purchase_price)
                ) / new_total_shares

                cursor.execute(
                    """
                    UPDATE holdings
                    SET
                        asset_id = %s,
                        company_name = %s,
                        shares = %s,
                        cost_basis = %s
                    WHERE holding_id = %s;
                    """,
                    (
                        asset_id,
                        company_name,
                        new_total_shares,
                        new_average_cost,
                        existing_holding["holding_id"],
                    ),
                )

                self.db.commit()

                return {
                    "action": "updated",
                    "holding_id": existing_holding["holding_id"],
                    "portfolio_id": portfolio_id,
                    "asset_id": asset_id,
                    "ticker": ticker,
                    "company_name": company_name,
                    "shares": float(new_total_shares),
                    "cost_basis": float(new_average_cost),
                    "purchase_date": str(
                        existing_holding["purchase_date"]
                    ),
                }

            # Insert a new row when the ticker does not exist.
            cursor.execute(
                """
                INSERT INTO holdings (
                    portfolio_id,
                    asset_id,
                    ticker,
                    company_name,
                    shares,
                    cost_basis,
                    purchase_date
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s);
                """,
                (
                    portfolio_id,
                    asset_id,
                    ticker,
                    company_name,
                    shares_bought,
                    purchase_price,
                    purchase_date,
                ),
            )

            self.db.commit()

            return {
                "action": "created",
                "holding_id": cursor.lastrowid,
                "portfolio_id": portfolio_id,
                "asset_id": asset_id,
                "ticker": ticker,
                "company_name": company_name,
                "shares": float(shares_bought),
                "cost_basis": float(purchase_price),
                "purchase_date": str(purchase_date),
            }

        except Exception:
            self.db.rollback()
            raise

        finally:
            cursor.close()

    # Asset Create Method

    def add_asset(self, asset_type):
        cursor = self.db.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO asset (asset_type)
                VALUES (%s);
                """,
                (asset_type,),
            )

            self.db.commit()

            return {
                "asset_id": cursor.lastrowid,
                "asset_type": asset_type,
            }

        except Exception:
            self.db.rollback()
            raise

        finally:
            cursor.close()

    # Portfolio Update Method

    def update_portfolio(self, portfolio):
        cursor = self.db.cursor()

        try:
            cursor.execute(
                """
                UPDATE portfolio
                SET
                    portfolio_name = %s,
                    cash_balance = %s
                WHERE portfolio_id = %s;
                """,
                (
                    portfolio["portfolio_name"],
                    portfolio["cash_balance"],
                    portfolio["portfolio_id"],
                ),
            )

            # created_at is intentionally not changed.
            self.db.commit()

            return cursor.rowcount > 0

        except Exception:
            self.db.rollback()
            raise

        finally:
            cursor.close()

    # Holding Update Method

    def update_holding(self, holding):
        """
        Directly edit an existing holding.

        Use add_holding() when buying more shares so that the
        average cost basis is calculated automatically.
        """
        cursor = self.db.cursor()

        try:
            cursor.execute(
                """
                UPDATE holdings
                SET
                    portfolio_id = %s,
                    asset_id = %s,
                    ticker = %s,
                    company_name = %s,
                    shares = %s,
                    cost_basis = %s,
                    purchase_date = %s
                WHERE holding_id = %s;
                """,
                (
                    holding["portfolio_id"],
                    holding["asset_id"],
                    holding["ticker"].strip().upper(),
                    holding["company_name"],
                    holding["shares"],
                    holding["cost_basis"],
                    holding["purchase_date"],
                    holding["holding_id"],
                ),
            )

            self.db.commit()

            return cursor.rowcount > 0

        except Exception:
            self.db.rollback()
            raise

        finally:
            cursor.close()

    # Delete Methods

    def delete_portfolio_by_id(self, portfolio_id):
        cursor = self.db.cursor()

        try:
            cursor.execute(
                """
                DELETE FROM portfolio
                WHERE portfolio_id = %s;
                """,
                (portfolio_id,),
            )

            self.db.commit()

            return cursor.rowcount > 0

        except Exception:
            self.db.rollback()
            raise

        finally:
            cursor.close()

    def delete_holding_by_id(self, holding_id):
        cursor = self.db.cursor()

        try:
            cursor.execute(
                """
                DELETE FROM holdings
                WHERE holding_id = %s;
                """,
                (holding_id,),
            )

            self.db.commit()

            return cursor.rowcount > 0

        except Exception:
            self.db.rollback()
            raise

        finally:
            cursor.close()

    def delete_asset_by_id(self, asset_id):
        cursor = self.db.cursor()

        try:
            cursor.execute(
                """
                DELETE FROM asset
                WHERE asset_id = %s;
                """,
                (asset_id,),
            )

            self.db.commit()

            return cursor.rowcount > 0

        except Exception:
            self.db.rollback()
            raise

        finally:
            cursor.close()

    def get_portfolio_summary(self, portfolio_id):
        db = get_db_connection()
        cursor = db.cursor(dictionary=True, buffered=True)
        try:
            cursor.execute(
                "SELECT cash_balance FROM portfolio WHERE portfolio_id = %s;",
                (portfolio_id,),
            )
            portfolio = cursor.fetchone()
            if not portfolio:
                return None

            cash_balance = float(portfolio["cash_balance"] or 0)
            cursor.execute(
                "SELECT h.shares, h.cost_basis, h.ticker, a.asset_type "
                "FROM holdings h "
                "JOIN asset a ON h.asset_id = a.asset_id "
                "WHERE h.portfolio_id = %s;",
                (portfolio_id,),
            )
            holdings = cursor.fetchall()

            totals = {
                "Stocks": 0.0,
                "Bonds": 0.0,
                "Crypto": 0.0,
                "Cash": cash_balance,
            }
            total_holdings_value = 0.0
            total_return = 0.0
            total_cost_basis = 0.0

            for holding in holdings:
                shares = float(holding["shares"] or 0)
                cost_basis = float(holding["cost_basis"] or 0)
                asset_type = holding["asset_type"] or "Stock"
                ticker = holding["ticker"]

                current_price = 0.0
                market_value = 0.0
                profit_loss = 0.0
                if ticker:
                    info = get_info(ticker)
                    current_price = float(
                        info.get("currentPrice")
                        or info.get("regularMarketPrice")
                        or 0
                    )
                    market_value = shares * current_price
                    profit_loss = market_value - (shares * cost_basis)

                label = (
                    "Stocks" if asset_type == "Stock" else
                    "Bonds" if asset_type == "Bond" else
                    "Crypto" if asset_type == "Crypto" else
                    "Cash"
                )

                totals[label] = totals.get(label, 0.0) + market_value
                total_holdings_value += market_value
                total_return += profit_loss
                total_cost_basis += cost_basis * shares

            return {
                "cash_balance": cash_balance,
                "total_value": total_holdings_value + cash_balance,
                "total_return": total_return,
                "cost_basis_total": total_cost_basis,
                "stocks_value": totals["Stocks"],
                "bonds_value": totals["Bonds"],
                "crypto_value": totals["Crypto"],
            }
        finally:
            cursor.close()
            db.close()