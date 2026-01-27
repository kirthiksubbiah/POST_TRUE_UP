import re
import pytest
import requests
from datetime import datetime

from config.config import CONFIG
from helpers.logger_helper import get_logger

logger = get_logger(
    name="Global_workflow_logger",
    log_dir="logs/Global_workflow_validation_logs",
    filename_prefix="Global_workflow_validation",
)

# =====================================================
# REGEX
# =====================================================
NAME_MIGRATED_REGEX = re.compile(r"\(migrated(?:\s*\d+)?\)", re.IGNORECASE)


def description_matches_date(updated: str, migrated_date: str | None) -> bool:
    """
    Jira workflow API does NOT return description.
    We rely on 'updated' timestamp to match CLI date.

    migrated_date format: DD Mon YYYY
    updated format: YYYY-MM-DD HH:MM:SS.ssssss
    """
    if not migrated_date:
        return True

    try:
        cli_date = datetime.strptime(migrated_date, "%d %b %Y").date()
        updated_date = datetime.fromisoformat(updated).date()
        return cli_date == updated_date
    except Exception:
        return False


# =====================================================
# TEST
# =====================================================
@pytest.mark.parametrize("instance_key", ["INSTANCE_2"])
def test_workflow_validation_rest_only(instance_key, migrated_date):
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
    # FETCH WORKFLOWS
    # =====================================================
    workflows = []
    start_at = 0
    max_results = 50

    while True:
        resp = session.get(
            f"{base_url}/rest/api/3/workflows/search",
            params={"startAt": start_at, "maxResults": max_results},
            timeout=30,
        )
        resp.raise_for_status()

        data = resp.json()
        values = data.get("values", [])

        if not values:
            break

        workflows.extend(values)
        start_at += max_results
        if start_at >= data.get("total", 0):
            break

    # =====================================================
    # VALIDATION LOGIC
    # =====================================================
    for wf in workflows:
        name = wf.get("name", "")
        updated = wf.get("updated", "")
        active = wf.get("isActive", True)

        # 1️⃣ Check migrated DATE first
        if not description_matches_date(updated, migrated_date):
            continue

        # 2️⃣ Then check NAME for migrated tag
        if NAME_MIGRATED_REGEX.search(name):
            offending.append({
                "Name": name,
                "Active": "Yes" if active else "No",
                "Last Updated": updated,
            })

    # =====================================================
    # OUTPUT
    # =====================================================
    if offending:
        print("\nGLOBAL WORKFLOWS WITH MIGRATED TAG\n")
        for wf in offending:
            print(f"- {wf['Name']}")
            print(f"  Active       : {wf['Active']}")
            print(f"  Last Updated : {wf['Last Updated']}")
            print()
    else:
        print("\nNO WORKFLOW MIGRATED TAG FOUND\n")

    # =====================================================
    # ASSERT
    # =====================================================
    assert not offending, (
        f"{len(offending)} workflows still contain migrated suffixes"
    )
