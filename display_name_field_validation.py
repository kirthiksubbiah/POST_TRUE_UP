from urllib.parse import urljoin
from playwright.sync_api import Page
import pytest
from helpers.collect_request_type_links import collect_request_links
from config.config import CONFIG
from helpers.logger_helper import get_logger

logger = get_logger(
    name="display_name_logger",
    log_dir="logs/display_name_validation_logs",
    filename_prefix="display_name_validation",
)


# =========================================================
# COLLECT FORM FIELDS (UNCHANGED)
# =========================================================
def collect_form_fields(page: Page) -> dict[str, dict]:
    fields = {}
    page.wait_for_timeout(2000)

    labels = page.locator(
        "label, "
        "span[data-testid*='label'], "
        "div[data-testid*='label'], "
        "div[aria-label]"
    ).all()

    for label in labels:
        raw_text = label.inner_text().strip()

        if not raw_text:
            continue
        if len(raw_text) > 60:
            continue
        if raw_text.lower() in {
            "select...",
            "normal text",
            "add attachment",
            "drop files here",
        }:
            continue

        name = raw_text.split("\n")[0].replace("*", "").strip()
        if not name:
            continue

        required = "*" in raw_text

        box_label = label.bounding_box()
        if not box_label:
            continue

        label_for = label.get_attribute("for")

        # RICH TEXT DETECTION (Description + Jira Forms custom fields)
        if (
            label_for == "description"
            or (
                label_for
                and label_for.startswith("customfield_")
                and label.locator(
                    "xpath=following::div[@contenteditable='true'][1]"
                ).count() > 0
            )
        ):
            fields[name] = {
                "required": required,
                "type": "richtext",
            }
            continue

        control = label.locator(
            "xpath=following::input[1] | "
            "following::textarea[1] | "
            "following::*[@role='combobox'][1]"
        )

        if control.count() == 0:
            continue

        box_control = control.first.bounding_box()
        if not box_control:
            continue
        if box_control["y"] - box_label["y"] > 200:
            continue

        tag = control.first.evaluate("el => el.tagName")
        role = control.first.get_attribute("role")

        if tag == "TEXTAREA":
            field_type = "textarea"
        elif role == "combobox":
            field_type = "dropdown"
        else:
            field_type = "text"

        fields[name] = {
            "required": required,
            "type": field_type,
        }

    attachment_heading = page.locator(
        "span:has-text('Attachment'), div:has-text('Attachment')"
    )

    if attachment_heading.count() > 0:
        fields["Attachment"] = {
            "required": False,
            "type": "attachment",
        }

    return fields


# =========================================================
# COMPARE + PRINT (LOGIC UNCHANGED, RETURN STATUS ADDED)
# =========================================================
def compare_and_print_fields(form_name, left_name, right_name, left, right) -> bool:
    left_keys = set(left)
    right_keys = set(right)

    common = left_keys & right_keys
    missing_in_right = left_keys - right_keys
    missing_in_left = right_keys - left_keys

    mismatched = []
    for k in common:
        if left[k] != right[k]:
            mismatched.append(k)

    print(f"\n🔍 Comparing form: {form_name}")

    print(f"\n📋 {left_name} fields detected ({len(left)})")
    for name, meta in left.items():
        req = "required" if meta["required"] else "optional"
        print(f" - {name} [{meta['type']}, {req}]")

    print(f"\n📋 {right_name} fields detected ({len(right)})")
    for name, meta in right.items():
        req = "required" if meta["required"] else "optional"
        print(f" - {name} [{meta['type']}, {req}]")

    print(f"\n------ FORM SUMMARY: {form_name} ------")
    print(f"Number of {left_name} fields  : {len(left)}")
    print(f"Number of {right_name} fields : {len(right)}")
    print(f"Number of fields matched     : {len(common) - len(mismatched)}")

    failed = False

    if missing_in_right:
        failed = True
        print(f"\n➖ Fields Missing in {right_name}:")
        for f in sorted(missing_in_right):
            print(f" - {f}")

    if missing_in_left:
        failed = True
        print(f"\n➕ Extra Fields in {right_name}:")
        for f in sorted(missing_in_left):
            print(f" + {f}")

    if mismatched:
        failed = True
        print(f"\n❌ Field behaviour mismatch:")
        for f in mismatched:
            print(f" * {f}")
            print(f"   {left_name} : {left[f]}")
            print(f"   {right_name}: {right[f]}")

    if not failed:
        print("\n✅ All fields are matching")

    return not failed


# =========================================================
# TEST CASE (FAILS IF ANY FORM FAILS)
# =========================================================
def test_field_validation(contexts):
    print("\n================ FIELD COMPARISON =================\n")

    fields_by_instance = {}

    # -------- DISCOVERY --------
    for instance_key, context in contexts.items():
        cfg = CONFIG[instance_key]
        base = cfg["base_url"]
        portal = cfg["portal"]

        page = context.new_page()
        page.goto(base + portal, wait_until="domcontentloaded")

        links = collect_request_links(page)
        assert links, f"No request types found for {instance_key}"

        instance_forms = {}

        for form_name, href in links.items():
            page.goto(urljoin(base, href), wait_until="domcontentloaded")
            instance_forms[form_name] = collect_form_fields(page)

        page.close()
        fields_by_instance[instance_key] = instance_forms

    # -------- COMPARISON --------
    left, right = list(fields_by_instance.keys())

    failed_forms = []

    for form in fields_by_instance[left]:
        passed = compare_and_print_fields(
            form_name=form,
            left_name=left,
            right_name=right,
            left=fields_by_instance[left].get(form, {}),
            right=fields_by_instance[right].get(form, {}),
        )

        if not passed:
            failed_forms.append(form)

    # -------- FINAL ASSERT --------
    if failed_forms:
        pytest.fail(
            f"\n❌ Field comparison failed for {len(failed_forms)} form(s): "
            f"{', '.join(failed_forms)}"
        )
