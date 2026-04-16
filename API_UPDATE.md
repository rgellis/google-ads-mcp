# API Update Checklist

Tracks remaining work to bring the project to full v23 coverage with 100% test coverage.

**Created:** 2026-04-15

---

## 1. Fix Deprecated v20 Patterns in Existing Services

### HIGH PRIORITY (broken/stub implementations)

- [ ] **`src/services/conversions/conversion_value_rule_service.py`** — `create_basic` and `update_basic` return hardcoded fake dicts, `remove` raises `NotImplementedError`. Entire file is a non-functional stub blaming "v20 limitations". Rewrite with real v23 SDK calls using `ConversionValueRuleOperation`, `MutateConversionValueRulesRequest`.
- [ ] **`src/services/shared/shared_set_service.py:285`** — `raise NotImplementedError` with dead code below it. Implement or remove the dead code path.
- [ ] **`src/services/data_import/batch_job_service.py:182`** — Operations list constructed but never populated; `add_operations` is effectively a no-op. Implement actual operation building from input.

### MEDIUM PRIORITY (logic gated on stale v20 assumptions)

- [ ] **`src/services/audiences/audience_service.py` (lines 97, 299, 314-315)** — Exclusion dimension limits and runtime warnings cite "v20" — may be too restrictive in v23. Verify v23 exclusion support and remove/update v20 guards.
- [ ] **`src/services/data_import/offline_user_data_job_service.py:194`** — Comment: "OfflineUserData not available in v20 - simplified implementation". Verify v23 type availability and implement fully.
- [ ] **`src/services/data_import/user_data_service.py:397`** — Comment: "StoreSalesMetadata is not supported as a separate field in v20 API". Verify v23 support and implement if available.

### LOW PRIORITY (cosmetic — stale docstrings mentioning "v20")

- [ ] `src/services/metadata/google_ads_service.py`
- [ ] `src/services/ad_group/ad_group_criterion_label_service.py`
- [ ] `src/services/ad_group/ad_group_customizer_service.py`
- [ ] `src/services/assets/asset_group_asset_service.py`
- [ ] `src/services/assets/asset_group_signal_service.py`
- [ ] `src/services/assets/customer_asset_service.py`
- [ ] `src/services/campaign/campaign_asset_set_service.py`
- [ ] `src/services/campaign/campaign_conversion_goal_service.py`
- [ ] `src/services/campaign/campaign_customizer_service.py`
- [ ] `src/services/account/customer_customizer_service.py`
- [ ] `src/services/account/customer_label_service.py`
- [ ] `src/services/account/customer_manager_link_service.py`
- [ ] `src/services/conversions/conversion_custom_variable_service.py`

---

## 2. Implement Remaining 26 Services

### Existed since v20 (18 services)

- [ ] `asset_group_listing_group_filter` — `mutate_asset_group_listing_group_filters` — PMax product feed targeting filters
- [ ] `asset_set_asset` — `mutate_asset_set_assets` — Link assets to asset sets
- [ ] `campaign_group` — `mutate_campaign_groups` — Campaign grouping/organization
- [ ] `campaign_lifecycle_goal` — `configure_campaign_lifecycle_goals` — Campaign acquisition/retention goals
- [ ] `content_creator_insights` — `generate_creator_insights`, `generate_trending_insights` — YouTube creator and trending data
- [ ] `conversion_value_rule_set` — `mutate_conversion_value_rule_sets` — Group conversion value rules
- [ ] `customer_asset_set` — `mutate_customer_asset_sets` — Customer-level asset set links
- [ ] `customer_lifecycle_goal` — `configure_customer_lifecycle_goals` — Account-level lifecycle goals
- [ ] `customer_sk_ad_network_conversion_value_schema` — `mutate_customer_sk_ad_network_conversion_value_schema` — iOS SKAdNetwork schema
- [ ] `keyword_theme_constant` — `suggest_keyword_theme_constants` — Smart campaign theme suggestions
- [ ] `local_services_lead` — `append_lead_conversation`, `provide_lead_feedback` — Local Services Ads lead management
- [ ] `product_link_invitation` — `create_product_link_invitation`, `remove_product_link_invitation`, `update_product_link_invitation` — Product link invitation management
- [ ] `recommendation_subscription` — `mutate_recommendation_subscription` — Auto-apply recommendation subscriptions
- [ ] `shareable_preview` — `generate_shareable_previews` — Generate shareable ad preview URLs
- [ ] `smart_campaign_setting` — `get_smart_campaign_status`, `mutate_smart_campaign_settings` — Smart campaign setting management
- [ ] `third_party_app_analytics_link` — `regenerate_shareable_link_id` — Third-party app analytics links
- [ ] `travel_asset_suggestion` — `suggest_travel_assets` — Travel campaign asset suggestions
- [ ] `user_list_customer_type` — `mutate_user_list_customer_types` — User list customer type classifications

### New in v23 only (8 services)

- [ ] `asset_generation` — `generate_images`, `generate_text` — AI-generated assets
- [ ] `automatically_created_asset_removal` — `remove_campaign_automatically_created_asset` — Remove auto-created campaign assets
- [ ] `benchmarks` — `generate_benchmarks_metrics`, `list_benchmarks_available_dates`, `list_benchmarks_locations`, `list_benchmarks_products`, `list_benchmarks_sources` — Competitive benchmarking
- [ ] `campaign_goal_config` — `mutate_campaign_goal_configs` — Campaign goal configuration
- [ ] `goal` — `mutate_goals` — Account-level goal management
- [ ] `incentive` — `apply_incentive`, `fetch_incentive` — Promotional credits/incentives
- [ ] `reservation` — `book_campaigns`, `quote_campaigns` — Guaranteed reservation campaigns
- [ ] `you_tube_video_upload` — `create_you_tube_video_upload`, `remove_you_tube_video_upload`, `update_you_tube_video_upload` — YouTube video uploads via Ads API

---

## 3. Test Coverage

### Tests needing updates for newly added methods (7 files)

- [ ] `tests/test_ad_group_ad_service.py` — add: `remove_automatically_created_assets`
- [ ] `tests/test_campaign_service.py` — add: `enable_p_max_brand_guidelines`
- [ ] `tests/test_experiment_service.py` — add: `graduate_experiment`, `list_experiment_async_errors`
- [ ] `tests/test_recommendation_service.py` — add: `generate_recommendations`
- [ ] `tests/test_reach_plan_service.py` — add: `generate_reach_forecast` (replaces stub test), `generate_conversion_rates`, `list_plannable_user_interests`, `list_plannable_user_lists`
- [ ] `tests/test_keyword_plan_idea_service.py` — add: `generate_keyword_historical_metrics`, `generate_ad_group_themes`, `generate_keyword_forecast_metrics`
- [ ] `tests/test_audience_insights_service.py` — add: `generate_audience_definition`, `generate_audience_overlap_insights`, `generate_targeting_suggestion_metrics`, `list_audience_insights_attributes`, `list_insights_eligible_dates`; also fix `BasicInsightsAudience` references

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

---

## For each service implementation

1. Check v23 service types in SDK (`google.ads.googleads.v23.services.types.*`)
2. Implement ALL operations for 1:1 API coverage using full v23 types
3. Write comprehensive tests covering all methods
4. Update `TRACKER.md` with completion status
5. Run `uv run ruff format .` and `uv run pyright`
