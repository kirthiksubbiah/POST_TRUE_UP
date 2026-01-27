import re
import pytest
import requests

from config.config import CONFIG
from helpers.logger_helper import get_logger

logger = get_logger(
    name="Global_status_logger",
    log_dir="logs/Global_status_validation_logs",
    filename_prefix="Global_status_validation",
)

# =====================================================
# REGEX
# =====================================================
NAME_MIGRATED_REGEX = re.compile(r"\(migrated(?:\s*\d+)?\)", re.IGNORECASE)


def description_matches_date(description: str, migrated_date: str | None) -> bool:
    """
    Checks ONLY description for:
    (Migrated on <DD Mon YYYY> ...)
    """
    if not migrated_date:
        return True

    return re.search(
        rf"\(migrated\s+on\s+{re.escape(migrated_date)}.*?\)",
        description,
        re.IGNORECASE,
    ) is not None


# =====================================================
# TEST
# =====================================================
@pytest.mark.parametrize("instance_key", ["INSTANCE_2"])
def test_global_status_validation_rest_only(instance_key, migrated_date):
    cfg = CONFIG[instance_key]

    base_url = cfg["base_url"]
    auth = (cfg["email"], cfg["api_token"])

    offending = []

    # =====================================================
    # SESSION
    # =====================================================
    session = requests.Session()
    session.auth = auth
    session.headers.update({
        "Accept": "application/json",
        "Content-Type": "application/json",
    })

    # =====================================================
    # FETCH STATUSES
    # =====================================================
    resp = session.get(f"{base_url}/rest/api/3/status", timeout=30)
    resp.raise_for_status()

    statuses = resp.json()

    # =====================================================
    # VALIDATION LOGIC
    # =====================================================
    for status in statuses:
        name = status.get("name", "")
        description = status.get("description", "") or ""
        category = status.get("statusCategory", {}).get("name", "")

        # 1️⃣ Check migrated DATE in description
        if not description_matches_date(description, migrated_date):
            continue

        # 2️⃣ Check migrated tag in NAME
        if NAME_MIGRATED_REGEX.search(name):
            offending.append({
                "Name": name,
                "Category": category,
                "Description": description,
            })

    # =====================================================
    # OUTPUT
    # =====================================================
    if offending:
        print("\nGLOBAL STATUSES WITH MIGRATED TAG IN NAME\n")
        for s in offending:
            print(f"- {s['Name']}")
            print(f"  Category    : {s['Category']}")
            print(f"  Description : {s['Description']}")
            print()
    else:
        print("\nNO GLOBAL STATUS WITH MIGRATED TAG FOUND\n")

    # =====================================================
    # ASSERT
    # =====================================================
    assert not offending, (
        f"{len(offending)} statuses still contain migrated suffixes"
    )
