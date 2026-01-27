import sys
import subprocess

# =====================================================
# MODULE GROUPS
# =====================================================
NON_GLOBAL_MODULES = [
    "request_type_link_validation",
    "display_name_field_validation",
    "custom_jira_field_validation",
    "request_type_form_submission",
    "jira_workflow_validation",
]

GLOBAL_MODULES = [
    "global_custom_jira_field_validation",
    "global_workflow_validation",
    "global_workflow_scheme_validation",
    "global_status_validation",
]

# =====================================================
# HELP
# =====================================================
HELP = """

post_true_up_process - Custom CLI Tool
 
Usage:

  python post_true_up_process.py <module> [arguments]

  python post_true_up_process.py -h | --help
 
Modules:

  request_type_link_validation      Validate the number of Links present in Env1 and Env2 (Match/Mismatch)

  display_name_field_validation     Validate the number of Fields present in each Form in Env1 and Env2 (Match/Mismatch)

  custom_jira_field_validation      Validate the number of Custom Fields present in each Form in Env1 and Env2 (Match/Mismatch)

  request_type_form_submission      Validate the Form Submission (Success/Failure)

  jira_workflow_validation          Validate the Workflow (Functional/Broken)

  global_custom_jira_field_validation   Validate migrated custom fields 

  global_workflow_validation            Validate migrated workflows 

  global_workflow_scheme_validation     Validate migrated workflow schemes 

  global_status_validation              Validate migrated statuses 

Login Scripts (Run directly):

  python login/instance_1_login.py   Login to Instance 1 and generate session data

  python login/instance_2_login.py   Login to Instance 2 and generate session data
 
Use "python post_true_up_process.py <module> -h" for more help on a module.

Use "python post_true_up_process.py run_all" for space level validation

Use "python post_true_up_process.py run_all_global --migrated-date <"DD Mon YYYY">" for global level validation

"""
 
MODULE_HELP = {

    'request_type_link_validation':
        """

request_type_link_validation.py - Validate the number of Links present in Env1 and Env2 (Match/Mismatch)
 
Usage:

  python post_true_up_process.py request_type_link_validation
 
Arguments:

(No arguments required)

""",

    'display_name_field_validation':
        """

display_name_field_validation.py - Validate the number of Fields present in each Form in Env1 and Env2 (Match/Mismatch)
 
Usage:

  python post_true_up_process.py display_name_field_validation
 
Arguments:

(No arguments required)

""",

    'custom_jira_field_validation':
        """

custom_jira_field_validation.py - Validate the number of Custom Fields present in each Form in Env1 and Env2 (Match/Mismatch)
 
Usage:

  python post_true_up_process.py custom_jira_field_validation
 
Arguments:

(No arguments required)

""",

    'request_type_form_submission':
        """

request_type_form_submission.py - Validate the Form Submission (Success/Failure)
 
Usage:

  python post_true_up_process.py request_type_form_submission
 
Arguments:

(No arguments required)

""",

    'jira_workflow_validation':
        """

jira_workflow_validation.py - Validate the Workflow (Functional/Broken)
 
Usage:

  python post_true_up_process.py jira_workflow_validation
 
Arguments:

(No arguments required)

""",

    'global_custom_jira_field_validation':
        """

global_custom_jira_field_validation.py - Validate migrated global custom fields 
 
Usage:

  python post_true_up_process.py global_custom_jira_field_validation [--migrated-date "16 Jan 2026(DD Mon YYYY)"]

Arguments:

  --migrated-date   Filter by migration date

""",

    'global_workflow_validation':
        """

global_workflow_validation.py - Validate migrated workflows 
 
Usage:

  python post_true_up_process.py global_workflow_validation [--migrated-date "16 Jan 2026"(DD Mon YYYY)]

Arguments:

  --migrated-date   Filter by migration date

""",

    'global_workflow_scheme_validation':
        """

global_workflow_scheme_validation.py - Validate migrated workflow schemes 
 
Usage:

  python post_true_up_process.py global_workflow_scheme_validation [--migrated-date "16 Jan 2026(DD Mon YYYY)"]

Arguments:

  --migrated-date   Filter by migration date

""",

    'global_status_validation':
        """

global_status_validation.py - Validate migrated statuses 
 
Usage:

  python post_true_up_process.py global_status_validation [--migrated-date "16 Jan 2026(DD Mon YYYY)"]

Arguments:

  --migrated-date   Filter by migration date

""",

    'instance_1_login':
        """

instance_1_login.py - Login to Jira Instance 1
 
Usage:

  python login/instance_1_login.py
 
Purpose:

  - Authenticates to Instance 1
  - Generates required session/token data for validations

""",

    'instance_2_login':
        """

instance_2_login.py - Login to Jira Instance 2
 
Usage:

  python login/instance_2_login.py
 
Purpose:

  - Authenticates to Instance 2
  - Generates required session/token data for validations

"""
}

# =====================================================
# MAIN
# =====================================================
def main():
    if len(sys.argv) == 1 or sys.argv[1] in ('-h', '--help'):
        print(HELP)
        return

    module = sys.argv[1]

    # ============================
    # RUN ALL NON-GLOBAL VALIDATIONS
    # ============================
    if module == "run_all":
        for m in NON_GLOBAL_MODULES:
            script = f"{m}.py"
            args = ["pytest", script, "-s", "-v"]
            print(f"\n▶ Running: {' '.join(args)}\n")
            subprocess.run(args)
        return

    # ============================
    # RUN ALL GLOBAL VALIDATIONS
    # ============================
    if module == "run_all_global":
        if "--migrated-date" not in sys.argv:
            print("\nERROR: --migrated-date \"DD Mon YYYY\" is required\n")
            return

        for m in GLOBAL_MODULES:
            script = f"{m}.py"
            args = ["pytest", script, "-s", "-v"] + sys.argv[2:]
            print(f"\n▶ Running: {' '.join(args)}\n")
            subprocess.run(args)
        return

    # ============================
    # SINGLE MODULE EXECUTION
    # ============================
    if module in MODULE_HELP:
        if len(sys.argv) > 2 and sys.argv[2] in ('-h', '--help'):
            print(MODULE_HELP[module])
        else:
            script = f"{module}.py"
            args = ["pytest", script, "-s", "-v"] + sys.argv[2:]
            print(f"\n▶ Running: {' '.join(args)}\n")
            subprocess.run(args)
    else:
        print(f"Unknown module: {module}")
        print(HELP)

# =====================================================
if __name__ == "__main__":
    main()
