CREATE TABLE IF NOT EXISTS `your_gcp_project.core.mortgage_account` (
  mortgage_account_id STRING NOT NULL OPTIONS(description="Primary key"),
  customer_id STRING NOT NULL OPTIONS(description="Foreign key to customer.customer_id"),
  property_address STRING NOT NULL OPTIONS(description="Physical address of the mortgaged property"),
  property_value NUMERIC NOT NULL OPTIONS(description="Appraised value of the property at origination"),
  loan_amount NUMERIC NOT NULL OPTIONS(description="Original principal loan amount"),
  outstanding_balance NUMERIC NOT NULL OPTIONS(description="Remaining principal balance"),
  currency STRING NOT NULL OPTIONS(description="ISO 4217 currency code, e.g. USD"),
  interest_rate NUMERIC NOT NULL OPTIONS(description="Annual interest rate as decimal, e.g. 0.065 for 6.5%"),
  interest_rate_type STRING NOT NULL OPTIONS(description="e.g. fixed, variable"),
  loan_term_months INT64 NOT NULL OPTIONS(description="Loan term in months, e.g. 360 for 30-year"),
  monthly_payment NUMERIC NOT NULL OPTIONS(description="Scheduled monthly payment amount"),
  origination_date DATE NOT NULL OPTIONS(description="Date the mortgage was originated"),
  maturity_date DATE NOT NULL OPTIONS(description="Date the loan is scheduled to be fully paid"),
  status STRING NOT NULL OPTIONS(description="e.g. active, paid_off, defaulted, foreclosed")
)
PARTITION BY origination_date
CLUSTER BY customer_id, status
OPTIONS(
  description="One row per mortgage loan account held by a customer"
);
