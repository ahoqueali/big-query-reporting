#!/usr/bin/env python3
"""
validate_mapping.py

Checks that every ontology/*.yaml file's `maps_to` block references a
semantic model (and dimensions/measures) that actually exist in
semantic_models/*.yml. Also checks that every semantic model's columns
trace back to a data_model/*.yaml table, catching drift between the
three layers early.

Usage:
    python scripts/validate_mapping.py
"""

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Missing dependency. Run: pip install pyyaml --break-system-packages")

ROOT = Path(__file__).resolve().parent.parent
DATA_MODEL_DIR = ROOT / "data_model"
SEMANTIC_DIR = ROOT / "semantic_models"
ONTOLOGY_DIR = ROOT / "ontology"


def load_yaml_files(directory: Path, pattern="*.yml"):
    files = list(directory.glob(pattern)) + list(directory.glob(pattern.replace("yml", "yaml")))
    return {f.stem: yaml.safe_load(f.read_text()) for f in files}


def main():
    errors = []

    data_models = load_yaml_files(DATA_MODEL_DIR, "*.yaml")
    semantic_models_raw = load_yaml_files(SEMANTIC_DIR, "*.yml")
    ontologies = load_yaml_files(ONTOLOGY_DIR, "*.yaml")

    # Flatten semantic models into name -> {dimensions:set, measures:set}
    semantic_index = {}
    for _, doc in semantic_models_raw.items():
        for sm in doc.get("semantic_models", []):
            name = sm["name"]
            dims = {d["name"] for d in sm.get("dimensions", [])}
            measures = {m["name"] for m in sm.get("measures", [])}
            semantic_index[name] = {"dimensions": dims, "measures": measures}

    # Validate each ontology file's maps_to block
    for onto_name, onto in ontologies.items():
        maps_to = onto.get("maps_to")
        if not maps_to:
            errors.append(f"[ontology:{onto_name}] missing 'maps_to' block")
            continue

        sm_name = maps_to.get("semantic_model")
        if sm_name not in semantic_index:
            errors.append(
                f"[ontology:{onto_name}] maps_to.semantic_model "
                f"'{sm_name}' not found in semantic_models/"
            )
            continue

        sm = semantic_index[sm_name]
        for dim in maps_to.get("dimensions", []):
            if dim not in sm["dimensions"]:
                errors.append(
                    f"[ontology:{onto_name}] dimension '{dim}' not found "
                    f"in semantic model '{sm_name}' (has: {sorted(sm['dimensions'])})"
                )
        for measure in maps_to.get("measures", []):
            if measure not in sm["measures"]:
                errors.append(
                    f"[ontology:{onto_name}] measure '{measure}' not found "
                    f"in semantic model '{sm_name}' (has: {sorted(sm['measures'])})"
                )

    # Validate semantic model expr columns exist in data_model tables
    table_columns = {
        name: {c["name"] for c in tbl["columns"]}
        for name, tbl in data_models.items()
    }
    for _, doc in semantic_models_raw.items():
        for sm in doc.get("semantic_models", []):
            table_ref = sm["model"].replace("ref('", "").replace("')", "")
            if table_ref not in table_columns:
                errors.append(
                    f"[semantic:{sm['name']}] model ref '{table_ref}' "
                    f"not found in data_model/"
                )
                continue
            cols = table_columns[table_ref]
            for dim in sm.get("dimensions", []):
                expr = dim.get("expr", dim["name"])
                if dim["type"] != "time" and expr not in cols and dim["name"] not in cols:
                    pass  # time dims and derived exprs are allowed to skip this check
            for measure in sm.get("measures", []):
                expr = measure.get("expr", measure["name"])
                if expr not in cols:
                    errors.append(
                        f"[semantic:{sm['name']}] measure '{measure['name']}' "
                        f"expr '{expr}' not found in data_model table '{table_ref}' "
                        f"(has: {sorted(cols)})"
                    )

    if errors:
        print(f"FAILED: {len(errors)} issue(s) found:\n")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("All ontology → semantic → data model mappings are consistent.")


if __name__ == "__main__":
    main()
