from decimal import Decimal, InvalidOperation

from app.database import get_db_connection


class DataBaseService:
    def __init__(self):
        self._db = None

    @property
    def db(self):
        if self._db is None or not self._db.is_connected():
            self._db = get_db_connection()

        return self._db

    def get_all_portfolios(self):
        cursor = self.db.cursor(dictionary=True)

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

            return cursor.fetchone()

        finally:
            cursor.close()

    def get_portfolio_holdings(self, portfolio_id):
        cursor = self.db.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT
                    holding_id,
                    portfolio_id,
                    asset_id,
                    ticker,
                    company_name,
                    shares,
                    cost_basis,
                    purchase_date
                FROM holdings
                WHERE portfolio_id = %s
                ORDER BY ticker;
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
                    holding_id,
                    portfolio_id,
                    asset_id,
                    ticker,
                    company_name,
                    shares,
                    cost_basis,
                    purchase_date
                FROM holdings
                WHERE holding_id = %s;
                """,
                (holding_id,),
            )

            return cursor.fetchone()

        finally:
            cursor.close()

    def get_holding_by_ticker(self, portfolio_id, ticker):
        cursor = self.db.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT
                    holding_id,
                    portfolio_id,
                    asset_id,
                    ticker,
                    company_name,
                    shares,
                    cost_basis,
                    purchase_date
                FROM holdings
                WHERE portfolio_id = %s
                  AND ticker = %s;
                """,
                (
                    portfolio_id,
                    ticker.strip().upper(),
                ),
            )

            return cursor.fetchone()

        finally:
            cursor.close()

    def get_all_assets(self):
        cursor = self.db.cursor(dictionary=True)

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

            return cursor.fetchone()

        finally:
            cursor.close()

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
                "cash_balance": float(portfolio["cash_balance"]),
            }

        except Exception:
            self.db.rollback()
            raise

        finally:
            cursor.close()

    def add_holding(self, holding):
        """
        Adds a new holding or adds shares to an existing ticker.

        The incoming cost_basis represents the price paid per share
        for the new purchase.

        If the ticker already exists, the stored cost_basis becomes
        the weighted-average cost basis.
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
            shares_bought = Decimal(str(holding["shares"]))
            cost_basis = Decimal(str(holding["cost_basis"]))

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

        cursor = self.db.cursor(dictionary=True)

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
                raise ValueError("Portfolio not found.")

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

            self.db.commit()

            return {
                "action": action,
                "holding_id": holding_id,
                "portfolio_id": portfolio_id,
                "asset_id": asset_id,
                "ticker": ticker,
                "company_name": company_name,
                "shares": float(final_shares),
                "cost_basis": float(final_cost_basis),
                "purchase_date": str(final_purchase_date),
                "purchase_total": float(purchase_total),
                "cash_remaining": float(
                    cash_balance - purchase_total
                ),
            }

        except Exception:
            self.db.rollback()
            raise

        finally:
            cursor.close()

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

            sale_price = Decimal(str(sale_price))

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
        cursor = self.db.cursor(dictionary=True)

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

            self.db.commit()

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
            self.db.rollback()
            raise

        finally:
            cursor.close()

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

            self.db.commit()

            return cursor.rowcount > 0

        except Exception:
            self.db.rollback()
            raise

        finally:
            cursor.close()

    def update_holding(self, holding):
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
                    holding["company_name"].strip(),
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
        """
        Returns only values that can be calculated from stored
        database data.

        These are cost-basis totals, not live market values.
        """

        cursor = self.db.cursor(dictionary=True)

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
                    asset_id,
                    shares,
                    cost_basis
                FROM holdings
                WHERE portfolio_id = %s;
                """,
                (portfolio_id,),
            )

            holdings = cursor.fetchall()

            cash_balance = Decimal(
                str(portfolio["cash_balance"] or 0)
            )

            stocks_cost_basis = Decimal("0.00")
            bonds_cost_basis = Decimal("0.00")
            crypto_cost_basis = Decimal("0.00")
            total_cost_basis = Decimal("0.00")

            for holding in holdings:
                shares = Decimal(
                    str(holding["shares"] or 0)
                )

                cost_basis = Decimal(
                    str(holding["cost_basis"] or 0)
                )

                holding_cost = shares * cost_basis
                asset_id = holding["asset_id"]

                if asset_id == 1:
                    stocks_cost_basis += holding_cost

                elif asset_id == 2:
                    bonds_cost_basis += holding_cost

                elif asset_id == 3:
                    crypto_cost_basis += holding_cost

                total_cost_basis += holding_cost

            return {
                "cash_balance": float(cash_balance),
                "cost_basis_total": float(
                    total_cost_basis
                ),
                "stocks_cost_basis": float(
                    stocks_cost_basis
                ),
                "bonds_cost_basis": float(
                    bonds_cost_basis
                ),
                "crypto_cost_basis": float(
                    crypto_cost_basis
                ),
            }

        finally:
            cursor.close()