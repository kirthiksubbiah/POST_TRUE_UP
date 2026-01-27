import pytest
from playwright.sync_api import Browser

from config.config import CONFIG


def pytest_addoption(parser):
    parser.addoption(
        "--migrated-date",
        action="store",
        default=None,
        help="Migration date filter, e.g. '16 Jan 2026'",
    )


@pytest.fixture
def migrated_date(request):
    return request.config.getoption("--migrated-date")


@pytest.fixture(scope="session")
def contexts(browser: Browser):
    contexts = {}

    for instance_key, cfg in CONFIG.items():
        context = browser.new_context(
            storage_state=cfg["storage_state"]
        )
        contexts[instance_key] = context

    yield contexts

    for context in contexts.values():
        context.close()
