# API Update Checklist

Tracks remaining work to bring the project to full v23 coverage with 100% test coverage.

**Created:** 2026-04-15

---

## 1. Fix Deprecated v20 Patterns in Existing Services

### HIGH PRIORITY (broken/stub implementations)

- [x] **`src/services/conversions/conversion_value_rule_service.py`** — ~~`create_basic` and `update_basic` return hardcoded fake dicts, `remove` raises `NotImplementedError`.~~ **DONE** — Full rewrite with real v23 SDK calls using `MutateConversionValueRulesRequest`, supports action ops, device/geo/audience conditions.
- [x] **`src/services/shared/shared_set_service.py:285`** — ~~`raise NotImplementedError` with dead code below it.~~ **DONE** — Removed `NotImplementedError`, unblocked existing implementation, added response capture.
- [x] **`src/services/data_import/batch_job_service.py:182`** — ~~Operations list constructed but never populated.~~ **DONE** — Replaced placeholder loop with dict-to-MutateOperation mapping via `setattr`, removed stale sequence_token default.

### P1 (discovered during deep validation)

- [x] **`src/services/targeting/geo_target_constant_service.py`** — ~~Runtime `AttributeError` in both suggest methods.~~ **DONE** — Fixed to use `SuggestGeoTargetConstantsRequest.LocationNames()` (class-level), and fixed `suggest_geo_targets_by_address` which incorrectly used `GeoTargets` (resource name lookup) instead of `LocationNames` (text search).
- [x] **`src/services/account/customer_service.py`** — ~~Missing `mutate_customer` RPC, dead code in `list_accessible_customers`.~~ **DONE** — Added `mutate_customer` (update descriptive_name, auto_tagging, tracking_url_template), removed dead code, fixed `list_accessible_customers` return type from raw proto to dict.
- [x] **`src/services/metadata/google_ads_service.py`** — ~~`mutate` method not registered as tool.~~ **DONE** — Added `mutate_google_ads` tool wrapper accepting dict-based operations, registered in `tools.extend(...)`. Also fixed stale v20 docstring.
- [x] **`src/services/audiences/custom_interest_service.py`** — ~~`get_custom_interest_details` returns raw response.~~ **DONE** — Fixed to return serialized row from inside the loop, raises if not found.
- [x] **`src/services/account/billing_setup_service.py`** — ~~Missing `remove` operation.~~ **DONE** — Added `remove_billing_setup` method and tool for cancelling pending billing setups.
- [x] **`src/services/bidding/bidding_seasonality_adjustment_service.py`** — ~~`status` parameter never applied.~~ **DONE** — Added `SeasonalityEventStatusEnum` import and `adjustment.status = ...` assignment.

### MEDIUM PRIORITY (logic gated on stale v20 assumptions)

- [x] **`src/services/audiences/audience_service.py` (lines 97, 299, 314-315)** — ~~Exclusion dimension limits and runtime warnings cite "v20".~~ **DONE** — Removed 3 stale v20 comments/references from live code.
- [x] **`src/services/data_import/offline_user_data_job_service.py:194`** — ~~Comment: "OfflineUserData not available in v20".~~ **DONE** — Removed v20 reference from comment.
- [x] **`src/services/data_import/user_data_service.py:397`** — ~~Comment: "StoreSalesMetadata is not supported in v20 API".~~ **DONE** — Removed v20 reference from comment.

### LOW PRIORITY (cosmetic — stale docstrings mentioning "v20")

- [x] All 13 files updated from "v20" to "v23" in module docstrings. **DONE**
- `src/services/metadata/google_ads_service.py` (fixed earlier with mutate registration)
- `src/services/ad_group/ad_group_criterion_label_service.py`
- `src/services/ad_group/ad_group_customizer_service.py`
- `src/services/assets/asset_group_asset_service.py`
- `src/services/assets/asset_group_signal_service.py`
- `src/services/assets/customer_asset_service.py`
- `src/services/campaign/campaign_asset_set_service.py`
- `src/services/campaign/campaign_bid_modifier_service.py`
- `src/services/campaign/campaign_conversion_goal_service.py`
- `src/services/campaign/campaign_customizer_service.py`
- `src/services/account/customer_customizer_service.py`
- `src/services/account/customer_label_service.py`
- `src/services/account/customer_manager_link_service.py`
- `src/services/conversions/conversion_custom_variable_service.py`

---

## 2. Implement Remaining Services

**All 26 services DONE.**

### Existed since v20 (18 services) — ALL DONE

- [x] `asset_group_listing_group_filter` — PMax product feed targeting filters
- [x] `asset_set_asset` — Link assets to asset sets
- [x] `campaign_group` — Campaign grouping/organization
- [x] `campaign_lifecycle_goal` — Campaign acquisition/retention goals
- [x] `content_creator_insights` — YouTube creator and trending data
- [x] `conversion_value_rule_set` — Group conversion value rules
- [x] `customer_asset_set` — Customer-level asset set links
- [x] `customer_lifecycle_goal` — Account-level lifecycle goals
- [x] `customer_sk_ad_network_conversion_value_schema` — iOS SKAdNetwork schema
- [x] `keyword_theme_constant` — Smart campaign theme suggestions
- [x] `local_services_lead` — Local Services Ads lead management
- [x] `product_link_invitation` — Product link invitation management
- [x] `recommendation_subscription` — Auto-apply recommendation subscriptions
- [x] `shareable_preview` — Generate shareable ad preview URLs
- [x] `smart_campaign_setting` — Smart campaign setting management
- [x] `third_party_app_analytics_link` — Third-party app analytics links
- [x] `travel_asset_suggestion` — Travel campaign asset suggestions
- [x] `user_list_customer_type` — User list customer type classifications

### New in v23 only — ALL DONE (7 of 8; 1 skipped)

- [x] `asset_generation` — AI-generated text and image assets
- [x] `automatically_created_asset_removal` — Remove auto-created campaign assets
- [x] `benchmarks` — Competitive benchmarking (5 RPCs)
- [x] `campaign_goal_config` — Campaign goal configuration
- [x] `goal` — Account-level goal management
- [x] `incentive` — Promotional credits/incentives
- [x] `reservation` — Guaranteed reservation campaigns
- [x] `you_tube_video_upload` — YouTube video uploads via Ads API (create/update/remove with file stream)

---

## 3. Test Coverage

### Tests needing updates for newly added methods (7 files)

- [x] `tests/test_ad_group_ad_service.py` — **DONE** — added `remove_automatically_created_assets`, fixed tool count 4→5
- [x] `tests/test_campaign_service.py` — **DONE** — added `enable_p_max_brand_guidelines`, fixed tool count 2→3
- [x] `tests/test_experiment_service.py` — **DONE** — added `graduate_experiment`, `list_experiment_async_errors`, fixed tool count 5→7
- [x] `tests/test_recommendation_service.py` — **DONE** — added `generate_recommendations`, fixed tool count 3→4
- [x] `tests/test_reach_plan_service.py` — **DONE** — added 4 new method tests, removed old stub test, fixed tool count 3→6
- [x] `tests/test_keyword_plan_idea_service.py` — **DONE** — added 3 new method tests, fixed tool count 4→7
- [x] `tests/test_audience_insights_service.py` — **DONE** — added 5 new method tests, fixed `country_location`→`country_locations`, removed `BasicInsightsAudience` refs, fixed tool count 3→8

### Services completely missing tests (15 files)

- [ ] `customer_customizer` — `src/services/account/customer_customizer_service.py`
- [ ] `customer_user_access_invitation` — `src/services/account/customer_user_access_invitation_service.py`
- [ ] `identity_verification` — `src/services/account/identity_verification_service.py`
- [ ] `payments_account` — `src/services/account/payments_account_service.py`
- [ ] `ad_group_ad_label` — `src/services/ad_group/ad_group_ad_label_service.py`
- [ ] `ad_group_asset_set` — `src/services/ad_group/ad_group_asset_set_service.py`
- [ ] `bidding_seasonality_adjustment` — `src/services/bidding/bidding_seasonality_adjustment_service.py`
- [ ] `conversion_adjustment_upload` — `src/services/conversions/conversion_adjustment_upload_service.py`
- [ ] `conversion_value_rule` — `src/services/conversions/conversion_value_rule_service.py`
- [ ] `custom_conversion_goal` — `src/services/conversions/custom_conversion_goal_service.py`
- [ ] `data_link` — `src/services/data_import/data_link_service.py`
- [ ] `offline_user_data_job` — `src/services/data_import/offline_user_data_job_service.py`
- [ ] `customizer_attribute` — `src/services/shared/customizer_attribute_service.py`
- [ ] `shared_criterion` — `src/services/shared/shared_criterion_service.py`
- [ ] `customer_negative_criterion` — `src/services/targeting/customer_negative_criterion_service.py`

### Systemic test fix: patch paths

- [x] **Fixed `src.sdk_services.*` -> `src.services.*`** in 51 test files. All `patch()` targets were pointing at a non-existent module, causing mocks to silently no-op. Also fixed `src.sdk_servers.*` -> `src.servers.*` in 2 test files.

---

## For each service implementation

1. Check v23 service types in SDK (`google.ads.googleads.v23.services.types.*`)
2. Implement ALL operations for 1:1 API coverage using full v23 types
3. Write comprehensive tests covering all methods
4. Update `TRACKER.md` with completion status
5. Run `uv run ruff format .` and `uv run pyright`
