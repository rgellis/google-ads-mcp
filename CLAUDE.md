## Objective

MCP server wrapping the entire Google Ads API v23 for LLM interaction. Built on the official Python SDK (`google-ads==30.0.0`) with FastMCP.

## Architecture

- `main.py` — Entry point, SERVER_GROUPS dict, `--groups` CLI flag
- `src/servers/` — 12 domain modules (core, assets, targeting, bidding, etc.) using `create_server()` factory
- `src/services/` — 113 service files organized by domain (account, ad_group, assets, campaign, etc.)
- `src/utils.py` — `format_customer_id`, `serialize_proto_message`, `set_request_options`
- `src/sdk_client.py` — Google Ads SDK client wrapper with lazy initialization
- `tests/` — 113 test files, one per service, 991+ tests

## Rules

1. Use `uv` for package management. See `pyproject.toml`.
2. After changes run `uv run ruff format .` and `uv run pyright`.
3. Every service method must have a test. Run `uv run pytest` to verify.
4. All code uses v23 imports — never reference v20/v21/v22.
5. Tool wrapper docstrings are the LLM-facing interface — they must document valid enum values, campaign type restrictions, and targeting level constraints.

## Service Pattern

Every service follows this structure:

```python
class FooService:
    # Lazy client via @property
    # Async methods with try/except GoogleAdsException + Exception
    # Returns serialize_proto_message(response)

def create_foo_tools(service):
    # String enum params → SDK enums via getattr()
    # Docstrings = what the LLM reads to select and use the tool

def register_foo_tools(mcp):
    # Instantiate service, register tools
```

## Critical Rules

- **Never set proto fields to default values explicitly** — `criterion.negative = False` marks the field as "set" on the wire. Google's API rejects fields that shouldn't be present even if the value is the default. Let proto defaults work implicitly.
- **Campaign-level demographics on Search are exclusion-only** — bid adjustments must be done at ad group level.
- **custom_audience/custom_affinity** only work on Display, Demand Gen, and Video campaigns.

## Resources

- `./refs/googleads.llms.txt` — Google Ads API resource links
- `./refs/fastmcp.llms.txt` — FastMCP documentation
- `google-ads-python/` — SDK source code with proto-generated types
- `AGENTS.md` — Full agent guide for both codebase contributors and MCP tool users

## Commands

```bash
uv run main.py                    # Run server (core group only)
uv run main.py --groups all       # All 113 servers
uv run pytest                     # 991+ tests
uv run pyright                    # Type check (0 errors)
uv run ruff format .              # Format
```
