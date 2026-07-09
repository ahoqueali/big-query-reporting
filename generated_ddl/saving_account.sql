CREATE TABLE IF NOT EXISTS `your_gcp_project.core.saving_account` (
  saving_account_id STRING NOT NULL OPTIONS(description="Primary key"),
  customer_id STRING NOT NULL OPTIONS(description="Foreign key to customer.customer_id"),
  balance NUMERIC NOT NULL OPTIONS(description="Current account balance"),
  currency STRING NOT NULL OPTIONS(description="ISO 4217 currency code, e.g. USD"),
  interest_rate NUMERIC NOT NULL OPTIONS(description="Annual interest rate as decimal, e.g. 0.035 for 3.5%"),
  minimum_balance NUMERIC OPTIONS(description="Minimum balance required to avoid fees"),
  opened_date DATE NOT NULL OPTIONS(description="Date the account was opened"),
  status STRING OPTIONS(description="e.g. active, closed, frozen")
)
PARTITION BY opened_date
CLUSTER BY customer_id, interest_rate
OPTIONS(
  description="One row per savings account held by a customer"
);
