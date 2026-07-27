/*Creating the portfolio tracker database*/
create database portfolio_tracker; 

/*Choosing the portfolio tracker database*/
use portfolio_tracker;

/*Creating the portfolio table*/
create table Portfolio (
    portfolio_id int auto_increment primary key,
    portfolio_name varchar(100) not null,
    cash_balance decimal(10, 2) default 0.00,
    created_at timestamp default current_timestamp
    );

/*Creating the asset table*/
create table Asset (
    asset_id int auto_increment primary key,
    asset_type enum('Stock', 'Bond', 'Crypto', 'Cash') not null
    );

/*Creating the holdings table*/
create table Holdings (
    holding_id int auto_increment primary key,
    portfolio_id int not null,
    asset_id int not null,
    ticker varchar(10) not null,
    company_name varchar(100) not null,
    shares decimal(10,4),
    current_price decimal(10, 2),
    market_value decimal(10, 2),
    cost_basis decimal(10, 2),
    profit_loss decimal(10, 2),
    
    /*Creating the portfolio_id foreign key*/
    foreign key (portfolio_id)
	references Portfolio(portfolio_id)
        on delete cascade,
        
	/*Creating the asset_id foreign key */
    foreign key (asset_id)
	references Asset(asset_id)
        on delete cascade
    );
