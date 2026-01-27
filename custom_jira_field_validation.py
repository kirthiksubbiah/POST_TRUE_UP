import requests
import urllib3
from requests.auth import HTTPBasicAuth
from playwright.sync_api import Page
from helpers.collect_request_type_links import collect_request_links
from config.config import CONFIG
from helpers.logger_helper import get_logger

logger = get_logger(
    name="field_logger",
    log_dir="logs/field_validation_logs",
    filename_prefix="field_validation",
)


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# =====================================================
# REST HELPER
# =====================================================
def jira_get(cfg, path):
    r = requests.get(
        cfg["base_url"] + path,
        auth=HTTPBasicAuth(cfg["email"], cfg["api_token"]),
        headers={"Accept": "application/json"},
        verify=False,
    )
    r.raise_for_status()
    return r.json()


# =====================================================
# NORMALIZATION
# =====================================================
def normalize_field_name(name: str) -> str:
    return (
        name.lower()
        .replace("(migrated)", "")
        .replace("(migrated )", "")
        .strip()
    )


# =====================================================
# OUTPUT: PER-INSTANCE FIELD SUMMARY
# =====================================================
def print_instance_field_summary(instance_key, data):
    print(f"\n### INSTANCE: {instance_key} ###\n")

    for req in sorted(data):
        fields = data[req]

        print(f"🔹 {req}")

        if not fields:
            print("  [JIRA FORM] No linked custom fields")
        else:
            for fid, name in sorted(fields.items()):
                print(f"  - {fid} → {name}")

        print()


# =====================================================
# DOM FIELD DISCOVERY
# =====================================================
def discover_dom_custom_fields(page: Page) -> set[str]:
    field_ids = set()
    labels = page.locator("label")

    for i in range(labels.count()):
        for_attr = labels.nth(i).get_attribute("for")
        if for_attr and for_attr.startswith("customfield_"):
            field_ids.add(for_attr)

    return field_ids


# =====================================================
# PROFORMA + DOM FIELD DISCOVERY
# =====================================================
def discover_backing_field_ids(page: Page, base: str, create_links):
    results = {}

    def on_request_finished(request):
        response = request.response()
        if not response:
            return

        url = response.url.lower()
        if "/gateway/api/proforma/" in url and "fielddata" in url:
            try:
                data = response.json()
                for key in data:
                    if key.startswith("customfield_"):
                        current_fields.add(key)
            except Exception:
                pass

    page.on("requestfinished", on_request_finished)

    for req_name, href in create_links.items():
        current_fields = set()

        page.goto(base + href, wait_until="domcontentloaded")
        page.wait_for_timeout(8000)

        current_fields |= discover_dom_custom_fields(page)
        results[req_name] = current_fields

    page.remove_listener("requestfinished", on_request_finished)
    return results


# =====================================================
# customfield_x → FIELD NAME
# =====================================================
def resolve_custom_field_names(cfg, field_ids):
    fields = jira_get(cfg, "/rest/api/3/field")
    field_map = {f["id"]: f["name"] for f in fields}
    return {fid: field_map.get(fid, "UNKNOWN") for fid in field_ids}


# =====================================================
# MAIN TEST — STRICT VALIDATION
# =====================================================
def test_form_backing_custom_fields(contexts):
    instance_results = {}

    rename_failed = False
    add_failed = False
    remove_failed = False

    # ---------- COLLECT ----------
    for instance_key, context in contexts.items():
        cfg = CONFIG[instance_key]
        base = cfg["base_url"]
        portal = cfg["portal"]

        page = context.new_page()
        page.goto(base + portal, wait_until="domcontentloaded")

        create_links = collect_request_links(page)
        backing_ids = discover_backing_field_ids(page, base, create_links)
        page.close()

        resolved = {}
        for req, ids in backing_ids.items():
            resolved[req] = resolve_custom_field_names(cfg, ids)

        instance_results[instance_key] = resolved
    # =====================================================
    # OUTPUT HELPERS – CUSTOM FIELD SUMMARY
    # =====================================================
    def print_section(title: str):
        print(f"\n================ {title} =================\n")


    def print_custom_summary(instance_key: str, data: dict[str, dict[str, str]]):
        print(f"\n### INSTANCE: {instance_key} ###\n")

        for req in sorted(data):
            fields = data[req]

            print(f"🔹 {req}")

            if not fields:
                print("  [JIRA FORM] No linked custom fields")
            else:
                for fid, name in sorted(fields.items()):
                    print(f"  - {fid} → {name}")

            print()


    # =================================================
    # PHASE 1: RAW VIEW
    # =================================================

    # print_section("JIRA FORM LINKED CUSTOM FIELDS")

    # inst1, inst2 = list(instance_results.keys())

    # print_custom_summary(inst1, instance_results[inst1])
    # print_custom_summary(inst2, instance_results[inst2])

    # print("\n" + "-" * 60 + "\n")


    # =================================================
    # PHASE 2: STRICT COMPARISON
    # =================================================
    print("\n================ JIRA FORM FIELD COMPARISON =================\n")

    inst1, inst2 = list(instance_results.keys())
    # print(f"INSTANCE_1 = {inst1}")
    # print(f"INSTANCE_2 = {inst2}\n")

    for req in sorted(set(instance_results[inst1]) | set(instance_results[inst2])):
        f1 = instance_results[inst1].get(req, {})
        f2 = instance_results[inst2].get(req, {})

        norm1 = {normalize_field_name(v): (k, v) for k, v in f1.items()}
        norm2 = {normalize_field_name(v): (k, v) for k, v in f2.items()}

        if not norm1 and not norm2:
            continue

        print(f"🔹 {req}")

        # COMMON
        for cname in sorted(norm1.keys() & norm2.keys()):
            id1, name1 = norm1[cname]
            id2, name2 = norm2[cname]

            if name1 == name2:
                print(f"  ✅ {name1} : {id1} → {id2}")
            else:
                print(f"  ❌ RENAMED {name1} → {name2}")
                print(f"     {id1} → {id2}")
                rename_failed = True

        # REMOVED
        for cname in sorted(norm1.keys() - norm2.keys()):
            id1, name1 = norm1[cname]
            print(f"  ❌ REMOVED {name1} : {id1}")
            remove_failed = True

        # ADDED
        for cname in sorted(norm2.keys() - norm1.keys()):
            id2, name2 = norm2[cname]
            print(f"  ❌ ADDED {name2} : {id2}")
            add_failed = True

        print()

    # =================================================
    # FINAL ASSERTIONS
    # =================================================
    assert not rename_failed, "Custom field rename detected"
    assert not add_failed, "Custom field addition detected"
    assert not remove_failed, "Custom field removal detected"
