# Agent Guide

## Part 1: For AI Agents Working on This Codebase

### What this project is

An MCP server wrapping the entire Google Ads API v23 for LLM interaction. Built on the official Python SDK (`google-ads==30.0.0`) with FastMCP. Every tool parameter is a simple string/number (not proto types) so LLMs can use them via chat or voice.

### Architecture

```
main.py                    → Entry point, SERVER_GROUPS, --groups CLI flag
src/servers/               → 12 domain modules creating FastMCP instances
src/services/              → 113 service files (one per API service)
src/services/{domain}/     → Service class + create_*_tools() + register_*_tools()
tests/                     → 113 test files (one per service)
src/utils.py               → format_customer_id, serialize_proto_message, set_request_options
src/sdk_client.py          → Google Ads SDK client wrapper
```

### Service file pattern

Every service follows this structure:

```python
class FooService:
    # Lazy SDK client initialization via @property
    # Async methods with try/except GoogleAdsException + generic Exception
    # Returns serialize_proto_message(response)

def create_foo_tools(service):
    # Thin wrappers converting string enums → SDK enums via getattr()
    # Docstrings are what the LLM sees — must include valid enum values,
    # campaign type restrictions, and targeting level constraints

def register_foo_tools(mcp):
    # Creates service, registers tools with FastMCP
```

### Key patterns to follow

- **String enums in tool wrappers**: The service class takes SDK enum types. The tool wrapper takes strings and converts via `getattr(EnumClass.EnumType, string_value)`.
- **No hardcoded proto defaults**: Never set a proto field to its default value explicitly (e.g. `criterion.negative = False`). Proto-plus marks explicitly-set fields as present on the wire, and Google's API may reject fields that shouldn't be "set" even if the value is the default.
- **Error handling**: Every service method that calls the API directly must have `try/except GoogleAdsException` then `except Exception`. Delegation methods (that call another service method) don't need their own try/except.
- **Success logging**: Every API call must log via `await ctx.log(level="info", message="...")` on success.
- **Tests**: Every public service method must have a test. Tests mock the SDK client and patch `serialize_proto_message`.

### Commands

```bash
uv run main.py                    # Run server (core group)
uv run main.py --groups all       # Run with all services
uv run pytest                     # Run tests
uv run pyright                    # Type check
uv run ruff format .              # Format code
```

### What NOT to do

- Don't set proto fields to default values unconditionally (see "No hardcoded proto defaults" above)
- Don't create a tool without a corresponding test
- Don't add a tool to a service without adding it to the `tools.extend()` list
- Don't add imports at the top level if they're only needed conditionally (use inline imports in method bodies for rare enum types)
- Don't reference v20 — everything is v23

---

## Part 2: For LLM Agents Using This MCP Server

### Key targeting rules

These rules prevent the most common API errors when managing Google Ads campaigns.

#### Search campaign demographics

Campaign-level demographics on Search campaigns are **exclusion-only**. You cannot set bid modifiers on them.

- To **exclude** an age range/gender/income range: Use `camp_criterion_add_age_range_criteria` etc. (negative only, no bid_modifier)
- To **adjust bids** by demographic: Use `ag_criterion_add_demographic_criteria` at the **ad group level**

#### Audience targeting on Search campaigns

`custom_audience` and `custom_affinity` criteria only work on **Display, Demand Gen, and Video** campaigns.

For Search campaigns, use:
- `camp_criterion_add_audience_criteria` (user lists / RLSA)
- `camp_criterion_add_user_interest_criteria` (in-market / affinity segments)
- `ag_criterion_add_audience_criteria` (ad group level)

#### Campaign-level only criteria

These can ONLY be set at the campaign level (not ad group):
- Ad schedule, device, carrier, mobile device, operating system version
- Proximity, location group, listing scope, extended demographic
- Video lineup, keyword theme, life event, local service ID, IP block

#### Ad group-level only criteria

These can ONLY be set at the ad group level:
- Listing group (product groups), app payment model
- Keywords (positive — campaign level is negative only)

#### Positive vs negative targeting

Some criteria only support one direction:
- **Positive only** (cannot exclude): ad schedule, device, language, carrier, proximity, combined audience, custom audience, custom affinity
- **Negative only** (cannot target positively): content label, placement (at campaign level), IP block

#### Bid modifiers

`bid_modifier` is a multiplier on the base bid:
- `1.0` = no change
- `1.5` = +50%
- `0.5` = -50%
- `0.0` = exclude (functionally removes the demographic/criterion)

#### Campaign removal

To remove a campaign, use `campaign_remove_campaign`. Setting `status = REMOVED` via update does NOT work — the API requires a remove operation.

#### Network settings

When creating a Search campaign, `target_search_network` and `target_content_network` default to `false`. Set them explicitly if you want ads to show on search partner sites or the Display Network.

### Ad types by campaign type

| Campaign Type | Supported Ad Types |
|--------------|-------------------|
| Search | responsive_search_ad |
| Display | responsive_display_ad, image_ad, display_upload_ad |
| Video | video_ad (in_stream, bumper, non_skippable, in_feed), video_responsive_ad |
| Demand Gen | demand_gen_multi_asset_ad, demand_gen_carousel_ad, demand_gen_video_responsive_ad, demand_gen_product_ad |
| Shopping | shopping_product_ad, shopping_comparison_listing_ad |
| App | app_ad, app_engagement_ad, app_pre_registration_ad |
| Smart | smart_campaign_ad |
| Hotel | hotel_ad |
| Travel | travel_ad |
| Local | local_ad |
| PMax | Uses asset groups, not traditional ads |

### Deprecated types (do not use)

| Type | Replacement |
|------|-------------|
| text_ad | responsive_search_ad |
| legacy_responsive_display_ad | responsive_display_ad |
| legacy_app_install_ad | app_ad |
| shopping_smart_ad | Performance Max |
| custom_intent | custom_audience |
