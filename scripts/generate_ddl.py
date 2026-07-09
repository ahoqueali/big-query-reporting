#!/usr/bin/env python3
"""
generate_ddl.py

Reads YAML table definitions from data_model/ and generates BigQuery
CREATE TABLE DDL statements into generated_ddl/.

Usage:
    python scripts/generate_ddl.py
    python scripts/generate_ddl.py --apply   # also runs `bq query` to deploy

Requires: pyyaml (pip install pyyaml --break-system-packages)
"""

import argparse
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Missing dependency. Run: pip install pyyaml --break-system-packages")

ROOT = Path(__file__).resolve().parent.parent
DATA_MODEL_DIR = ROOT / "data_model"
OUTPUT_DIR = ROOT / "generated_ddl"


def render_column(col: dict) -> str:
    name = col["name"]
    col_type = col["type"]
    mode = col.get("mode", "NULLABLE")
    line = f"  {name} {col_type}"
    if mode == "REQUIRED":
        line += " NOT NULL"
    description = col.get("description")
    if description:
        escaped = description.replace('"', '\\"')
        line += f' OPTIONS(description="{escaped}")'
    return line


def render_ddl(table_def: dict) -> str:
    project = table_def.get("project", "your_gcp_project")
    dataset = table_def["dataset"]
    table = table_def["table"]
    full_name = f"`{project}.{dataset}.{table}`"

    columns = ",\n".join(render_column(c) for c in table_def["columns"])

    ddl = f"CREATE TABLE IF NOT EXISTS {full_name} (\n{columns}\n)"

    partition = table_def.get("partition_by")
    if partition:
        ddl += f"\nPARTITION BY {partition['field']}"

    cluster = table_def.get("cluster_by")
    if cluster:
        ddl += f"\nCLUSTER BY {', '.join(cluster)}"

    description = table_def.get("description")
    options = []
    if description:
        escaped = description.replace('"', '\\"')
        options.append(f'description="{escaped}"')
    if options:
        options_joined = ",\n  ".join(options)
        ddl += f"\nOPTIONS(\n  {options_joined}\n)"

    ddl += ";\n"
    return ddl


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true",
                         help="Run the generated DDL against BigQuery via `bq query`")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(exist_ok=True)

    yaml_files = sorted(DATA_MODEL_DIR.glob("*.yaml")) + sorted(DATA_MODEL_DIR.glob("*.yml"))
    if not yaml_files:
        print(f"No YAML files found in {DATA_MODEL_DIR}")
        return

    for yf in yaml_files:
        with open(yf) as f:
            table_def = yaml.safe_load(f)

        ddl = render_ddl(table_def)
        out_path = OUTPUT_DIR / f"{table_def['table']}.sql"
        out_path.write_text(ddl)
        print(f"Generated {out_path}")

        if args.apply:
            print(f"Applying {out_path} to BigQuery...")
            result = subprocess.run(
                ["bq", "query", "--use_legacy_sql=false", ddl],
                capture_output=True, text=True
            )
            if result.returncode != 0:
                print(f"  FAILED: {result.stderr}", file=sys.stderr)
            else:
                print("  OK")


if __name__ == "__main__":
    main()
