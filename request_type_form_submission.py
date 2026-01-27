import pytest
import re
from playwright.sync_api import Page
from helpers.collect_request_type_links import collect_request_links
from helpers.jira_form_submission import create_request
from config.config import CONFIG
from helpers.logger_helper import get_logger

logger = get_logger(
    name="form_submission_logger",
    log_dir="logs/form_submission_logs",
    filename_prefix="form_submission",
)


INSTANCE_KEY = "INSTANCE_2"


def get_service_desk_id_from_portal(portal: str) -> str:
    m = re.search(r"/portal/(\d+)", portal)
    if not m:
        raise RuntimeError(f"Cannot extract serviceDeskId from {portal}")
    return m.group(1)


@pytest.mark.e2e
def test_form_submission_via_rest(contexts):
    cfg = CONFIG[INSTANCE_KEY]

    base = cfg["base_url"]
    portal = cfg["portal"]
    service_desk_id = get_service_desk_id_from_portal(portal)

    context = contexts[INSTANCE_KEY]
    page = context.new_page()

    failures = []

    print(f"\n========== INSTANCE: {INSTANCE_KEY} ==========")

    # AUTHENTICATED PAGE
    page.goto(base + portal, wait_until="domcontentloaded")

    links = collect_request_links(page)
    print(f"Found {len(links)} forms for submission")
    assert links, "No request types discovered (likely auth issue)"

    for req_name, href in links.items():
        request_type_id = href.split("/create/")[-1]
        print(f"\n→ Submitting: {req_name}")

        try:
            result = create_request(
                instance_key=INSTANCE_KEY,
                service_desk_id=service_desk_id,
                request_type_id=request_type_id,
                request_type_name=req_name,
            )

            data = result["body"]

            print(f"   ✔ HTTP Code : {result['status_code']}")
            print(f"   ✔ Issue Key : {data['issueKey']}")
            print(f"   ✔ Summary   : {data['summary']}")
            print(f"   ✔ Status    : {data['currentStatus']['status']}")
            print(f"   ✔ Link      : {data['_links']['web']}")

        except Exception as e:
            print(f"   ✖ FAILED : {req_name}")
            print(f"     Reason : {e}")
            failures.append({"request": req_name, "error": str(e)})

    page.close()

    if failures:
        print("\n========== FAILURES SUMMARY ==========")
        for f in failures:
            print(f"{f['request']} → {f['error']}")
        pytest.fail(f"{len(failures)} request submissions failed")












