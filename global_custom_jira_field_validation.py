import re
import pytest
import requests

from config.config import CONFIG
from helpers.logger_helper import get_logger

logger = get_logger(
    name="Global_custom_field_logger",
    log_dir="logs/Global_custom_field_validation_logs",
    filename_prefix="Global_custom_field_validation",
)

# =====================================================
# TYPE MAP
# =====================================================
TYPE_MAP = {
    "string": "Text",
    "number": "Number",
    "datetime": "Date / Date Time",
    "date": "Date",
    "array": "Multi-value",
    "option": "Select List (single)",
    "option-with-child": "Cascading Select",
    "user": "User",
}

# =====================================================
# REGEX
# =====================================================
DESCRIPTION_DATE_REGEX = re.compile(
    r"Migrated on 16 Jan 2026", re.IGNORECASE
)

NAME_MIGRATED_REGEX = re.compile(
    r"\(migrated(?:\s*\d+)?\)", re.IGNORECASE
)


# =====================================================
# TEST
# =====================================================
@pytest.mark.parametrize("instance_key", ["INSTANCE_2"])
def test_global_custom_jira_field_validation_rest_only(instance_key):
    cfg = CONFIG[instance_key]

    base_url = cfg["base_url"]
    auth = (cfg["email"], cfg["api_token"])

    offending = []
    start_at = 0
    max_results = 50

    # =====================================================
    # FETCH ALL CUSTOM FIELDS (PAGINATED)
    # =====================================================
    while True:
        resp = requests.get(
            f"{base_url}/rest/api/3/field/search",
            auth=auth,
            params={
                "startAt": start_at,
                "maxResults": max_results,
                "type": "custom",
            },
            timeout=30,
        )
        resp.raise_for_status()

        data = resp.json()
        values = data.get("values", [])

        if not values:
            break

        for field in values:
            name = field.get("name", "")
            description = field.get("description") or ""
            field_id = field.get("id", "")
            schema_type = field.get("schema", {}).get("type", "unknown")

            # -------------------------------------------------
            # STEP 1: DESCRIPTION MUST HAVE MIGRATION DATE
            # -------------------------------------------------
            if not DESCRIPTION_DATE_REGEX.search(description):
                continue

            # -------------------------------------------------
            # STEP 2: NAME MUST STILL HAVE "(migrated*)"
            # -------------------------------------------------
            if NAME_MIGRATED_REGEX.search(name):
                offending.append({
                    "Name": name,
                    "Category": TYPE_MAP.get(schema_type, schema_type),
                    "Description": description,
                    "Field ID": field_id,
                })

        start_at += max_results
        if start_at >= data.get("total", 0):
            break

    # =====================================================
    # OUTPUT
    # =====================================================
    if offending:
        print("\n❌ GLOBAL CUSTOM FIELDS STILL HAVING MIGRATED TAG\n")
        for f in offending:
            print(f"- Name       : {f['Name']}")
            print(f"  Category   : {f['Category']}")
            print(f"  Description: {f['Description']}")
            print(f"  Field ID   : {f['Field ID']}")
            print()
    else:
        print("\n✅ No status migrated tag found")

    # =====================================================
    # ASSERT
    # =====================================================
    assert not offending, (
        f"{len(offending)} custom fields still have '(migrated)' in name "
        f"after migration on 16 Jan 2026"
    )
