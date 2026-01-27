from playwright.sync_api import Page


def collect_request_links(page: Page) -> dict[str, str]:
    links = {}

    page.wait_for_selector("a[data-test-id^='request-type:']", timeout=30000)

    anchors = page.locator("a[data-test-id^='request-type:']").all()

    for a in anchors:
        test_id = a.get_attribute("data-test-id")
        href = a.get_attribute("href")

        if not test_id or not href:
            continue

        # Extract canonical request name
        # data-test-id="request-type:Request new software"
        name = test_id.split("request-type:", 1)[-1].strip()

        links[name] = href

    return links
