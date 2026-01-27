import pytest
from urllib.parse import urljoin
from playwright.sync_api import BrowserContext
from helpers.collect_request_type_links import collect_request_links
from config.config import CONFIG
import os
os.environ["NODE_TLS_REJECT_UNAUTHORIZED"] = "0"
from helpers.logger_helper import get_logger

logger = get_logger(
    name="link_logger",
    log_dir="logs/link_validation_logs",
    filename_prefix="link_validation",
)


# =====================================================
# FETCH REQUEST LINKS
# =====================================================
def fetch_request_links(context: BrowserContext, instance_key: str) -> dict[str, str]:
    cfg = CONFIG[instance_key]
    base = cfg["base_url"]
    portal = cfg["portal"]

    page = context.new_page()
    page.goto(base + portal, wait_until="domcontentloaded")
    links = collect_request_links(page)
    page.close()

    assert links, f"No request links found for {instance_key}"
    return links


# =====================================================
# PRINT LINK DETAILS
# =====================================================
def print_link_details(context: BrowserContext, instance_key: str, links: dict[str, str]):
    cfg = CONFIG[instance_key]
    base = cfg["base_url"]

    page = context.new_page()
    broken_links = []

    print(f"\n📋 {instance_key} LINK DETAILS:")
    for name, href in links.items():
        url = urljoin(base, href)
        try:
            response = page.request.get(url, max_redirects=5, timeout=30000)
            print(f"  - {name}")
            print(f"      STATUS   : {response.status}")
            print(f"      REDIRECT : {response.url}")

            if response.status >= 400:
                broken_links.append((name, url, response.status))

        except Exception as e:
            print(f"  - {name}")
            print(f"      STATUS   : ERROR")
            print(f"      REASON   : {e}")
            broken_links.append((name, url, "EXCEPTION"))

    page.close()
    return broken_links



# =====================================================
# POSITIVE TEST
# =====================================================
def test_compare_instance_links_positive(contexts):
    left, right = list(CONFIG.keys())

    left_links = fetch_request_links(contexts[left], left)
    right_links = fetch_request_links(contexts[right], right)

    print("\n========== POSITIVE LINK COMPARISON ==========")

    left_broken = print_link_details(contexts[left], left, left_links)
    right_broken = print_link_details(contexts[right], right, right_links)

    print(f"\n{left} count  : {len(left_links)}")
    print(f"{right} count : {len(right_links)}")

    assert set(left_links) == set(right_links), "Link names mismatch"

    all_broken = left_broken + right_broken
    if all_broken:
        print("\n❌ BROKEN LINKS DETECTED:")
        for name, url, status in all_broken:
            print(f" - {name} | {status} | {url}")

    assert not all_broken, "One or more links are broken"



# =====================================================
# NEGATIVE TEST (INTENTIONAL FAILURE)
# =====================================================
@pytest.mark.xfail(strict=True, reason="link injected for negative testing")
def test_compare_instance_links_negative(contexts):
    left, right = list(CONFIG.keys())

    left_links = fetch_request_links(contexts[left], left)
    right_links = fetch_request_links(contexts[right], right)

    #Inject fake link
    right_links["FAKE_BROKEN_LINK"] = "/create/THIS_SHOULD_FAIL"

    print("\n========== NEGATIVE LINK COMPARISON ==========")

    # PRINT LINKS FIRST
    print_link_details(contexts[left], left, left_links)
    print_link_details(contexts[right], right, right_links)

    # PRINT COUNTS
    print(f"\n{left} count  : {len(left_links)}")
    print(f"{right} count : {len(right_links)}")

    # SHOW MISMATCH
    extra = set(right_links) - set(left_links)
    if extra:
        print(f"\n➕ Extra links detected in {right}:")
        for k in sorted(extra):
            print(f" + {k}")

    #EXPECTED FAILURE
    assert set(left_links) == set(right_links)
