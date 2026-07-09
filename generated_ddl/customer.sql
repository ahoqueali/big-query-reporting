CREATE TABLE IF NOT EXISTS `your_gcp_project.core.customer` (
  customer_id STRING NOT NULL OPTIONS(description="Primary key"),
  signup_date DATE NOT NULL OPTIONS(description="Date the customer signed up"),
  region STRING OPTIONS(description="Sales region code"),
  lifetime_value NUMERIC OPTIONS(description="Cumulative revenue from this customer"),
  is_active BOOL OPTIONS(description="Whether the customer has an active subscription")
)
PARTITION BY signup_date
CLUSTER BY region, customer_id
OPTIONS(
  description="One row per customer"
);
