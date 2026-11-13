import json
from pathlib import Path

ASSETS_PATH = Path(__file__).resolve().parent.parent / "mcp_servers" / "assets.json"

def get_asset(ip: str) -> str:
    """Return the device record for an IP as JSON text, or an error message."""
    assets = json.loads(ASSETS_PATH.read_text(encoding="utf-8"))
    if ip not in assets:
        return json.dumps({"error": f"unknown device {ip}", "known_ips": list(assets)})
    return json.dumps({"ip": ip, **assets[ip]})

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
            "properties": {
                "ip": {"type": "string", "description": "IPv4 address, e.g. 185.175.0.5"}
            },
            "required": ["ip"],
            "additionalProperties": False,
        },
    },
}

TOOLS = {"get_asset": get_asset}