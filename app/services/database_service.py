from app.database import get_db_connection

class DataBaseService:
    def get_all_portfolios(self):
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM portfolio;")
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()

    def get_portfolio_by_id(self, portfolio_id):
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM portfolio WHERE portfolio_id = %s;", (portfolio_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
            db.close()

    def get_portfolio_holdings(self, portfolio_id):
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM holdings WHERE portfolio_id = %s;", (portfolio_id,))
            holdings = cursor.fetchall()
            print(f"Holdings for portfolio {portfolio_id}: {holdings}")
            return self._aggregate_holdings_by_ticker(holdings)
        finally:
            cursor.close()
            db.close()

    #sym:_aggregate_holdings_by_ticker
    def _aggregate_holdings_by_ticker(self, holdings):
        grouped = {}
        for holding in holdings:
            ticker = holding["ticker"]
            shares = float(holding["shares"] or 0)
            current_price = float(holding["current_price"] or 0)
            cost_basis = float(holding["cost_basis"] or 0)
            market_value = float(holding["market_value"] or 0)
            profit_loss = float(holding["profit_loss"] or 0)

            if ticker not in grouped:
                grouped[ticker] = {
                    "holding_id": holding.get("holding_id"),
                    "portfolio_id": holding["portfolio_id"],
                    "asset_id": holding["asset_id"],
                    "ticker": ticker,
                    "company_name": holding["company_name"],
                    "shares": shares,
                    "market_value": market_value,
                    "profit_loss": profit_loss,
                    "_weighted_current_price": current_price * shares,
                    "_weighted_cost_basis": cost_basis * shares,
                }
            else:
                grouped[ticker]["shares"] += shares
                grouped[ticker]["market_value"] += market_value
                grouped[ticker]["profit_loss"] += profit_loss
                grouped[ticker]["_weighted_current_price"] += current_price * shares
                grouped[ticker]["_weighted_cost_basis"] += cost_basis * shares

        result = []
        for aggregated in grouped.values():
            total_shares = aggregated["shares"]
            aggregated["current_price"] = (
                aggregated["_weighted_current_price"] / total_shares
            ) if total_shares else 0.0
            aggregated["cost_basis"] = (
                aggregated["_weighted_cost_basis"] / total_shares
            ) if total_shares else 0.0
            aggregated.pop("_weighted_current_price", None)
            aggregated.pop("_weighted_cost_basis", None)
            result.append(aggregated)

        return result

    def get_holding_by_id(self, holding_id):
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM holdings WHERE holding_id = %s;", (holding_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
            db.close()

    def get_all_assets(self):
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM asset;")
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()

    def get_asset_by_id(self, asset_id):
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM asset WHERE asset_id = %s;", (asset_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
            db.close()

    def buy_holding(self, portfolio_id, ticker, shares, price):
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT asset_id FROM asset WHERE asset_type = %s LIMIT 1;", ("Stock",))
            asset_row = cursor.fetchone()
            if asset_row:
                asset_id = asset_row["asset_id"]
            else:
                cursor.execute("INSERT INTO asset (asset_type) VALUES (%s);", ("Stock",))
                asset_id = cursor.lastrowid

            cursor.execute(
                "SELECT * FROM holdings WHERE portfolio_id = %s AND ticker = %s LIMIT 1;",
                (portfolio_id, ticker)
            )
            existing = cursor.fetchone()

            if existing:
                total_shares = float(existing["shares"] or 0) + float(shares)
                total_cost_basis = (float(existing["cost_basis"] or 0) * float(existing["shares"] or 0)) + (float(price) * float(shares))
                new_cost_basis = total_cost_basis / total_shares if total_shares else 0
                new_market_value = total_shares * float(price)
                new_profit_loss = new_market_value - (new_cost_basis * total_shares)

                cursor.execute(
                    "UPDATE holdings SET shares = %s, current_price = %s, cost_basis = %s, market_value = %s, profit_loss = %s WHERE holding_id = %s;",
                    (total_shares, price, new_cost_basis, new_market_value, new_profit_loss, existing["holding_id"])
                )
                db.commit()
                return {
                    "holding_id": existing["holding_id"],
                    "portfolio_id": portfolio_id,
                    "asset_id": asset_id,
                    "ticker": ticker,
                    "company_name": existing["company_name"],
                    "shares": total_shares,
                    "current_price": float(price),
                    "cost_basis": new_cost_basis,
                    "market_value": new_market_value,
                    "profit_loss": new_profit_loss,
                }

            market_value = float(shares) * float(price)
            cursor.execute(
                "INSERT INTO holdings (portfolio_id, asset_id, ticker, company_name, shares, current_price, market_value, cost_basis, profit_loss) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);",
                (portfolio_id, asset_id, ticker, ticker, shares, price, market_value, price, 0.0)
            )
            holding_id = cursor.lastrowid
            db.commit()
            return {
                "holding_id": holding_id,
                "portfolio_id": portfolio_id,
                "asset_id": asset_id,
                "ticker": ticker,
                "company_name": ticker,
                "shares": float(shares),
                "current_price": float(price),
                "cost_basis": float(price),
                "market_value": market_value,
                "profit_loss": 0.0,
            }
        finally:
            cursor.close()
            db.close()

    def sell_holding(self, portfolio_id, ticker, shares, price):
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT * FROM holdings WHERE portfolio_id = %s AND ticker = %s LIMIT 1;",
                (portfolio_id, ticker)
            )
            existing = cursor.fetchone()
            if not existing:
                return {"error": "Holding not found"}

            current_shares = float(existing["shares"] or 0)
            sell_shares = float(shares)
            if sell_shares <= 0 or sell_shares > current_shares:
                return {"error": "Invalid sell quantity"}

            remaining_shares = current_shares - sell_shares
            if remaining_shares == 0:
                cursor.execute(
                    "DELETE FROM holdings WHERE holding_id = %s;",
                    (existing["holding_id"],)
                )
                db.commit()
                return {"message": "Holding sold completely", "holding_id": existing["holding_id"]}

            remaining_market = remaining_shares * float(price)
            remaining_cost_basis = float(existing["cost_basis"] or 0)
            remaining_profit_loss = remaining_market - (remaining_cost_basis * remaining_shares)

            cursor.execute(
                "UPDATE holdings SET shares = %s, current_price = %s, market_value = %s, profit_loss = %s WHERE holding_id = %s;",
                (remaining_shares, price, remaining_market, remaining_profit_loss, existing["holding_id"])
            )
            db.commit()
            return {
                "holding_id": existing["holding_id"],
                "portfolio_id": portfolio_id,
                "asset_id": existing["asset_id"],
                "ticker": ticker,
                "company_name": existing["company_name"],
                "shares": remaining_shares,
                "current_price": float(price),
                "cost_basis": remaining_cost_basis,
                "market_value": remaining_market,
                "profit_loss": remaining_profit_loss,
            }
        finally:
            cursor.close()
            db.close()
