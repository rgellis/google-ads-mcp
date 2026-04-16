# Business Logic Audit

Comprehensive audit of every service's business logic against the Google Ads API v23 proto specs.
Checks: required fields, field types, optional field exposure, correct enum usage, resource name formats.

**Started:** 2026-04-15
**Status:** In progress

---

## Systemic Gap: Optional Request Fields

Almost all mutate services have 3 optional request fields that the SDK supports but our MCP tool wrappers don't expose:

| Field | Type | Purpose | Services affected |
|-------|------|---------|-------------------|
| `partial_failure` | bool | Allow valid operations to succeed even if others fail | ~70 services |
| `validate_only` | bool | Validate request without executing | ~70 services |
| `response_content_type` | enum | Control what to return in response (RESOURCE_NAME_ONLY vs MUTABLE_RESOURCE) | ~60 services |

**Recommendation:** Add these as optional parameters to all mutate tool wrappers with sensible defaults (`partial_failure=False`, `validate_only=False`, `response_content_type=RESOURCE_NAME_ONLY`).

---

## Service-Level Issues Found

### Actual Bugs (would cause API failures or wrong behavior)

| # | Service | Issue | Severity |
|---|---------|-------|----------|
| 1 | `billing_setup` | `create_billing_setup` sets output-only fields `end_date_time` and `end_time_type` — API will reject or ignore | Medium |
| 2 | `customer_lifecycle_goal` | Update path uses wrong resource name format `customerLifecycleGoals` (plural) — should be `customerLifecycleGoal` (singular). Also empty `update_mask` means no fields get updated | High |
| 3 | `customer_sk_ad_network` | The `schema: Dict[str, Any]` parameter is accepted but never applied to the proto object — caller's data is silently dropped | High |

| 4 | `ad_group_asset_set` | GAQL query uses `asset_set.type_` — invalid GAQL field name, must be `asset_set.type` | Medium |
| 5 | `ad_group_criterion_label` | `format_customer_id()` not called — raw customer_id with dashes will fail | Medium |
| 6 | `ad_group_customizer` | `format_customer_id()` not called — raw customer_id with dashes will fail | Medium |
| 7 | `asset_group_signal` | `format_customer_id()` not called in service methods | Medium |
| 8 | `customer_asset` | `format_customer_id()` not called in service methods | Medium |
| 9 | `automatically_created_asset_removal` | Required field `partial_failure` never set on request | Medium |

### Verified Correct (account services 1-17)

| # | Service | Verdict |
|---|---------|---------|
| 1 | account_budget_proposal | CORRECT |
| 2 | account_link | CORRECT |
| 3 | billing_setup | ISSUE (see above) |
| 4 | customer | CORRECT |
| 5 | customer_client_link | CORRECT |
| 6 | customer_customizer | CORRECT |
| 7 | customer_label | CORRECT |
| 8 | customer_lifecycle_goal | ISSUE (see above) |
| 9 | customer_manager_link | CORRECT |
| 10 | customer_sk_ad_network | ISSUE (see above) |
| 11 | customer_user_access | CORRECT |
| 12 | customer_user_access_invitation | CORRECT |
| 13 | goal | CORRECT |
| 14 | identity_verification | CORRECT |
| 15 | incentive | CORRECT |
| 16 | invoice | CORRECT |
| 17 | payments_account | CORRECT |

### Verified (ad group, ads, assets, audiences, bidding — services 18-56)

| # | Service | Verdict |
|---|---------|---------|
| 18 | ad | CORRECT |
| 19 | ad_group | CORRECT |
| 20 | ad_group_ad | CORRECT |
| 21 | ad_group_ad_label | CORRECT |
| 22 | ad_group_asset | CORRECT |
| 23 | ad_group_asset_set | ISSUE (GAQL `type_` bug) |
| 24 | ad_group_bid_modifier | CORRECT |
| 25 | ad_group_criterion | CORRECT |
| 26 | ad_group_criterion_customizer | CORRECT |
| 27 | ad_group_criterion_label | ISSUE (missing format_customer_id) |
| 28 | ad_group_customizer | ISSUE (missing format_customer_id) |
| 29 | ad_group_label | CORRECT |
| 30 | ad_parameter | CORRECT |
| 31 | asset | CORRECT |
| 32 | asset_generation | CORRECT |
| 33 | asset_group | CORRECT |
| 34 | asset_group_asset | CORRECT |
| 35 | asset_group_listing_group_filter | CORRECT |
| 36 | asset_group_signal | ISSUE (missing format_customer_id) |
| 37 | asset_set | CORRECT |
| 38 | asset_set_asset | CORRECT |
| 39 | automatically_created_asset_removal | ISSUE (required partial_failure not set) |
| 40 | customer_asset | ISSUE (missing format_customer_id) |
| 41 | customer_asset_set | CORRECT |
| 42 | youtube_video_upload | CORRECT |
| 43 | audience | CORRECT |
| 44 | audience_insights | CORRECT |
| 45 | content_creator_insights | CORRECT |
| 46 | custom_audience | CORRECT |
| 47 | custom_interest | CORRECT |
| 48 | customer_negative_criterion | CORRECT |
| 49 | geo_target_constant | CORRECT |
| 50 | remarketing_action | CORRECT |
| 51 | user_list | CORRECT |
| 52 | user_list_customer_type | CORRECT |
| 53 | bidding_data_exclusion | CORRECT |
| 54 | bidding_seasonality_adjustment | CORRECT |
| 55 | bidding_strategy | CORRECT |
| 56 | campaign_budget (budget) | CORRECT |

### Remaining services (57-111) — audit in progress

*To be completed*

---

## Checklist for Full Coverage

### Per-service optional field gaps

For 100% API field coverage, every mutate service's tool wrapper should expose:

- [ ] `partial_failure` parameter (where SDK supports it)
- [ ] `validate_only` parameter (where SDK supports it)
- [ ] `response_content_type` parameter (where SDK supports it)

### Specific service fixes needed

- [x] Fix `billing_setup.create_billing_setup` — remove `end_date_time` and `end_time_type` parameters (output-only fields) **DONE**
- [ ] Fix `customer_lifecycle_goal` — correct resource name format to singular `customerLifecycleGoal`; populate `update_mask` fields
- [ ] Fix `customer_sk_ad_network` — actually apply the `schema` dict to the proto object
- [ ] Fix `ad_group_asset_set` — GAQL query `asset_set.type_` should be `asset_set.type`
- [ ] Fix `ad_group_criterion_label` — add `format_customer_id()` call
- [ ] Fix `ad_group_customizer` — add `format_customer_id()` call
- [ ] Fix `asset_group_signal` — add `format_customer_id()` call
- [ ] Fix `customer_asset` — add `format_customer_id()` call
- [ ] Fix `automatically_created_asset_removal` — set required `partial_failure` field on request
- [ ] Add `partial_failure`, `validate_only`, `response_content_type` params to all mutate tool wrappers
- [ ] Audit services 57-111 for similar issues (in progress)
