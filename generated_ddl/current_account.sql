CREATE TABLE IF NOT EXISTS `your_gcp_project.core.current_account` (
  current_account_id STRING NOT NULL OPTIONS(description="Primary key"),
  customer_id STRING NOT NULL OPTIONS(description="Foreign key to customer.customer_id"),
  balance NUMERIC NOT NULL OPTIONS(description="Current account balance"),
  currency STRING NOT NULL OPTIONS(description="ISO 4217 currency code, e.g. USD"),
  overdraft_limit NUMERIC OPTIONS(description="Maximum overdraft amount allowed"),
  overdraft_interest_rate NUMERIC OPTIONS(description="Annual interest rate on overdrawn balances"),
  has_debit_card BOOL OPTIONS(description="Whether a debit card is linked to this account"),
  opened_date DATE NOT NULL OPTIONS(description="Date the account was opened"),
  status STRING OPTIONS(description="e.g. active, closed, frozen")
)
PARTITION BY opened_date
CLUSTER BY customer_id, overdraft_limit
OPTIONS(
  description="One row per current (checking) account held by a customer"
);
