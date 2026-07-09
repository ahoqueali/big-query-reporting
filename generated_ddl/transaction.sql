CREATE TABLE IF NOT EXISTS `your_gcp_project.core.transaction` (
  transaction_id STRING NOT NULL OPTIONS(description="Primary key"),
  account_id STRING NOT NULL OPTIONS(description="Foreign key to saving_account.saving_account_id or current_account.current_account_id"),
  transaction_type STRING NOT NULL OPTIONS(description="e.g. deposit, withdrawal, transfer, fee, interest"),
  amount NUMERIC NOT NULL OPTIONS(description="Transaction amount (positive for credit, negative for debit)"),
  currency STRING NOT NULL OPTIONS(description="ISO 4217 currency code, e.g. USD"),
  balance_before NUMERIC NOT NULL OPTIONS(description="Account balance immediately before this transaction"),
  balance_after NUMERIC NOT NULL OPTIONS(description="Account balance immediately after this transaction"),
  description STRING OPTIONS(description="Human-readable transaction description"),
  transaction_date DATE NOT NULL OPTIONS(description="Date the transaction posted"),
  status STRING NOT NULL OPTIONS(description="e.g. posted, pending, cancelled")
)
PARTITION BY transaction_date
CLUSTER BY account_id, transaction_type
OPTIONS(
  description="One row per financial transaction against an account"
);
