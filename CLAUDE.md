## Objective

MCP server wrapping the entire Google Ads API v23 for LLM interaction. Built on the official Python SDK (`google-ads==30.0.0`) with FastMCP.

## Architecture

- `main.py` — Entry point, SERVER_GROUPS dict, `--groups` CLI flag
- `src/servers/` — 12 domain modules (core, assets, targeting, bidding, etc.) using `create_server()` factory
- `src/services/` — 113 service files organized by domain (account, ad_group, assets, campaign, etc.)
- `src/utils.py` — `format_customer_id`, `serialize_proto_message`, `set_request_options`, GAQL helpers (`gaql_int`, `gaql_enum_name`, `gaql_resource_field`, `gaql_string_literal`)
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

## GAQL safety and tool surface

- **Structured tools take only universal filters** (status, type, ID, limit). Anything else — substring-on-name, date ranges, metric thresholds, custom SELECT/ORDER BY, multi-condition AND/OR — goes through `search_google_ads` (the free-form GAQL passthrough). Don't add `name_contains` / `start_date` / similar one-off params to structured list endpoints.
- **`list_*` / `search_*` tool wrapper docstrings** must include the standard GAQL escape-hatch hint that points the LLM to `search_google_ads`. See any service for the canonical wording (e.g. `metadata/search_service.py`).
- **Use the GAQL helpers in `src/utils.py`** when interpolating user input into a GAQL string:
  - `gaql_int(value, field_name)` — IDs and `LIMIT` (~32 sites).
  - `gaql_enum_name(value, field_name)` — status / type / scope filters; validates `[A-Z][A-Z0-9_]*`.
  - `gaql_resource_field(value, field_name)` — resource/field names; validates `[a-z][a-z0-9_]*`.
  - `gaql_string_literal(value, field_name)` — freeform user content (names, ad text). Escapes `\\` and `'`, rejects control chars, returns the value already wrapped in single quotes.
- **`format_customer_id` is hardened**: it strips hyphens and validates the result is exactly 10 digits, rejecting non-string input. A normalized `customer_id` is therefore safe to interpolate into GAQL string literals, resource paths, or proto fields without further escaping.

## Output-only proto annotations are not always trustworthy

The v23 protos sometimes annotate `Output only` fields that the API genuinely needs on create or update. Don't blindly delete a write because the docstring says "Output only" — verify it's actually output-only first. Use this checklist before flagging an Output-only write as a bug:

**Output-only is legitimate when ANY of these is true:**
1. The field is **derived from a sibling oneof**. Setting type_/status manually is redundant because the API computes it from which oneof member is set. Examples: `Asset.type_` (derived from asset_data oneof), `BiddingStrategy.type_` (from scheme oneof), `CustomerNegativeCriterion.type_` (from criterion oneof), `AccountLink.type_` (from linked_account oneof).
2. The field is a **status enum with only ENABLED/REMOVED**, and REMOVED is achieved via a separate `remove` operation, not by setting `status=REMOVED`. ENABLED is the implicit default. Examples: `Audience.status`, `CustomAudience.status`, `AssetSet.status`, `CampaignSharedSet.status`, `BiddingStrategy.status`, etc. (All have just ENABLED/REMOVED — no PAUSED transition for users to drive.)
3. The field is **truly server-controlled** — IDs, approval statuses, computed timestamps, policy review outputs, etc.

**Output-only is a proto-annotation BUG when ANY of these is true:**
1. The field is the **only oneof member carrying user payload** for that resource type. Sibling oneof members on the same resource are Immutable or unannotated (settable). Examples: `Asset.image_asset`, `Asset.location_asset` (every other asset_data oneof member is settable), `ProductLinkInvitation.merchant_center` / `.hotel_center` (compare `ProductLink` where the same identifier types are Immutable).
2. The field is the **only way to convey identity/association on create**, and there's no alternative path (no temp-ID resource_name, no implicit context). Example: `CampaignBidModifier.campaign` — without it, the API has no way to know which campaign owns the modifier; the official Google SDK examples set it directly despite the annotation.
3. The **operation proto's docstring contradicts the field annotations**. Example: `CustomerSkAdNetworkConversionValueSchemaOperation` says "Update operation: The schema is expected to have a valid resource name" but every schema field is annotated Output-only — impossible if literal.

**When in doubt, do this verification before deleting:**
1. Look at sibling oneof members on the same resource — are they all flagged the same way, or is the field uniquely Output-only? Uniquely-flagged is suspicious.
2. Look for a sister proto in the same domain — is the analogous field annotated Immutable there? (e.g., `ProductLink` vs `ProductLinkInvitation`)
3. Check the resource's status enum values — is ENABLED/REMOVED the full set, or are there user-driven transitions?
4. Read the operation/request proto docstrings — do they imply the field must be settable?
5. Search for the field in `examples/` under `google-ads-python` for the official usage pattern.

If you keep an Output-only write because the annotation is a bug, add a short inline comment explaining the proto-annotation-bug reasoning so future readers (and audits) don't re-flag it.

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
