import re
import pytest
import requests
from config.config import CONFIG
from helpers.logger_helper import get_logger


logger = get_logger(
    name="Global_workflow_scheme_logger",
    log_dir="logs/Global_workflow_scheme_validation_logs",
    filename_prefix="Global_workflow_scheme_validation",
)

# =====================================================
# REGEX BUILDER (REUSED)
# =====================================================
def build_migrated_regex(migrated_date: str | None):
    if migrated_date:
        return re.compile(
            rf"\(migrated\s+on\s+{re.escape(migrated_date)}.*?\)",
            re.IGNORECASE,
        )
    return re.compile(r"\(migrated(?:\s*\d+)?\)", re.IGNORECASE)


@pytest.mark.parametrize("instance_key", ["INSTANCE_2"])
def test_workflow_scheme_validation_rest_only(instance_key, migrated_date):
    cfg = CONFIG[instance_key]

    base_url = cfg["base_url"]
    auth = (cfg["email"], cfg["api_token"])

    MIGRATED_REGEX = build_migrated_regex(migrated_date)

    offending = []

    # =====================================================
    # SESSION (STABILITY)
    # =====================================================
    session = requests.Session()
    session.auth = auth
    session.headers.update({
        "Accept": "application/json",
        "Content-Type": "application/json",
    })

    # =====================================================
    # FETCH ALL WORKFLOW SCHEMES
    # =====================================================
    resp = session.get(
        f"{base_url}/rest/api/3/workflowscheme",
        timeout=30,
    )
    resp.raise_for_status()

    schemes = resp.json().get("values", [])

    # =====================================================
    # FIND MIGRATED WORKFLOW SCHEMES
    # =====================================================
    for scheme in schemes:
        name = scheme.get("name", "")
        description = scheme.get("description", "") or ""

        combined = f"{name} {description}"

        if MIGRATED_REGEX.search(combined):
            offending.append({
                "Name": name,
                "Description": description,
            })

    # =====================================================
    # OUTPUT
    # =====================================================
    if offending:
        print("\nGLOBAL WORKFLOW SCHEMES WITH MIGRATED TAG\n")
        for s in offending:
            print(f"- {s['Name']}")
            print(f"  Description  : {s['Description']}")
            print()

    # =====================================================
    # ASSERT
    # =====================================================
    assert not offending, (
        f"{len(offending)} workflow schemes still contain migrated suffixes"
    )
