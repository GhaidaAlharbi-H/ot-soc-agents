import json
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "mcp_servers"
ASSETS_PATH = DATA / "assets.json"
BASELINE_PATH = DATA / "baseline.json"

def get_asset(ip: str) -> str:
    """Return the device record for an IP as JSON text, or an error message."""
    assets = json.loads(ASSETS_PATH.read_text(encoding="utf-8"))
    if ip not in assets:
        return json.dumps({"error": f"unknown device {ip}", "known_ips": list(assets)})
    return json.dumps({"ip": ip, **assets[ip]})

def get_baseline(src_ip: str, dst_ip: str) -> str:
    """Return normal Modbus behaviour between two devices, measured from benign traffic."""
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    key = f"{src_ip}->{dst_ip}"
    if key not in baseline:
        return json.dumps({
            "pair": key,
            "baseline": None,
            "meaning": "These devices never exchange Modbus traffic in normal operation.",
            "known_pairs": [k for k in baseline if not k.startswith("_")],
        })
    return json.dumps({"pair": key, "source": baseline["_source"], **baseline[key]})

GET_ASSET_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_asset",
        "description": (
            "Look up a substation device by IP address. Returns its role, observed facts "
            "(register map, links) and assumed facts (criticality, allowed and forbidden "
            "response actions)."
        ),
        "parameters": {
            "type": "object",
            "properties": {"ip": {"type": "string", "description": "IPv4 address, e.g. 185.175.0.5"}},
            "required": ["ip"],
            "additionalProperties": False,
        },
    },
}

GET_BASELINE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_baseline",
        "description": (
            "Get normal Modbus behaviour from a client to a server, measured from benign "
            "traffic: poll interval, normal writes per hour and their addresses, read sizes, "
            "exception replies."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "src_ip": {"type": "string", "description": "Client (requester) IP"},
                "dst_ip": {"type": "string", "description": "Server (IED) IP"},
            },
            "required": ["src_ip", "dst_ip"],
            "additionalProperties": False,
        },
    },
}

TOOL_SCHEMAS = [GET_ASSET_SCHEMA, GET_BASELINE_SCHEMA]
TOOLS = {"get_asset": get_asset, "get_baseline": get_baseline}