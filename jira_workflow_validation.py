from playwright.sync_api import Page
from config.config import CONFIG
from helpers.logger_helper import get_logger

logger = get_logger(
    name="workflow_logger",
    log_dir="logs/workflow_validation_logs",
    filename_prefix="workflow_validation",
)


# =====================================================
# NORMALIZATION
# =====================================================
def normalize_workflow_name(name: str) -> str:
    return name.lower().replace("(migrated)", "").strip()


def clean_issue_type(name: str) -> str:
    return name.replace("(Assign)", "").strip()


def normalize_workflow_text(text: str) -> str:
    lines = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            lines.append(" ".join(line.split()))
    return "\n".join(lines)


def print_section(title: str):
    print(f"\n================ {title} =================\n")


# =====================================================
# UI SCRAPER – WORKFLOWS (POC STYLE)
# =====================================================
def collect_workflows_from_ui(page: Page) -> dict[str, list[str]]:
    workflows = {}

    for row in page.locator("tr").all():
        name_node = row.locator("h3.project-config-workflow-name")
        if name_node.count() == 0:
            continue

        workflow_name = name_node.first.inner_text().strip()
        if not workflow_name.startswith("SUP:"):
            continue

        issue_types = {
            clean_issue_type(span.inner_text().strip())
            for span in row.locator("span.project-config-issuetype-name").all()
            if span.inner_text().strip()
        }

        workflows[workflow_name] = sorted(issue_types)

    return workflows


# =====================================================
# UI SCRAPER – WORKFLOW SCHEME
# =====================================================
def get_workflow_scheme_name(page: Page) -> str:
    h2 = page.locator("h2.project-config-workflows-scheme-name")
    if h2.count() > 0:
        title = h2.first.get_attribute("title")
        return title.strip() if title else h2.first.inner_text().strip()
    return "UNKNOWN WORKFLOW SCHEME"

# =====================================================
# OUTPUT – WORKFLOW SUMMARY
# =====================================================

def print_workflow_summary(instance_key: str, workflows: dict[str, list[str]]):
    print(f"\n### INSTANCE: {instance_key} ###\n")

    for wf in sorted(workflows):
        print(f"🔹 {wf}")

        issue_types = workflows[wf]
        if not issue_types:
            print("  (no issue types)")
        else:
            for it in issue_types:
                print(f"  - {it}")

        print()
# =====================================================
# UI SCRAPER – WORKFLOW "VIEW AS TEXT"
# =====================================================
def collect_workflow_texts(page: Page) -> dict[str, str]:
    results = {}

    for link in page.locator("a.project-config-workflow-text-link").all():
        workflow_name = link.get_attribute("data-workflowname")
        if not workflow_name or not workflow_name.startswith("SUP:"):
            continue

        link.click()

        dialog = page.locator("div[role='dialog'] pre, div[role='dialog']").first
        dialog.wait_for(timeout=30000)

        results[workflow_name] = normalize_workflow_text(
            dialog.inner_text()
        )

        page.keyboard.press("Escape")
        page.wait_for_timeout(500)

    return results


# =====================================================
# TRANSITION PARSER (ORDER-INDEPENDENT)
# =====================================================
def parse_workflow_transitions(text: str) -> set[tuple[str, str, str, str]]:
    transitions = set()
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    current_from = None
    i = 0

    while i < len(lines):
        line = lines[i]

        if "→" not in line and not line.startswith("No Screen") and not line.startswith("JIRA"):
            current_from = line
            i += 1
            continue

        transition = line
        screen = "No Screen"

        if i + 1 < len(lines) and "Screen" in lines[i + 1]:
            screen = lines[i + 1]
            i += 1

        if i + 1 < len(lines) and lines[i + 1].startswith("→"):
            to_status = lines[i + 1].replace("→", "").strip()
            transitions.add((current_from, transition, screen, to_status))
            i += 2
            continue

        i += 1

    return transitions


# =====================================================
# MAIN TEST
# =====================================================
def test_workflow_validation(contexts):
    instance_results = {}

    scheme_failed = False
    workflow_failed = False
    issuetype_failed = False
    transition_failed = False

    # ---------- COLLECT ----------
    for instance_key, context in contexts.items():
        cfg = CONFIG[instance_key]
        page = context.new_page()

        page.goto(
            cfg["base_url"] + cfg["workflow_settings_url"],
            wait_until="domcontentloaded"
        )
        page.wait_for_timeout(3000)

        instance_results[instance_key] = {
            "scheme": get_workflow_scheme_name(page),
            "workflows": collect_workflows_from_ui(page),
            "texts": collect_workflow_texts(page),
        }

        page.close()

    inst1, inst2 = list(instance_results.keys())

    scheme1 = instance_results[inst1]["scheme"]
    scheme2 = instance_results[inst2]["scheme"]

    w1 = instance_results[inst1]["workflows"]
    w2 = instance_results[inst2]["workflows"]

    t1 = instance_results[inst1]["texts"]
    t2 = instance_results[inst2]["texts"]

    norm_w1 = {normalize_workflow_name(k): k for k in w1}
    norm_w2 = {normalize_workflow_name(k): k for k in w2}

    # =================================================
    # PHASE 1: RAW VIEW (command this if you dont what raw view summary )
    # =================================================
    
    print_section("JIRA WORKFLOWS (RAW VIEW)")
    print_workflow_summary(inst1, w1)
    print_workflow_summary(inst2, w2)

    # =================================================
    # PHASE 2: WORKFLOW SCHEME
    # =================================================
    print_section("WORKFLOW SCHEME COMPARISON")
    print(f"{inst1}: {scheme1}")
    print(f"{inst2}: {scheme2}")

    if scheme1 != scheme2:
        print("❌ Workflow scheme mismatch")
        scheme_failed = True
    else:
        print("✅ Workflow schemes match")

    # =================================================
    # PHASE 3: WORKFLOWS
    # =================================================
    print_section("WORKFLOWS COMPARISON")

    for key in sorted(set(norm_w1) | set(norm_w2)):
        wf1 = norm_w1.get(key)
        wf2 = norm_w2.get(key)

        if wf1 and wf2:
            if wf1 == wf2:
                print(f"✅ {wf1}")
            else:
                print(f"❌ RENAMED {wf1} → {wf2}")
                workflow_failed = True
        elif wf1:
            print(f"❌ REMOVED {wf1}")
            workflow_failed = True
        else:
            print(f"❌ ADDED {wf2}")
            workflow_failed = True

    # =================================================
    # PHASE 4: ISSUE TYPES
    # =================================================
    print_section("ISSUE TYPES COMPARISON (PER WORKFLOW)")

    for key in sorted(set(norm_w1) | set(norm_w2)):
        wf1 = norm_w1.get(key)
        wf2 = norm_w2.get(key)

        it1 = set(w1.get(wf1, [])) if wf1 else set()
        it2 = set(w2.get(wf2, [])) if wf2 else set()

        print(f"🔹 {wf1 or wf2}")
        print(f"   {inst1}: {', '.join(sorted(it1)) if it1 else '(none)'}")
        print(f"   {inst2}: {', '.join(sorted(it2)) if it2 else '(none)'}")

        if it1 != it2:
            print("   ❌ Issue type mismatch")
            issuetype_failed = True
        else:
            print("   ✅ Issue types match")

        print()

    # =================================================
    # PHASE 5: TRANSITIONS 
    # =================================================
    print_section("WORKFLOW TRANSITION TEXT COMPARISON")

    norm_t1 = {normalize_workflow_name(k): v for k, v in t1.items()}
    norm_t2 = {normalize_workflow_name(k): v for k, v in t2.items()}

    for wf in sorted(set(norm_t1) | set(norm_t2)):
        print(f"🔹 {wf}")

        raw1 = norm_t1.get(wf)
        raw2 = norm_t2.get(wf)

        if not raw1 or not raw2:
            print("   ❌ Workflow text missing in one instance")
            transition_failed = True
            continue

        s1 = parse_workflow_transitions(raw1)
        s2 = parse_workflow_transitions(raw2)

        if s1 == s2:
            print("   ✅ Workflow transitions are semantically identical")
            continue

        transition_failed = True
        print("   ❌ Workflow transition mismatch detected")

        missing = s1 - s2
        extra = s2 - s1

        if missing:
            print("   ➖ Missing in INSTANCE_2:")
            for f, t, screen, to in sorted(missing):
                print(f"      FROM [{f}]")
                print(f"        TRANSITION : {t}")
                print(f"        SCREEN     : {screen}")
                print(f"        TO         : {to}")

        if extra:
            print("   ➕ Extra in INSTANCE_2:")
            for f, t, screen, to in sorted(extra):
                print(f"      FROM [{f}]")
                print(f"        TRANSITION : {t}")
                print(f"        SCREEN     : {screen}")
                print(f"        TO         : {to}")

        print()

    # =================================================
    # FINAL ASSERTIONS
    # =================================================
    assert not scheme_failed, "Workflow scheme validation failed"
    assert not workflow_failed, "Workflow validation failed"
    assert not issuetype_failed, "Issue type validation failed"
    assert not transition_failed, "Transition validation failed"
