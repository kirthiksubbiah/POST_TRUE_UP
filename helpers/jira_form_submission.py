import requests
import urllib3
from requests.auth import HTTPBasicAuth
from config.config import CONFIG

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# =================================================
# DISCOVER REST FIELDS
# =================================================
def discover_rest_fields(instance_key, service_desk_id, request_type_id):
    cfg = CONFIG[instance_key]

    url = (
        f"{cfg['base_url']}/rest/servicedeskapi/servicedesk/"
        f"{service_desk_id}/requesttype/{request_type_id}/field"
    )

    resp = requests.get(
        url,
        auth=HTTPBasicAuth(cfg["email"], cfg["api_token"]),
        headers={"Accept": "application/json"},
        verify=False,
    )

    resp.raise_for_status()

    return {
        f["fieldId"]: {
            "name": f["name"],
            "required": f["required"],
            "schema": f.get("schema", {}),
        }
        for f in resp.json().get("requestTypeFields", [])
    }


# =================================================
# BUILD PAYLOAD (APPROVERS MUST BE SKIPPED)
# =================================================
def build_payload_fields(rest_fields, request_type_name):
    payload = {}

    for field_id, meta in rest_fields.items():
        name = meta["name"].lower()
        schema = meta.get("schema", {})
        field_type = schema.get("type")

        # Skip all user / approver / array fields
        if field_type in {"array", "user", "option"}:
            continue

        if not meta["required"]:
            continue

        # ---- TEXT / RICH TEXT ----
        if any(k in name for k in ["summary", "why", "describe", "details"]):
            payload[field_id] = f"Auto-generated for {request_type_name}"

        # ---- SAFE FALLBACK ----
        else:
            payload[field_id] = "Auto-generated"

    return payload


# =================================================
# CREATE REQUEST
# =================================================
def create_request(
    instance_key: str,
    service_desk_id: str,
    request_type_id: str,
    request_type_name: str,
):
    cfg = CONFIG[instance_key]

    rest_fields = discover_rest_fields(
        instance_key,
        service_desk_id,
        request_type_id,
    )

    payload = {
        "serviceDeskId": service_desk_id,
        "requestTypeId": request_type_id,
        "requestFieldValues": build_payload_fields(
            rest_fields,
            request_type_name,
        ),
    }

    resp = requests.post(
        f"{cfg['base_url']}/rest/servicedeskapi/request",
        json=payload,
        auth=HTTPBasicAuth(cfg["email"], cfg["api_token"]),
        headers={"Accept": "application/json"},
        verify=False,
    )

    if resp.status_code != 201:
        raise RuntimeError(
            f"Request creation failed "
            f"(status={resp.status_code}): {resp.text}"
        )

    return {
        "status_code": resp.status_code,
        "body": resp.json(),
    }
