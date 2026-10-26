# OT-SOC Agents

OT-aware multi-agent SOC assistant for Modbus alert triage (FC305 project).

## Setup
1. Install uv: https://docs.astral.sh/uv/
2. `uv sync`
3. Copy `.env.example` to `.env` and add your API key.
4. `uv run python -m core.smoke_test`