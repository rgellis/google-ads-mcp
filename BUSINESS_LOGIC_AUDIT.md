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

### Verified (services 91-111 + wrappers)

| # | Service | Verdict |
|---|---------|---------|
| 91 | shareable_preview | CORRECT |
| 92 | search (wrapper) | CORRECT |
| 93 | label | ISSUE (output-only `status` set on create/update) |
| 94 | shared_set | ISSUE (output-only `status` set on create/update) |
| 95 | shared_criterion | ISSUE (output-only `type_` set — inferred from oneof) |
| 96 | customizer_attribute | CORRECT |
| 97 | benchmarks | ISSUE (missing required `product_filter` field) |
| 98 | brand_suggestion | ISSUE (missing format_customer_id) |
| 99 | keyword_plan | CORRECT |
| 100 | keyword_plan_ad_group | ISSUE (missing format_customer_id) |
| 101 | keyword_plan_ad_group_keyword | ISSUE (missing format_customer_id) |
| 102 | keyword_plan_campaign | ISSUE (missing format_customer_id) |
| 103 | keyword_plan_campaign_keyword | ISSUE (missing format_customer_id) |
| 104 | keyword_plan_idea | ISSUE (format_customer_id missing in 4 of 7 methods) |
| 105 | keyword_theme_constant | CORRECT |
| 106 | reach_plan | ISSUE (dead LocationInfo var, deprecated plannable_location_id) |
| 107 | recommendation | ISSUE (GAQL uses removed `sitelink_extension_recommendation`, `ad_group_info` not forwarded) |
| 108 | recommendation_subscription | CORRECT |
| 109 | travel_asset_suggestion | CORRECT |
| 110 | product_link | ISSUE (missing format_customer_id) |
| 111 | product_link_invitation | ISSUE (create sends empty invitation — no link target) |
| + | third_party_app_analytics_link | CORRECT |
| + | keyword (wrapper) | CORRECT |
| + | budget (wrapper) | CORRECT |

### Verified (campaigns, conversions, data, experiments, metadata — services 57-90)

| # | Service | Verdict |
|---|---------|---------|
| 57 | campaign | ISSUE (output-only `experiment_type` set on create) |
| 58 | campaign_asset | ISSUE (enum object in resource name string instead of `.name`) |
| 59 | campaign_asset_set | ISSUE (missing format_customer_id) |
| 60 | campaign_bid_modifier | CORRECT |
| 61 | campaign_conversion_goal | CORRECT |
| 62 | campaign_criterion | CORRECT |
| 63 | campaign_customizer | CORRECT |
| 64 | campaign_draft | CORRECT |
| 65 | campaign_goal_config | ISSUE (immutable fields set on update; wrong resource name on remove) |
| 66 | campaign_group | CORRECT |
| 67 | campaign_label | CORRECT |
| 68 | campaign_lifecycle_goal | ISSUE (output-only `campaign` field set) |
| 69 | campaign_shared_set | CORRECT |
| 70 | reservation | CORRECT |
| 71 | smart_campaign_setting | CORRECT |
| 72 | smart_campaign (suggest) | ISSUE (invalid `keyword_seed` field; wrong fields on budget options request) |
| 73 | conversion (action) | ISSUE (output-only `data_driven_model_status` set on create) |
| 74 | conversion_adjustment_upload | CORRECT |
| 75 | conversion_custom_variable | CORRECT |
| 76 | conversion_goal_campaign_config | ISSUE (missing format_customer_id) |
| 77 | conversion_upload | CORRECT |
| 78 | conversion_value_rule | CORRECT |
| 79 | conversion_value_rule_set | CORRECT |
| 80 | custom_conversion_goal | ISSUE (missing format_customer_id) |
| 81 | customer_conversion_goal | CORRECT |
| 82 | batch_job | CORRECT |
| 83 | data_link | CORRECT |
| 84 | local_services_lead | CORRECT |
| 85 | offline_user_data_job | ISSUE (wrong param semantics for `user_list`; `get` returns wrong object) |
| 86 | user_data | CORRECT |
| 87 | experiment | CORRECT |
| 88 | experiment_arm | ISSUE (missing format_customer_id) |
| 89 | google_ads | CORRECT |
| 90 | google_ads_field | CORRECT |

---

## Checklist for Full Coverage

### Per-service optional field gaps

For 100% API field coverage, every mutate service's tool wrapper should expose:

- [ ] `partial_failure` parameter (where SDK supports it)
- [ ] `validate_only` parameter (where SDK supports it)
- [ ] `response_content_type` parameter (where SDK supports it)

### Specific service fixes needed

- [x] Fix `billing_setup.create_billing_setup` — remove `end_date_time` and `end_time_type` parameters (output-only fields) **DONE**
- [x] Fix `customer_lifecycle_goal` — correct resource name to singular `customerLifecycleGoal` **DONE**
- [x] Fix `customer_sk_ad_network` — apply `schema` dict fields to proto object **DONE**
- [x] Fix `ad_group_asset_set` — GAQL `asset_set.type_` → `asset_set.type` **DONE**
- [x] Fix `ad_group_criterion_label` — add `format_customer_id()` call **DONE**
- [x] Fix `ad_group_customizer` — add `format_customer_id()` call **DONE**
- [x] Fix `asset_group_signal` — add `format_customer_id()` call **DONE**
- [x] Fix `customer_asset` — add `format_customer_id()` call **DONE**
- [x] Fix `automatically_created_asset_removal` — set required `partial_failure` field **DONE**
- [x] Fix `label` — removed output-only `status` from create/update **DONE**
- [x] Fix `shared_set` — removed output-only `status` from create/update **DONE**
- [x] Fix `shared_criterion` — removed output-only `type_` assignment **DONE**
- [x] Fix `brand_suggestion` — added `format_customer_id()` **DONE**
- [x] Fix `keyword_plan_ad_group` — added `format_customer_id()` **DONE**
- [x] Fix `keyword_plan_ad_group_keyword` — added `format_customer_id()` **DONE**
- [x] Fix `keyword_plan_campaign` — added `format_customer_id()` **DONE**
- [x] Fix `keyword_plan_campaign_keyword` — added `format_customer_id()` **DONE**
- [x] Fix `keyword_plan_idea` — added `format_customer_id()` to 4 methods **DONE**
- [x] Fix `reach_plan` — removed dead LocationInfo var **DONE**
- [x] Fix `recommendation` — GAQL `sitelink_extension_recommendation` → `sitelink_asset_recommendation` **DONE**
- [x] Fix `product_link` — added `format_customer_id()` **DONE**
- [x] Fix `product_link_invitation` — added link target params to create **DONE**
- [x] Fix `campaign` — removed output-only `experiment_type` on create **DONE**
- [x] Fix `campaign_asset_set` — added `format_customer_id()` **DONE**
- [x] Fix `campaign_goal_config` — fixed immutable fields on update; fixed remove resource name **DONE**
- [x] Fix `campaign_lifecycle_goal` — removed output-only `campaign` field **DONE**
- [x] Fix `smart_campaign` — removed invalid `keyword_seed`; fixed budget options fields **DONE**
- [x] Fix `conversion` (action) — removed output-only `data_driven_model_status` **DONE**
- [x] Fix `conversion_goal_campaign_config` — added `format_customer_id()` **DONE**
- [x] Fix `custom_conversion_goal` — added `format_customer_id()` **DONE**
- [x] Fix `experiment_arm` — added `format_customer_id()` **DONE**
- [ ] Add `partial_failure`, `validate_only`, `response_content_type` params to all mutate tool wrappers
