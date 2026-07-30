#Database Schema Explaination 

##Portfolio Table

Stores portfolio info

Columns:
- portfolio_id (Primary Key)
- portfolio_name
- created_at

##Asset Table

Stores asset categories used for allocation

Columns:
- asset_id (Primary Key)
- asset_type

##Holdings Table

Stores assets owned within a portfolio

Columns:
- holding_id (Primary Key)
- portfolio_id (Foreign Key)
- asset_id (Foreign Key)
- ticker
- company_name
- shares
- current_price
- cost_basis
- market_value
- profit_loss
