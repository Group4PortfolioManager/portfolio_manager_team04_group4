from decimal import Decimal, InvalidOperation

from app.database import get_db_connection
from app.services.yahoo_service import get_info


class DataBaseService:
    def get_all_portfolios(self):
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT *
                FROM portfolio
                ORDER BY portfolio_id;
                """
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            db.close()

    def get_portfolio_by_id(self, portfolio_id):
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT *
                FROM portfolio
                WHERE portfolio_id = %s;
                """,
                (portfolio_id,),
            )

            return cursor.fetchone()

        finally:
            cursor.close()
            db.close()

    def get_portfolio_holdings(self, portfolio_id):
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

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
            db.close()

    def get_holding_by_id(self, holding_id):
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

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

            return cursor.fetchone()

        finally:
            cursor.close()
            db.close()

    def get_holding_by_ticker(self, portfolio_id, ticker):
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

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
            db.close()

    def get_all_assets(self):
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT *
                FROM asset
                ORDER BY asset_id;
                """
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            db.close()

    def get_asset_by_id(self, asset_id):
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT *
                FROM asset
                WHERE asset_id = %s;
                """,
                (asset_id,),
            )

            return cursor.fetchone()

        finally:
            cursor.close()
            db.close()

    def add_portfolio(self, portfolio):
        db = get_db_connection()
        cursor = db.cursor()

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

            db.commit()

            return {
                "portfolio_id": cursor.lastrowid,
                "portfolio_name": portfolio["portfolio_name"],
                "cash_balance": float(
                    portfolio["cash_balance"]
                ),
            }

        except Exception:
            db.rollback()
            raise

        finally:
            cursor.close()
            db.close()

    def add_holding(self, holding):
        """
        Add a new holding or buy more shares of an existing ticker.

        The incoming cost_basis is the price paid per share for the
        new purchase. When the ticker already exists, cost_basis is
        recalculated as a weighted average.
        """

        required_fields = [
            "portfolio_id",
            "asset_id",
            "ticker",
            "company_name",
            "shares",
            "cost_basis",
            "purchase_date",
        ]

        missing_fields = [
            field
            for field in required_fields
            if field not in holding
            or holding[field] in (None, "")
        ]

        if missing_fields:
            raise ValueError(
                "Missing required fields: "
                + ", ".join(missing_fields)
            )

        try:
            shares_bought = Decimal(
                str(holding["shares"])
            )

            cost_basis = Decimal(
                str(holding["cost_basis"])
            )

        except (
            InvalidOperation,
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "shares and cost_basis must be valid numbers."
            ) from exc

        if shares_bought <= 0:
            raise ValueError(
                "shares must be greater than zero."
            )

        if cost_basis < 0:
            raise ValueError(
                "cost_basis cannot be negative."
            )

        portfolio_id = holding["portfolio_id"]
        asset_id = holding["asset_id"]
        ticker = holding["ticker"].strip().upper()
        company_name = holding["company_name"].strip()
        purchase_date = holding["purchase_date"]

        purchase_total = shares_bought * cost_basis

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT
                    portfolio_id,
                    cash_balance
                FROM portfolio
                WHERE portfolio_id = %s
                FOR UPDATE;
                """,
                (portfolio_id,),
            )

            portfolio = cursor.fetchone()

            if portfolio is None:
                raise ValueError(
                    "Portfolio not found."
                )

            cash_balance = Decimal(
                str(portfolio["cash_balance"] or 0)
            )

            if purchase_total > cash_balance:
                raise ValueError(
                    "Insufficient cash balance."
                )

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

                new_average_cost = (
                    (old_shares * old_cost_basis)
                    + (shares_bought * cost_basis)
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

                action = "updated"
                holding_id = existing_holding["holding_id"]
                final_shares = new_total_shares
                final_cost_basis = new_average_cost
                final_purchase_date = existing_holding[
                    "purchase_date"
                ]

            else:
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
                        cost_basis,
                        purchase_date,
                    ),
                )

                action = "created"
                holding_id = cursor.lastrowid
                final_shares = shares_bought
                final_cost_basis = cost_basis
                final_purchase_date = purchase_date

            cursor.execute(
                """
                UPDATE portfolio
                SET cash_balance = cash_balance - %s
                WHERE portfolio_id = %s;
                """,
                (
                    purchase_total,
                    portfolio_id,
                ),
            )

            if cursor.rowcount == 0:
                raise ValueError(
                    "Portfolio not found."
                )

            db.commit()

            return {
                "action": action,
                "holding_id": holding_id,
                "portfolio_id": portfolio_id,
                "asset_id": asset_id,
                "ticker": ticker,
                "company_name": company_name,
                "shares": float(final_shares),
                "cost_basis": float(final_cost_basis),
                "purchase_date": str(
                    final_purchase_date
                ),
                "purchase_total": float(
                    purchase_total
                ),
                "cash_remaining": float(
                    cash_balance - purchase_total
                ),
            }

        except Exception:
            db.rollback()
            raise

        finally:
            cursor.close()
            db.close()

    def remove_shares(
        self,
        portfolio_id,
        ticker,
        shares_to_remove,
        sale_price,
    ):
        try:
            shares_to_remove = Decimal(
                str(shares_to_remove)
            )

            sale_price = Decimal(
                str(sale_price)
            )

        except (
            InvalidOperation,
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "Shares to remove and sale price "
                "must be valid numbers."
            ) from exc

        if shares_to_remove <= 0:
            raise ValueError(
                "Shares to remove must be greater than zero."
            )

        if sale_price < 0:
            raise ValueError(
                "Sale price cannot be negative."
            )

        ticker = ticker.strip().upper()

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT
                    holding_id,
                    shares,
                    cost_basis
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

            holding = cursor.fetchone()

            if holding is None:
                raise ValueError(
                    f"{ticker} is not currently "
                    "in this portfolio."
                )

            current_shares = Decimal(
                str(holding["shares"])
            )

            if shares_to_remove > current_shares:
                raise ValueError(
                    "Cannot remove more shares "
                    "than are currently owned."
                )

            remaining_shares = (
                current_shares - shares_to_remove
            )

            sale_total = (
                shares_to_remove * sale_price
            )

            if remaining_shares == 0:
                cursor.execute(
                    """
                    DELETE FROM holdings
                    WHERE holding_id = %s;
                    """,
                    (holding["holding_id"],),
                )

                action = "deleted"

            else:
                cursor.execute(
                    """
                    UPDATE holdings
                    SET shares = %s
                    WHERE holding_id = %s;
                    """,
                    (
                        remaining_shares,
                        holding["holding_id"],
                    ),
                )

                action = "updated"

            cursor.execute(
                """
                UPDATE portfolio
                SET cash_balance = cash_balance + %s
                WHERE portfolio_id = %s;
                """,
                (
                    sale_total,
                    portfolio_id,
                ),
            )

            if cursor.rowcount == 0:
                raise ValueError(
                    "Portfolio not found."
                )

            db.commit()

            return {
                "action": action,
                "ticker": ticker,
                "shares_removed": float(
                    shares_to_remove
                ),
                "remaining_shares": float(
                    remaining_shares
                ),
                "sale_price": float(sale_price),
                "sale_total": float(sale_total),
                "cost_basis": float(
                    holding["cost_basis"]
                ),
            }

        except Exception:
            db.rollback()
            raise

        finally:
            cursor.close()
            db.close()

    def add_asset(self, asset_type):
        db = get_db_connection()
        cursor = db.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO asset (asset_type)
                VALUES (%s);
                """,
                (asset_type,),
            )

            db.commit()

            return {
                "asset_id": cursor.lastrowid,
                "asset_type": asset_type,
            }

        except Exception:
            db.rollback()
            raise

        finally:
            cursor.close()
            db.close()

    def update_portfolio(self, portfolio):
        db = get_db_connection()
        cursor = db.cursor()

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

            db.commit()

            return cursor.rowcount > 0

        except Exception:
            db.rollback()
            raise

        finally:
            cursor.close()
            db.close()

    def update_holding(self, holding):
        db = get_db_connection()
        cursor = db.cursor()

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
                    holding["company_name"].strip(),
                    holding["shares"],
                    holding["cost_basis"],
                    holding["purchase_date"],
                    holding["holding_id"],
                ),
            )

            db.commit()

            return cursor.rowcount > 0

        except Exception:
            db.rollback()
            raise

        finally:
            cursor.close()
            db.close()

    def delete_portfolio_by_id(self, portfolio_id):
        db = get_db_connection()
        cursor = db.cursor()

        try:
            cursor.execute(
                """
                DELETE FROM portfolio
                WHERE portfolio_id = %s;
                """,
                (portfolio_id,),
            )

            db.commit()

            return cursor.rowcount > 0

        except Exception:
            db.rollback()
            raise

        finally:
            cursor.close()
            db.close()

    def delete_holding_by_id(self, holding_id):
        db = get_db_connection()
        cursor = db.cursor()

        try:
            cursor.execute(
                """
                DELETE FROM holdings
                WHERE holding_id = %s;
                """,
                (holding_id,),
            )

            db.commit()

            return cursor.rowcount > 0

        except Exception:
            db.rollback()
            raise

        finally:
            cursor.close()
            db.close()

    def delete_asset_by_id(self, asset_id):
        db = get_db_connection()
        cursor = db.cursor()

        try:
            cursor.execute(
                """
                DELETE FROM asset
                WHERE asset_id = %s;
                """,
                (asset_id,),
            )

            db.commit()

            return cursor.rowcount > 0

        except Exception:
            db.rollback()
            raise

        finally:
            cursor.close()
            db.close()

    def get_portfolio_summary(self, portfolio_id):
        """
        Build the live dashboard summary using stored holdings and
        Yahoo Finance prices.

        The database supplies ticker, shares, cost basis and asset
        type. Yahoo Finance supplies current price and previous close.
        """

        db = get_db_connection()
        cursor = db.cursor(
            dictionary=True,
            buffered=True,
        )

        try:
            cursor.execute(
                """
                SELECT cash_balance
                FROM portfolio
                WHERE portfolio_id = %s;
                """,
                (portfolio_id,),
            )

            portfolio = cursor.fetchone()

            if portfolio is None:
                return None

            cursor.execute(
                """
                SELECT
                    h.ticker,
                    h.shares,
                    h.cost_basis,
                    a.asset_type
                FROM holdings AS h
                INNER JOIN asset AS a
                    ON h.asset_id = a.asset_id
                WHERE h.portfolio_id = %s;
                """,
                (portfolio_id,),
            )

            holdings = cursor.fetchall()

        finally:
            cursor.close()
            db.close()

        cash_balance = Decimal(
            str(portfolio["cash_balance"] or 0)
        )

        stocks_value = Decimal("0.00")
        bonds_value = Decimal("0.00")
        crypto_value = Decimal("0.00")

        total_cost_basis = Decimal("0.00")
        total_return = Decimal("0.00")
        day_gain = Decimal("0.00")
        previous_holdings_value = Decimal("0.00")

        for holding in holdings:
            ticker = holding["ticker"]

            shares = Decimal(
                str(holding["shares"] or 0)
            )

            cost_basis = Decimal(
                str(holding["cost_basis"] or 0)
            )

            asset_type = (
                holding["asset_type"] or "Stock"
            )

            try:
                info = get_info(ticker) or {}

            except Exception as error:
                print(
                    f"Yahoo lookup failed for "
                    f"{ticker}: {error}"
                )
                info = {}

            current_price_value = (
                info.get("currentPrice")
                or info.get("regularMarketPrice")
                or info.get("navPrice")
                or 0
            )

            previous_close_value = (
                info.get("previousClose")
                or info.get(
                    "regularMarketPreviousClose"
                )
                or current_price_value
                or 0
            )

            current_price = Decimal(
                str(current_price_value)
            )

            previous_close = Decimal(
                str(previous_close_value)
            )

            market_value = shares * current_price
            holding_cost = shares * cost_basis

            profit_loss = (
                market_value - holding_cost
            )

            holding_day_gain = (
                current_price - previous_close
            ) * shares

            previous_market_value = (
                previous_close * shares
            )

            if asset_type == "Stock":
                stocks_value += market_value

            elif asset_type == "Bond":
                bonds_value += market_value

            elif asset_type == "Crypto":
                crypto_value += market_value

            total_cost_basis += holding_cost
            total_return += profit_loss
            day_gain += holding_day_gain
            previous_holdings_value += (
                previous_market_value
            )

        total_value = (
            stocks_value
            + bonds_value
            + crypto_value
            + cash_balance
        )

        total_return_percent = Decimal("0.00")

        if total_cost_basis > 0:
            total_return_percent = (
                total_return / total_cost_basis
            ) * Decimal("100")

        day_gain_percent = Decimal("0.00")

        if previous_holdings_value > 0:
            day_gain_percent = (
                day_gain / previous_holdings_value
            ) * Decimal("100")

        return {
            "cash_balance": float(cash_balance),
            "stocks_value": float(stocks_value),
            "bonds_value": float(bonds_value),
            "crypto_value": float(crypto_value),
            "total_value": float(total_value),
            "total_return": float(total_return),
            "total_return_percent": float(
                total_return_percent
            ),
            "day_gain": float(day_gain),
            "day_gain_percent": float(
                day_gain_percent
            ),
            "cost_basis_total": float(
                total_cost_basis
            ),
        }