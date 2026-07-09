# BigQuery Ontology / Semantic / Data Model Stack

A minimal, working example of three linked modeling layers, all defined in YAML:

```
ontology/           <- conceptual layer: entities, properties, relationships
semantic_models/     <- business layer: dimensions, measures, metrics (dbt/MetricFlow style)
data_model/           <- physical layer: BigQuery table schemas
scripts/
  generate_ddl.py     <- data_model/*.yaml -> generated_ddl/*.sql (BigQuery DDL)
  validate_mapping.py <- checks ontology -> semantic -> data_model references are consistent
generated_ddl/        <- output of generate_ddl.py (gitignore-able, regenerated on demand)
```

## Why three layers

- **data_model/**: what actually exists in BigQuery (tables, columns, types, partitioning).
- **semantic_models/**: what analysts/BI tools query (metrics like `total_ltv`, dimensions like `region`),
  decoupled from physical column names so the physical model can evolve independently.
- **ontology/**: what the business actually means by "Customer", "SavingAccount", etc. — entities
  and relationships that are true regardless of which database or semantic tool you use. This is the
  layer that stays stable even if you migrate off BigQuery or dbt entirely.

## Files by layer

| Entity | Ontology | Semantic Model | Data Model | DDL |
|---|---|---|---|---|
| Customer | `ontology/customer.yaml` | `semantic_models/customer.yml` | `data_model/customer.yaml` | `generated_ddl/customer.sql` |
| SavingAccount | `ontology/saving_account.yaml` | `semantic_models/saving_account.yml` | `data_model/saving_account.yaml` | `generated_ddl/saving_account.sql` |
| CurrentAccount | `ontology/current_account.yaml` | `semantic_models/current_account.yml` | `data_model/current_account.yaml` | `generated_ddl/current_account.sql` |
| MortgageAccount | `ontology/mortgage_account.yaml` | `semantic_models/mortgage_account.yml` | `data_model/mortgage_account.yaml` | `generated_ddl/mortgage_account.sql` |
| Transaction | `ontology/transaction.yaml` | `semantic_models/transaction.yml` | `data_model/transaction.yaml` | `generated_ddl/transaction.sql` |

Dependency direction: **ontology → semantic_models → data_model**. Each ontology entity's
`maps_to` block points at a semantic model; each semantic model's `model: ref(...)` points at a
data_model table.

## Entities

| Entity | Table | Description |
|---|---|---|
| Customer | `customer` | A party who has signed up and may hold Accounts and Mortgages |
| SavingAccount | `saving_account` | A deposit account that earns interest |
| CurrentAccount | `current_account` | A transactional account for everyday spending |
| MortgageAccount | `mortgage_account` | A secured loan used to finance a real estate purchase |
| Transaction | `transaction` | A financial event that debits or credits an Account balance |

## Usage

```bash
pip install pyyaml --break-system-packages

# 1. Generate BigQuery DDL from the data model YAML
python scripts/generate_ddl.py
cat generated_ddl/customer.sql

# 2. (optional) Actually deploy to BigQuery — requires `bq` CLI configured
python scripts/generate_ddl.py --apply

# 3. Validate that ontology / semantic / data model layers are consistent
python scripts/validate_mapping.py
```

Run `validate_mapping.py` in CI on every PR that touches `data_model/`, `semantic_models/`, or
`ontology/` — it catches broken references (e.g. an ontology mapping to a measure that was
renamed or removed) before they hit production.

## Extending this

- **More tables**: add a YAML file to `data_model/`, a matching block to `semantic_models/`, and
  an entity to `ontology/` with a `maps_to` pointing at it.
- **Real ontology rigor**: if you need formal inference/reasoning or interoperability with other
  systems, treat `ontology/*.yaml` as a lightweight bridge and maintain the canonical ontology in
  OWL/RDF (e.g. via Protégé), regenerating the YAML bridge from it.
- **Semantic layer engine**: this example mirrors dbt's MetricFlow YAML syntax. It also translates
  directly to Cube's schema format or to Malloy source/view definitions if you'd rather compile
  straight to BigQuery SQL without dbt.
- **Drift detection against live BigQuery**: extend `validate_mapping.py` to also query
  `INFORMATION_SCHEMA.COLUMNS` and diff against `data_model/*.yaml`, so you catch cases where
  someone manually altered a table outside of this pipeline.
