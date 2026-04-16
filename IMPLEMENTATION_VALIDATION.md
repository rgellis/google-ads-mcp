# Implementation Validation Report

Deep research of each implemented service against the v23 Google Ads SDK.
Checks: SDK RPC coverage, v20 stale patterns, deprecated types, import correctness, test status.

**Started:** 2026-04-15

**Systemic issue found:** Many test files use `src.sdk_services.*` instead of `src.services.*` in `patch()` targets, causing all mocks to silently no-op.

---

## Account Management Services

### 1. account_budget_proposal
- **SDK RPCs**: `mutate_account_budget_proposal` (1 RPC)
- **Our coverage**: create, update, remove, list (via GAQL) — **FULL**
- **v20 refs**: None
- **Deprecated types**: None
- **Imports**: All v23 correct
- **Tests**: Exist, cover all 4 methods + error handling. **BROKEN**: patch paths use `src.sdk_services.*`
- **Verdict**: **NEEDS_UPDATE** — fix test patch paths

### 2. account_link
- **SDK RPCs**: `create_account_link`, `mutate_account_link` (2 RPCs)
- **Our coverage**: create, update, remove, list (via GAQL) — **FULL**
- **v20 refs**: None
- **Deprecated types**: None
- **Imports**: All v23 correct
- **Tests**: Exist, cover all methods + error handling. **BROKEN**: patch paths use `src.sdk_services.*`
- **Verdict**: **NEEDS_UPDATE** — fix test patch paths

### 3. billing_setup
- **SDK RPCs**: `mutate_billing_setup` (1 RPC, supports create + remove)
- **Our coverage**: create, list, get, list_payments (via GAQL). **Missing**: `remove` operation
- **v20 refs**: None
- **Deprecated types**: None
- **Imports**: All v23 correct
- **Tests**: Exist, cover all implemented methods. **BROKEN**: patch paths use `src.sdk_services.*`
- **Verdict**: **NEEDS_UPDATE** — add remove_billing_setup, fix test patch paths

### 4. customer
- **SDK RPCs**: `create_customer_client`, `list_accessible_customers`, `mutate_customer` (3 RPCs)
- **Our coverage**: create_customer_client, list_accessible_customers. **Missing**: `mutate_customer`
- **v20 refs**: None
- **Deprecated types**: None
- **Dead code**: `list_accessible_customers` has unreachable code after early return (line 123)
- **Tests**: Exist. **BROKEN**: patch paths use `src.sdk_services.*`, test assertions don't match actual return values
- **Verdict**: **NEEDS_UPDATE** — add mutate_customer, fix dead code, fix test patch paths + assertions

### 5. customer_client_link
- **SDK RPCs**: `mutate_customer_client_link` (1 RPC)
- **Our coverage**: create, update, list (via GAQL) — **FULL**
- **v20 refs**: None
- **Deprecated types**: None
- **Tests**: Exist, 8 tests. **BROKEN**: patch paths use `src.sdk_services.*`
- **Verdict**: **NEEDS_UPDATE** — fix test patch paths

### 6. customer_customizer
- **SDK RPCs**: `mutate_customer_customizers` (1 RPC)
- **Our coverage**: create (text/number/price/percent), remove, mutate — **FULL**
- **v20 refs**: Module docstring says "v20" (line 1)
- **Deprecated types**: None
- **Tests**: **MISSING**
- **Verdict**: **NEEDS_UPDATE** — fix docstring, create tests

### 7. customer_label
- **SDK RPCs**: `mutate_customer_labels` (1 RPC)
- **Our coverage**: create, remove — **FULL**
- **v20 refs**: Module docstring says "v20" (line 1)
- **Deprecated types**: None
- **Tests**: Exist, 7 tests, correct patch paths
- **Verdict**: **NEEDS_UPDATE** — fix docstring only

### 8. customer_manager_link
- **SDK RPCs**: `mutate_customer_manager_link`, `move_manager_link` (2 RPCs)
- **Our coverage**: accept, decline, terminate, move, update — **FULL**
- **v20 refs**: Module docstring says "v20" (line 1)
- **Deprecated types**: None
- **Tests**: Exist, 9 tests, correct patch paths
- **Verdict**: **NEEDS_UPDATE** — fix docstring only

### 9. customer_user_access
- **SDK RPCs**: `mutate_customer_user_access` (1 RPC, supports update + remove only)
- **Our coverage**: update, revoke, list (via GAQL) — **FULL**
- **v20 refs**: None
- **Deprecated types**: None
- **Tests**: Exist, 8 tests. **BROKEN**: patch paths use `src.sdk_services.*`
- **Verdict**: **NEEDS_UPDATE** — fix test patch paths

### 10. customer_user_access_invitation
- **SDK RPCs**: `mutate_customer_user_access_invitation` (1 RPC)
- **Our coverage**: create, remove, list (via GAQL) — **FULL**
- **v20 refs**: None
- **Deprecated types**: None
- **Tests**: **MISSING**
- **Verdict**: **NEEDS_UPDATE** — create tests

### 11. identity_verification
- **SDK RPCs**: `start_identity_verification`, `get_identity_verification` (2 RPCs)
- **Our coverage**: start, get — **FULL**
- **v20 refs**: None
- **Deprecated types**: None
- **Tests**: **MISSING**
- **Verdict**: **NEEDS_UPDATE** — create tests

### 12. invoice
- **SDK RPCs**: `list_invoices` (1 RPC)
- **Our coverage**: list — **FULL** (missing optional `include_granular_level_invoice_details` param)
- **v20 refs**: None
- **Deprecated types**: None
- **Tests**: Exist, 7 tests. **BROKEN**: patch paths use `src.sdk_services.*`
- **Verdict**: **NEEDS_UPDATE** — fix test patch paths, add optional param

### 13. payments_account
- **SDK RPCs**: `list_payments_accounts` (1 RPC)
- **Our coverage**: list — **FULL**
- **v20 refs**: None
- **Deprecated types**: None
- **Tests**: **MISSING**
- **Verdict**: **NEEDS_UPDATE** — create tests

---

## Ad Group & Ads Services

### 14. ad
- **SDK RPCs**: `mutate_ads` (1 RPC)
- **Our coverage**: create_responsive_search_ad, create_expanded_text_ad, update_ad_status — uses `AdGroupAdServiceClient` instead of `AdServiceClient`
- **v20 refs**: None
- **Deprecated types**: `ExpandedTextAdInfo` — Google deprecated ETA creation in June 2022; API rejects new ones
- **Architecture issue**: Service wraps `AdGroupAdServiceClient.mutate_ad_group_ads` instead of `AdServiceClient.mutate_ads`
- **Tests**: Exist. **BROKEN**: patch paths use `src.sdk_services.*`
- **Verdict**: **NEEDS_UPDATE** — fix test patch paths; note ETA deprecation; architecture is intentional (ads created via ad_group_ad)

### 15. ad_group
- **SDK RPCs**: `mutate_ad_groups` (1 RPC)
- **Our coverage**: create, update — **FULL**
- **v20 refs**: None
- **Tests**: Exist. **BROKEN**: patch paths use `src.sdk_services.*`
- **Verdict**: **NEEDS_UPDATE** — fix test patch paths only

### 16. ad_group_ad
- **SDK RPCs**: `mutate_ad_group_ads`, `remove_automatically_created_assets` (2 RPCs)
- **Our coverage**: create, update_status, list, remove, remove_automatically_created_assets — **FULL**
- **v20 refs**: None
- **Tests**: Exist but assert tool count = 4 (should be 5 after new method). **BROKEN**: patch paths use `src.sdk_services.*`
- **Verdict**: **NEEDS_UPDATE** — fix test patch paths + update tool count assertion + add test for remove_automatically_created_assets

### 17. ad_group_ad_label
- **SDK RPCs**: `mutate_ad_group_ad_labels` (1 RPC)
- **Our coverage**: create, remove, list (via GAQL) — **FULL**
- **v20 refs**: None
- **Tests**: **MISSING**
- **Verdict**: **NEEDS_UPDATE** — create tests

### 18. ad_group_asset
- **SDK RPCs**: `mutate_ad_group_assets` (1 RPC)
- **Our coverage**: link, link_multiple, list, remove, update_status — **FULL**
- **v20 refs**: None
- **Tests**: Exist. **BROKEN**: patch paths use `src.sdk_services.*`
- **Verdict**: **NEEDS_UPDATE** — fix test patch paths

### 19. ad_group_asset_set
- **SDK RPCs**: `mutate_ad_group_asset_sets` (1 RPC)
- **Our coverage**: create, list, remove — **FULL**
- **v20 refs**: None
- **Bug**: GAQL query uses `asset_set.type_` (should be `asset_set.type`)
- **Tests**: **MISSING**
- **Verdict**: **NEEDS_UPDATE** — fix GAQL bug, create tests

### 20. ad_group_bid_modifier
- **SDK RPCs**: `mutate_ad_group_bid_modifiers` (1 RPC)
- **Our coverage**: create (device/hotel), list, update, remove — **FULL**
- **v20 refs**: None
- **Tests**: Exist. **BROKEN**: patch paths use `src.sdk_services.*`
- **Verdict**: **NEEDS_UPDATE** — fix test patch paths

### 21. ad_group_criterion
- **SDK RPCs**: `mutate_ad_group_criteria` (1 RPC)
- **Our coverage**: add_keywords, add_audience, add_demographic, update_bid, remove — **FULL**
- **v20 refs**: None
- **Bug**: `add_demographic_criteria` missing success log call that test asserts
- **Tests**: Exist. **BROKEN**: patch paths use `src.sdk_services.*`
- **Verdict**: **NEEDS_UPDATE** — fix test patch paths + add missing log call

### 22. ad_group_criterion_customizer
- **SDK RPCs**: `mutate_ad_group_criterion_customizers` (1 RPC)
- **Our coverage**: mutate — **FULL**
- **v20 refs**: None
- **Tests**: Exist. **BROKEN**: patch paths use `src.sdk_services.*`
- **Verdict**: **NEEDS_UPDATE** — fix test patch paths

### 23. ad_group_criterion_label
- **SDK RPCs**: `mutate_ad_group_criterion_labels` (1 RPC)
- **Our coverage**: assign, assign_multiple, remove, mutate — **FULL**
- **v20 refs**: Module docstring says "v20" (line 1)
- **Tests**: Exist, correct patch paths (uses direct mock injection)
- **Verdict**: **NEEDS_UPDATE** — fix docstring only

### 24. ad_group_customizer
- **SDK RPCs**: `mutate_ad_group_customizers` (1 RPC)
- **Our coverage**: create (text/number/price/percent), remove, mutate — **FULL**
- **v20 refs**: Module docstring says "v20" (line 1)
- **Tests**: Exist, correct patch paths (uses direct mock injection)
- **Verdict**: **NEEDS_UPDATE** — fix docstring only

### 25. ad_group_label
- **SDK RPCs**: `mutate_ad_group_labels` (1 RPC)
- **Our coverage**: apply, apply_bulk, list, remove — **FULL**
- **v20 refs**: None
- **Tests**: Exist. **BROKEN**: patch paths use `src.sdk_services.*`
- **Verdict**: **NEEDS_UPDATE** — fix test patch paths

### 26. ad_parameter
- **SDK RPCs**: `mutate_ad_parameters` (1 RPC)
- **Our coverage**: mutate (create/update/remove) — **FULL**
- **v20 refs**: None
- **Tests**: Exist. **BROKEN**: patch paths use `src.sdk_services.*`
- **Verdict**: **NEEDS_UPDATE** — fix test patch paths

### 27. keyword (wrapper)
- **SDK RPCs**: Uses `ad_group_criterion_service.mutate_ad_group_criteria`
- **Our coverage**: add, remove, update_bid — **FULL** (convenience wrapper)
- **v20 refs**: None
- **Tests**: Exist. **BROKEN**: patch paths use `src.sdk_services.*`
- **Verdict**: **NEEDS_UPDATE** — fix test patch paths

---

## Assets Services

### 28. asset
- **SDK RPCs**: `mutate_assets` (1 RPC)
- **Our coverage**: create_text, create_image, create_youtube, search — **FULL**
- **v20 refs**: None
- **Tests**: Exist. **BROKEN**: patch paths use `src.sdk_services.*`
- **Verdict**: **NEEDS_UPDATE** — fix test patch paths

### 29. asset_group
- **SDK RPCs**: `mutate_asset_groups` (1 RPC)
- **Our coverage**: create, list, update, remove — **FULL**
- **v20 refs**: None
- **Tests**: Exist. **BROKEN**: patch paths use `src.sdk_services.*`
- **Verdict**: **NEEDS_UPDATE** — fix test patch paths

### 30. asset_group_asset
- **SDK RPCs**: `mutate_asset_group_assets` (1 RPC)
- **Our coverage**: create, update_status, remove — **FULL**
- **v20 refs**: Module docstring says "v20" (line 1)
- **Tests**: Exist, correct patch approach (uses `patch.object`)
- **Verdict**: **NEEDS_UPDATE** — fix docstring only

### 31. asset_group_signal
- **SDK RPCs**: `mutate_asset_group_signals` (1 RPC)
- **Our coverage**: create_audience, create_search_theme, remove, mutate — **FULL**
- **v20 refs**: Module docstring says "v20" (line 1)
- **Tests**: Exist, correct patch approach
- **Verdict**: **NEEDS_UPDATE** — fix docstring only

### 32. asset_set
- **SDK RPCs**: `mutate_asset_sets` (1 RPC)
- **Our coverage**: create, list, update, remove — **FULL**
- **v20 refs**: None
- **Tests**: Exist. **BROKEN**: patch paths use `src.sdk_services.*`
- **Verdict**: **NEEDS_UPDATE** — fix test patch paths

### 33. customer_asset
- **SDK RPCs**: `mutate_customer_assets` (1 RPC)
- **Our coverage**: create, update_status, remove, mutate — **FULL**
- **v20 refs**: Module docstring says "v20" (line 1)
- **Tests**: Exist, correct patch approach. **BUG**: one test asserts wrong exception type (`GoogleAdsException` vs `Exception`)
- **Verdict**: **NEEDS_UPDATE** — fix docstring + fix test exception assertion

---

## Audiences & Targeting Services

### 34. audience
- **SDK RPCs**: `mutate_audiences` (1 RPC)
- **Our coverage**: create_combined, list, update, remove — **FULL**
- **v20 refs**: 3 stale v20 comments in live code (lines 97, 299, 314-315) including `logger.warning` citing "v20"
- **Tests**: Exist. **BROKEN**: patch paths use `src.sdk_services.*`
- **Verdict**: **NEEDS_UPDATE** — fix v20 comments/warnings, fix test patch paths

### 35. audience_insights
- **SDK RPCs**: 8 RPCs (generate_*, list_*)
- **Our coverage**: All 8 methods — **FULL**
- **v20 refs**: None
- **Tests**: Exist but **BROKEN**: patch paths use `src.sdk_services.*`, tool count asserts 3 (should be 8), field name `country_location` should be `country_locations`
- **Verdict**: **NEEDS_UPDATE** — fix test patch paths + tool count + field names

### 36. custom_audience
- **SDK RPCs**: `mutate_custom_audiences` (1 RPC)
- **Our coverage**: create, get_details, list, update — **FULL**
- **v20 refs**: None
- **Tests**: Exist. **BROKEN**: patch paths use `src.sdk_services.*`
- **Verdict**: **NEEDS_UPDATE** — fix test patch paths

### 37. custom_interest
- **SDK RPCs**: `mutate_custom_interests` (1 RPC)
- **Our coverage**: create, get_details, list, update — **FULL**
- **v20 refs**: None
- **Logic bug**: `get_custom_interest_details` returns raw response instead of processed dict
- **Tests**: Exist. **BROKEN**: patch paths use `src.sdk_services.*`
- **Verdict**: **NEEDS_UPDATE** — fix logic bug + fix test patch paths

### 38. remarketing_action
- **SDK RPCs**: `mutate_remarketing_actions` (1 RPC)
- **Our coverage**: create, get_tags, list, update — **FULL**
- **v20 refs**: None
- **Tests**: Exist. **BROKEN**: patch paths use `src.sdk_services.*`
- **Verdict**: **NEEDS_UPDATE** — fix test patch paths

### 39. user_list
- **SDK RPCs**: `mutate_user_lists` (1 RPC)
- **Our coverage**: create_basic, create_crm, create_logical, create_similar, update — **FULL**
- **v20 refs**: None
- **Tests**: Exist. **BROKEN**: patch paths use `src.sdk_services.*`
- **Verdict**: **NEEDS_UPDATE** — fix test patch paths

### 40. customer_negative_criterion
- **SDK RPCs**: `mutate_customer_negative_criteria` (1 RPC)
- **Our coverage**: add_keywords, add_placements, add_content_labels, list, remove — **FULL**
- **v20 refs**: None
- **Tests**: **MISSING**
- **Verdict**: **NEEDS_UPDATE** — create tests

### 41. geo_target_constant
- **SDK RPCs**: `suggest_geo_target_constants` (1 RPC)
- **Our coverage**: search, suggest_by_address, suggest_by_location — **FULL**
- **v20 refs**: None
- **Runtime bug**: `suggest_geo_targets_by_location` and `suggest_geo_targets_by_address` call `request.LocationNames()` / `request.GeoTargets()` as methods — should be imported types
- **Tests**: Exist. **BROKEN**: patch paths use `src.sdk_services.*`
- **Verdict**: **NEEDS_UPDATE** — fix proto request construction + fix test patch paths

---

## Bidding & Budgets Services

### 42. bidding_data_exclusion
- **SDK RPCs**: `mutate_bidding_data_exclusions` (1 RPC)
- **Our coverage**: create, list, update, remove — **FULL**
- **v20 refs**: None
- **Tests**: Exist. **BROKEN**: patch paths use `src.sdk_services.*`
- **Verdict**: **NEEDS_UPDATE** — fix test patch paths

### 43. bidding_seasonality_adjustment
- **SDK RPCs**: `mutate_bidding_seasonality_adjustments` (1 RPC)
- **Our coverage**: create, list, update, remove — **FULL**
- **v20 refs**: None
- **Logic bug**: `status` parameter accepted but never applied to proto object
- **Tests**: **MISSING**
- **Verdict**: **NEEDS_UPDATE** — fix status bug, create tests

### 44. bidding_strategy
- **SDK RPCs**: `mutate_bidding_strategies` (1 RPC)
- **Our coverage**: create_target_cpa, create_target_roas, create_maximize_conversions, create_target_impression_share — **FULL** (create-only scope)
- **v20 refs**: None
- **Tests**: Exist. **BROKEN**: patch paths use `src.sdk_services.*`
- **Verdict**: **NEEDS_UPDATE** — fix test patch paths

### 45. budget (campaign_budget)
- **SDK RPCs**: `mutate_campaign_budgets` (1 RPC)
- **Our coverage**: create, update — **FULL** (create+update scope)
- **v20 refs**: None
- **Tests**: Exist. **BROKEN**: patch paths use `src.sdk_services.*`
- **Verdict**: **NEEDS_UPDATE** — fix test patch paths

---

## Campaign Services

### 46. campaign
- **SDK RPCs**: `mutate_campaigns`, `enable_p_max_brand_guidelines` (2 RPCs)
- **Our coverage**: create, update, enable_p_max_brand_guidelines — **FULL**
- **v20 refs**: None
- **Tests**: Exist. **BROKEN**: patch paths use `src.sdk_services.*`
- **Verdict**: **NEEDS_UPDATE** — fix test patch paths; add tests for enable_p_max_brand_guidelines

### 47. campaign_asset
- **SDK RPCs**: `mutate_campaign_assets` (1 RPC)
- **Our coverage**: link, link_multiple, list, remove — **FULL**
- **v20 refs**: None
- **Tests**: Exist. **BROKEN**: patch paths use `src.sdk_services.*`
- **Verdict**: **NEEDS_UPDATE** — fix test patch paths

### 48. campaign_asset_set
- **SDK RPCs**: `mutate_campaign_asset_sets` (1 RPC)
- **Our coverage**: link, link_multiple, unlink, mutate — **FULL**
- **v20 refs**: Module docstring says "v20" (line 1)
- **Tests**: Exist. **BROKEN**: patch paths use `src.sdk_servers.*` (different wrong prefix)
- **Verdict**: **NEEDS_UPDATE** — fix docstring + fix test patch paths

### 49. campaign_bid_modifier
- **SDK RPCs**: `mutate_campaign_bid_modifiers` (1 RPC)
- **Our coverage**: create_interaction_type, list, update, remove — **FULL**
- **v20 refs**: Comment says "v20" (lines 3-6)
- **Tests**: Exist. **BROKEN**: patch paths use `src.sdk_services.*`
- **Verdict**: **NEEDS_UPDATE** — fix v20 comment + fix test patch paths

### 50. campaign_conversion_goal
- **SDK RPCs**: `mutate_campaign_conversion_goals` (1 RPC)
- **Our coverage**: update — **FULL**
- **v20 refs**: Module docstring says "v20" (line 1)
- **Tests**: Exist, correct patch approach (uses `patch.object`)
- **Verdict**: **NEEDS_UPDATE** — fix docstring only

### 51. campaign_criterion
- **SDK RPCs**: `mutate_campaign_criteria` (1 RPC)
- **Our coverage**: add_device, add_language, add_location, add_negative_keyword, remove — **FULL**
- **v20 refs**: None
- **Tests**: Exist. **BROKEN**: patch paths use `src.sdk_services.*`
- **Verdict**: **NEEDS_UPDATE** — fix test patch paths

### 52. campaign_customizer
- **SDK RPCs**: `mutate_campaign_customizers` (1 RPC)
- **Our coverage**: create, remove — **FULL**
- **v20 refs**: Module docstring says "v20" (line 1)
- **Tests**: Exist, correct patch approach (uses `patch.object`)
- **Verdict**: **NEEDS_UPDATE** — fix docstring only

### 53. campaign_draft
- **SDK RPCs**: `mutate_campaign_drafts`, `promote_campaign_draft`, `list_campaign_draft_async_errors` (3 RPCs)
- **Our coverage**: create, list, list_errors, promote, remove, update — **FULL**
- **v20 refs**: None
- **Tests**: Exist. **BROKEN**: patch paths use `src.sdk_services.*`
- **Verdict**: **NEEDS_UPDATE** — fix test patch paths

### 54. campaign_label
- **SDK RPCs**: `mutate_campaign_labels` (1 RPC)
- **Our coverage**: apply, apply_bulk, list, remove — **FULL**
- **v20 refs**: None
- **Tests**: Exist. **BROKEN**: patch paths use `src.sdk_services.*`
- **Verdict**: **NEEDS_UPDATE** — fix test patch paths

### 55. campaign_shared_set
- **SDK RPCs**: `mutate_campaign_shared_sets` (1 RPC)
- **Our coverage**: attach, attach_bulk, detach, get_campaigns, list, update_status — **FULL**
- **v20 refs**: None
- **Tests**: Exist. **BROKEN**: patch paths use `src.sdk_services.*`
- **Verdict**: **NEEDS_UPDATE** — fix test patch paths

### 56. experiment
- **SDK RPCs**: `mutate_experiments`, `end_experiment`, `schedule_experiment`, `promote_experiment`, `graduate_experiment`, `list_experiment_async_errors` (6 RPCs)
- **Our coverage**: All 6 — **FULL**
- **v20 refs**: None
- **Tests**: Exist but missing tests for `graduate_experiment` + `list_experiment_async_errors`. **BROKEN**: patch paths use `src.sdk_services.*`
- **Verdict**: **NEEDS_UPDATE** — fix test patch paths + add tests for new methods

### 57. experiment_arm
- **SDK RPCs**: `mutate_experiment_arms` (1 RPC)
- **Our coverage**: create, remove, update, mutate — **FULL**
- **v20 refs**: None
- **Tests**: Exist but lack `get_sdk_client` mocking — tests will fail without live SDK client
- **Verdict**: **NEEDS_UPDATE** — fix test mocking

---

## Conversion Services

### 58. conversion (conversion_action)
- **SDK RPCs**: `mutate_conversion_actions` (1 RPC)
- **Our coverage**: create, update — **FULL**
- **v20 refs**: None
- **Tests**: Exist. **BROKEN**: patch paths use `src.sdk_services.*`
- **Verdict**: **NEEDS_UPDATE** — fix test patch paths

### 59. conversion_adjustment_upload
- **SDK RPCs**: `upload_conversion_adjustments` (1 RPC)
- **Our coverage**: upload, create_restatement, create_retraction — **FULL**
- **v20 refs**: None
- **Tests**: **MISSING**
- **Verdict**: **NEEDS_UPDATE** — create tests

### 60. conversion_custom_variable
- **SDK RPCs**: `mutate_conversion_custom_variables` (1 RPC)
- **Our coverage**: create, update — **FULL**
- **v20 refs**: Module docstring says "v20" (line 1)
- **Tests**: Exist, correct patch approach (uses `patch.object`)
- **Verdict**: **NEEDS_UPDATE** — fix docstring only

### 61. conversion_goal_campaign_config
- **SDK RPCs**: `mutate_conversion_goal_campaign_configs` (1 RPC)
- **Our coverage**: update, mutate — **FULL**
- **v20 refs**: None
- **Tests**: Exist, correct patch approach
- **Verdict**: **PASS**

### 62. conversion_upload
- **SDK RPCs**: `upload_click_conversions`, `upload_call_conversions` (2 RPCs)
- **Our coverage**: upload_click, upload_call — **FULL**
- **v20 refs**: None
- **Tests**: Exist. **BROKEN**: patch paths use `src.sdk_services.*`
- **Verdict**: **NEEDS_UPDATE** — fix test patch paths

### 63. conversion_value_rule
- **SDK RPCs**: `mutate_conversion_value_rules` (1 RPC)
- **Our coverage**: **BROKEN** — `create_basic` and `update_basic` return hardcoded fake dicts; `remove` raises `NotImplementedError`; SDK RPC never called
- **v20 refs**: Multiple "v20 limitations" comments throughout
- **Tests**: **MISSING**
- **Verdict**: **NEEDS_REWRITE** — entire file is a non-functional stub

### 64. custom_conversion_goal
- **SDK RPCs**: `mutate_custom_conversion_goals` (1 RPC)
- **Our coverage**: create, update, remove, mutate — **FULL**
- **v20 refs**: None
- **Tests**: **MISSING**
- **Verdict**: **NEEDS_UPDATE** — create tests

### 65. customer_conversion_goal
- **SDK RPCs**: `mutate_customer_conversion_goals` (1 RPC)
- **Our coverage**: mutate — **FULL**
- **v20 refs**: None
- **Tests**: Exist, correct patch approach
- **Verdict**: **PASS**

---

## Data Import Services

### 66. batch_job
- **SDK RPCs**: `mutate_batch_job`, `add_batch_job_operations`, `run_batch_job`, `list_batch_job_results` (4 RPCs)
- **Our coverage**: All 4 RPCs covered. **BUT** `add_operations_to_batch_job` builds empty `MutateOperation` objects (placeholder loop)
- **v20 refs**: None
- **Tests**: Exist. **BROKEN**: patch paths use `src.sdk_services.*`
- **Verdict**: **NEEDS_UPDATE** — fix `add_operations` placeholder + fix test patch paths

### 67. data_link
- **SDK RPCs**: `create_data_link`, `remove_data_link`, `update_data_link` (3 RPCs)
- **Our coverage**: create, remove, update, list (via GAQL) — **FULL**
- **v20 refs**: None
- **Tests**: **MISSING**
- **Verdict**: **NEEDS_UPDATE** — create tests

### 68. offline_user_data_job
- **SDK RPCs**: `create_offline_user_data_job`, `add_offline_user_data_job_operations`, `run_offline_user_data_job` (3 RPCs)
- **Our coverage**: create, add_ops, run, get, list — **FULL**
- **v20 refs**: Stale comment line 194: "OfflineUserData not available in v20"
- **Tests**: **MISSING**
- **Verdict**: **NEEDS_UPDATE** — fix v20 comment + create tests

### 69. user_data
- **SDK RPCs**: `upload_user_data` (1 RPC)
- **Our coverage**: upload_customer_match, upload_enhanced_conversions, upload_store_sales — **FULL**
- **v20 refs**: Stale comment line 397: "StoreSalesMetadata is not supported in v20"
- **Tests**: Exist. **BROKEN**: patch paths use `src.sdk_services.*`
- **Verdict**: **NEEDS_UPDATE** — fix v20 comment + fix test patch paths

---

## Metadata & Search Services

### 70. google_ads
- **SDK RPCs**: `search`, `search_stream`, `mutate` (3 RPCs)
- **Our coverage**: search, search_stream implemented. `mutate` exists on class but **not registered as tool**
- **v20 refs**: Module docstring says "v20" (line 1)
- **Tests**: Exist, correct patch approach
- **Verdict**: **NEEDS_UPDATE** — register mutate as tool + fix docstring

### 71. google_ads_field
- **SDK RPCs**: `get_google_ads_field`, `search_google_ads_fields` (2 RPCs)
- **Our coverage**: get_field, search_fields, get_resource_fields, validate_query — **FULL**
- **v20 refs**: None
- **Tests**: Exist. **BROKEN**: patch paths use `src.sdk_services.*`
- **Verdict**: **NEEDS_UPDATE** — fix test patch paths

### 72. search (wrapper)
- **SDK RPCs**: Uses `GoogleAdsServiceClient.search`
- **Our coverage**: execute_query, search_campaigns, search_ad_groups, search_keywords — **FULL** (convenience wrapper)
- **v20 refs**: None
- **Tests**: Exist. **BROKEN**: patch paths use `src.sdk_services.*`
- **Verdict**: **NEEDS_UPDATE** — fix test patch paths

---

## Labels & Organization Services

### 73. label
- **SDK RPCs**: `mutate_labels` (1 RPC)
- **Our coverage**: create, update, list, apply_to_campaigns, apply_to_ad_groups — **FULL**
- **v20 refs**: None
- **Tests**: Exist. **BROKEN**: patch paths use `src.sdk_services.*`
- **Verdict**: **NEEDS_UPDATE** — fix test patch paths

### 74. shared_set
- **SDK RPCs**: `mutate_shared_sets` (1 RPC)
- **Our coverage**: create, update, list, attach_to_campaigns. **BROKEN**: `attach_shared_set_to_campaigns` raises `NotImplementedError` (line 285)
- **v20 refs**: None
- **Tests**: Exist. **BROKEN**: patch paths use `src.sdk_services.*`
- **Verdict**: **NEEDS_UPDATE** — fix NotImplementedError in attach method + fix test patch paths

### 75. shared_criterion
- **SDK RPCs**: `mutate_shared_criteria` (1 RPC)
- **Our coverage**: add_keywords, add_placements, list, remove — **FULL**
- **v20 refs**: None
- **Tests**: **MISSING**
- **Verdict**: **NEEDS_UPDATE** — create tests

### 76. customizer_attribute
- **SDK RPCs**: `mutate_customizer_attributes` (1 RPC)
- **Our coverage**: create, update, list, remove — **FULL**
- **v20 refs**: None
- **Tests**: **MISSING**
- **Verdict**: **NEEDS_UPDATE** — create tests

---

## Planning & Research Services

### 77. brand_suggestion
- **SDK RPCs**: `suggest_brands` (1 RPC)
- **Our coverage**: suggest_brands — **FULL**
- **v20 refs**: None
- **Tests**: Exist, correct mock injection
- **Verdict**: **PASS**

### 78. keyword_plan
- **SDK RPCs**: `mutate_keyword_plans` (1 RPC)
- **Our coverage**: create, create_campaign, add_keywords, get_ideas — **FULL**
- **v20 refs**: None
- **Tests**: Exist. **BROKEN**: patch paths use `src.sdk_services.*`
- **Verdict**: **NEEDS_UPDATE** — fix test patch paths

### 79. keyword_plan_ad_group
- **SDK RPCs**: `mutate_keyword_plan_ad_groups` (1 RPC)
- **Our coverage**: create, update, remove, mutate — **FULL**
- **v20 refs**: None
- **Tests**: Exist, correct mock injection
- **Verdict**: **PASS**

### 80. keyword_plan_ad_group_keyword
- **SDK RPCs**: `mutate_keyword_plan_ad_group_keywords` (1 RPC)
- **Our coverage**: create, update, remove, mutate — **FULL**
- **v20 refs**: None
- **Tests**: Exist, correct mock injection
- **Verdict**: **PASS**

### 81. keyword_plan_campaign
- **SDK RPCs**: `mutate_keyword_plan_campaigns` (1 RPC)
- **Our coverage**: create, update, remove, mutate — **FULL**
- **v20 refs**: None
- **Tests**: Exist, correct mock injection
- **Verdict**: **PASS**

### 82. keyword_plan_campaign_keyword
- **SDK RPCs**: `mutate_keyword_plan_campaign_keywords` (1 RPC)
- **Our coverage**: create, update, remove, mutate — **FULL**
- **v20 refs**: None
- **Tests**: Exist, correct mock injection
- **Verdict**: **PASS**

### 83. keyword_plan_idea
- **SDK RPCs**: `generate_keyword_ideas`, `generate_keyword_historical_metrics`, `generate_ad_group_themes`, `generate_keyword_forecast_metrics` (4 RPCs)
- **Our coverage**: All 7 methods covering all 4 RPCs — **FULL**
- **v20 refs**: None
- **Tests**: Exist but missing tests for 3 new methods. **BROKEN**: patch paths use `src.sdk_services.*`
- **Verdict**: **NEEDS_UPDATE** — fix test patch paths + add tests for new methods

### 84. reach_plan
- **SDK RPCs**: `list_plannable_locations`, `list_plannable_products`, `generate_reach_forecast`, `generate_conversion_rates`, `list_plannable_user_interests`, `list_plannable_user_lists` (6 RPCs)
- **Our coverage**: All 6 — **FULL**
- **v20 refs**: None
- **Tests**: Exist but missing tests for 4 new methods. **BROKEN**: patch paths use `src.sdk_services.*`
- **Verdict**: **NEEDS_UPDATE** — fix test patch paths + add tests for new methods

### 85. recommendation
- **SDK RPCs**: `apply_recommendation`, `dismiss_recommendation`, `generate_recommendations` (3 RPCs)
- **Our coverage**: get (via GAQL), apply, dismiss, generate — **FULL**
- **v20 refs**: None
- **Tests**: Exist but missing test for `generate_recommendations`. **BROKEN**: patch paths use `src.sdk_services.*`
- **Verdict**: **NEEDS_UPDATE** — fix test patch paths + add test for new method

---

## Product Integration Services

### 86. product_link
- **SDK RPCs**: `create_product_link`, `remove_product_link` (2 RPCs)
- **Our coverage**: create (merchant/ads/data_partner), remove — **FULL**
- **v20 refs**: None
- **Tests**: Exist, correct mock injection
- **Verdict**: **PASS**

---

## Smart Campaign Services

### 87. smart_campaign (wrapper for smart_campaign_suggest)
- **SDK RPCs**: `suggest_smart_campaign_budget_options`, `suggest_smart_campaign_ad`, `suggest_keyword_themes` (3 RPCs)
- **Our coverage**: suggest_budget, suggest_ad, suggest_keywords — **FULL**
- **v20 refs**: None
- **Tests**: Exist. **BROKEN**: patch paths use `src.sdk_services.*`
- **Verdict**: **NEEDS_UPDATE** — fix test patch paths

---

## Consolidated Findings

### Systemic test issue
**~40 test files** use `src.sdk_services.*` in `patch()` targets. The directory `src/sdk_services/` does not exist. All these mocks silently no-op. Correct path is `src.services.*`.

### Services requiring code fixes (not just test fixes)

| Priority | Service | Issue |
|----------|---------|-------|
| P0 | `conversion_value_rule` | Entire file is a stub — create/update return fake dicts, remove raises NotImplementedError |
| P0 | `shared_set` | `attach_shared_set_to_campaigns` raises NotImplementedError (line 285) |
| P1 | `batch_job` | `add_operations_to_batch_job` builds empty MutateOperation objects |
| P1 | `geo_target_constant` | Runtime AttributeError — `request.LocationNames()` should be imported type |
| P1 | `customer` | Missing `mutate_customer` RPC; dead code in `list_accessible_customers` |
| P1 | `google_ads` | `mutate` method exists but not registered as tool |
| P2 | `custom_interest` | `get_custom_interest_details` returns raw response instead of processed dict |
| P2 | `billing_setup` | Missing `remove` operation |
| P2 | `bidding_seasonality_adjustment` | `status` param accepted but never applied |
| P2 | `audience` | 3 stale v20 guards in live code (lines 97, 299, 314-315) |

### Stale v20 docstrings (13 files — cosmetic)

1. `google_ads_service.py`, 2. `ad_group_criterion_label_service.py`, 3. `ad_group_customizer_service.py`, 4. `asset_group_asset_service.py`, 5. `asset_group_signal_service.py`, 6. `customer_asset_service.py`, 7. `campaign_asset_set_service.py`, 8. `campaign_conversion_goal_service.py`, 9. `campaign_customizer_service.py`, 10. `customer_customizer_service.py`, 11. `customer_label_service.py`, 12. `customer_manager_link_service.py`, 13. `conversion_custom_variable_service.py`

### Missing test files (15 services)

1. `customer_customizer`, 2. `customer_user_access_invitation`, 3. `identity_verification`, 4. `payments_account`, 5. `ad_group_ad_label`, 6. `ad_group_asset_set`, 7. `bidding_seasonality_adjustment`, 8. `conversion_adjustment_upload`, 9. `conversion_value_rule`, 10. `custom_conversion_goal`, 11. `data_link`, 12. `offline_user_data_job`, 13. `customizer_attribute`, 14. `shared_criterion`, 15. `customer_negative_criterion`

### Tests needing updates for new methods (7 files)

1. `test_ad_group_ad_service.py` — add `remove_automatically_created_assets` + fix tool count (4→5)
2. `test_campaign_service.py` — add `enable_p_max_brand_guidelines`
3. `test_experiment_service.py` — add `graduate_experiment`, `list_experiment_async_errors`
4. `test_recommendation_service.py` — add `generate_recommendations`
5. `test_reach_plan_service.py` — add 4 new methods, replace stub test
6. `test_keyword_plan_idea_service.py` — add 3 new methods
7. `test_audience_insights_service.py` — add 5 new methods + fix tool count (3→8) + fix `country_location`→`country_locations`

### PASS verdicts (10 services — no changes needed)

1. `brand_suggestion`, 2. `product_link`, 3. `keyword_plan_ad_group`, 4. `keyword_plan_ad_group_keyword`, 5. `keyword_plan_campaign`, 6. `keyword_plan_campaign_keyword`, 7. `conversion_goal_campaign_config`, 8. `customer_conversion_goal`, 9. `ad_group_criterion_label` (docstring only), 10. `ad_group_customizer` (docstring only)
