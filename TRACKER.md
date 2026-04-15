# Google Ads MCP Service Implementation Tracker

## Overview
This document tracks the implementation progress of all Google Ads API services in the MCP server.
- **SDK version**: `google-ads==30.0.0` (supports v20-v23)
- **All imports currently use**: `v23`
- **Goal**: 1:1 mapping of ALL Google Ads services with full type safety using generated protobuf types.

## Progress Summary
- **Total v23 services**: 111
- **Implemented**: 87 service files (+ 5 convenience wrappers mapping to existing SDK services)
- **Not implemented**: 24 services
- **All code uses v23 imports** - no legacy v20/v21/v22 references remain.

**Last Audit Date:** 2026-04-15

---

## Name Mapping (convenience wrappers)

These are custom service files that wrap an existing SDK service under a friendlier name:

| Our name | SDK service it wraps | Notes |
|---|---|---|
| `budget` | `campaign_budget` | Same SDK client, different file name |
| `conversion` | `conversion_action` | Same SDK client, different file name |
| `keyword` | `ad_group_criterion` | Keyword-specific subset of criterion ops |
| `search` | `google_ads` | Convenience GAQL search wrapper |
| `smart_campaign` | `smart_campaign_suggest` | Only wraps suggest methods; `smart_campaign_setting` NOT covered |

---

## Implementation Status - Full Checklist

Legend:
- **Implemented**: has a service file in `src/services/`
- **v23 RPC methods**: the actual gRPC methods the SDK service exposes
- **Our methods**: the MCP tool functions we expose

### Account Management

| # | Service | Status | v23 RPC methods | Our methods | Gap? |
|---|---------|--------|----------------|-------------|------|
| 1 | `account_budget_proposal` | done | `mutate_account_budget_proposal` | create, update, remove, list | - |
| 2 | `account_link` | done | `create_account_link`, `mutate_account_link` | create, update, remove, list | - |
| 3 | `billing_setup` | done | `mutate_billing_setup` | create, get, list, list_payments | - |
| 4 | `customer` | done | `create_customer_client`, `list_accessible_customers`, `mutate_customer` | create_customer_client, list_accessible_customers | - |
| 5 | `customer_client_link` | done | `mutate_customer_client_link` | create, update, list | - |
| 6 | `customer_customizer` | done | `mutate_customer_customizers` | create (text/number/price/percent), remove, mutate | - |
| 7 | `customer_label` | done | `mutate_customer_labels` | create, remove | - |
| 8 | `customer_manager_link` | done | `move_manager_link`, `mutate_customer_manager_link` | accept, decline, move, terminate, update | - |
| 9 | `customer_user_access` | done | `mutate_customer_user_access` | list, update, revoke | - |
| 10 | `customer_user_access_invitation` | done | `mutate_customer_user_access_invitation` | create, list, remove | - |
| 11 | `identity_verification` | done | `get_identity_verification`, `start_identity_verification` | get, start | - |
| 12 | `invoice` | done | `list_invoices` | list | - |
| 13 | `payments_account` | done | `list_payments_accounts` | list | - |

### Ad Group & Ads

| # | Service | Status | v23 RPC methods | Our methods | Gap? |
|---|---------|--------|----------------|-------------|------|
| 14 | `ad` | done | `mutate_ads` | create_responsive_search_ad, create_expanded_text_ad, update_status | - |
| 15 | `ad_group` | done | `mutate_ad_groups` | create, update | - |
| 16 | `ad_group_ad` | done | `mutate_ad_group_ads`, `remove_automatically_created_assets` | create, list, remove, update_status | **Missing**: `remove_automatically_created_assets` |
| 17 | `ad_group_ad_label` | done | `mutate_ad_group_ad_labels` | create, list, remove | - |
| 18 | `ad_group_asset` | done | `mutate_ad_group_assets` | link, link_multiple, list, remove, update_status | - |
| 19 | `ad_group_asset_set` | done | `mutate_ad_group_asset_sets` | create, list, remove | - |
| 20 | `ad_group_bid_modifier` | done | `mutate_ad_group_bid_modifiers` | create (device/hotel), list, remove, update | - |
| 21 | `ad_group_criterion` | done | `mutate_ad_group_criteria` | add_keywords, add_audience, add_demographic, remove, update_bid | - |
| 22 | `ad_group_criterion_customizer` | done | `mutate_ad_group_criterion_customizers` | mutate | - |
| 23 | `ad_group_criterion_label` | done | `mutate_ad_group_criterion_labels` | assign, assign_multiple, remove, mutate | - |
| 24 | `ad_group_customizer` | done | `mutate_ad_group_customizers` | create (text/number/price/percent), remove, mutate | - |
| 25 | `ad_group_label` | done | `mutate_ad_group_labels` | apply, apply_bulk, list, remove | - |
| 26 | `ad_parameter` | done | `mutate_ad_parameters` | mutate | - |
| 27 | `keyword` (wrapper) | done | (uses `ad_group_criterion`) | add, remove, update_bid | convenience wrapper |

### Assets

| # | Service | Status | v23 RPC methods | Our methods | Gap? |
|---|---------|--------|----------------|-------------|------|
| 28 | `asset` | done | `mutate_assets` | create_text, create_image, create_youtube, search | - |
| 29 | `asset_generation` | **NOT IMPL** | `generate_images`, `generate_text` | - | v23-only service |
| 30 | `asset_group` | done | `mutate_asset_groups` | create, list, remove, update | - |
| 31 | `asset_group_asset` | done | `mutate_asset_group_assets` | create, remove, update_status | - |
| 32 | `asset_group_listing_group_filter` | **NOT IMPL** | `mutate_asset_group_listing_group_filters` | - | PMax listing filters |
| 33 | `asset_group_signal` | done | `mutate_asset_group_signals` | create_audience, create_search_theme, remove, mutate | - |
| 34 | `asset_set` | done | `mutate_asset_sets` | create, list, remove, update | - |
| 35 | `asset_set_asset` | **NOT IMPL** | `mutate_asset_set_assets` | - | Links assets to sets |
| 36 | `automatically_created_asset_removal` | **NOT IMPL** | `remove_campaign_automatically_created_asset` | - | v23-only service |
| 37 | `customer_asset` | done | `mutate_customer_assets` | create, remove, update_status, mutate | - |
| 38 | `customer_asset_set` | **NOT IMPL** | `mutate_customer_asset_sets` | - | Customer-level asset sets |

### Audiences & Targeting

| # | Service | Status | v23 RPC methods | Our methods | Gap? |
|---|---------|--------|----------------|-------------|------|
| 39 | `audience` | done | `mutate_audiences` | create_combined, list, remove, update | - |
| 40 | `audience_insights` | done | `generate_audience_composition_insights`, `generate_audience_definition`, `generate_audience_overlap_insights`, `generate_insights_finder_report`, `generate_suggested_targeting_insights`, `generate_targeting_suggestion_metrics`, `list_audience_insights_attributes`, `list_insights_eligible_dates` | generate_composition, generate_finder_report, generate_suggested_targeting | **Missing**: `generate_audience_definition`, `generate_audience_overlap_insights`, `generate_targeting_suggestion_metrics`, `list_audience_insights_attributes`, `list_insights_eligible_dates` |
| 41 | `custom_audience` | done | `mutate_custom_audiences` | create, get_details, list, update | - |
| 42 | `custom_interest` | done | `mutate_custom_interests` | create, get_details, list, update | - |
| 43 | `customer_negative_criterion` | done | `mutate_customer_negative_criteria` | add_keywords, add_placements, add_content_labels, list, remove | - |
| 44 | `geo_target_constant` | done | `suggest_geo_target_constants` | search, suggest_by_address, suggest_by_location | - |
| 45 | `remarketing_action` | done | `mutate_remarketing_actions` | create, get_tags, list, update | - |
| 46 | `user_list` | done | `mutate_user_lists` | create_basic, create_crm, create_logical, create_similar, update | - |
| 47 | `user_list_customer_type` | **NOT IMPL** | `mutate_user_list_customer_types` | - | Customer types for user lists |

### Bidding & Budgets

| # | Service | Status | v23 RPC methods | Our methods | Gap? |
|---|---------|--------|----------------|-------------|------|
| 48 | `bidding_data_exclusion` | done | `mutate_bidding_data_exclusions` | create, list, remove, update | - |
| 49 | `bidding_seasonality_adjustment` | done | `mutate_bidding_seasonality_adjustments` | create, list, remove, update | - |
| 50 | `bidding_strategy` | done | `mutate_bidding_strategies` | create_target_cpa, create_target_roas, create_maximize_conversions, create_target_impression_share | - |
| 51 | `budget` (=`campaign_budget`) | done | `mutate_campaign_budgets` | create, update | - |

### Campaigns

| # | Service | Status | v23 RPC methods | Our methods | Gap? |
|---|---------|--------|----------------|-------------|------|
| 52 | `campaign` | done | `mutate_campaigns`, `enable_p_max_brand_guidelines` | create, update | **Missing**: `enable_p_max_brand_guidelines` (v23-new) |
| 53 | `campaign_asset` | done | `mutate_campaign_assets` | link, link_multiple, list, remove | - |
| 54 | `campaign_asset_set` | done | `mutate_campaign_asset_sets` | link, link_multiple, unlink, mutate | - |
| 55 | `campaign_bid_modifier` | done | `mutate_campaign_bid_modifiers` | create_interaction_type, list, remove, update | - |
| 56 | `campaign_conversion_goal` | done | `mutate_campaign_conversion_goals` | update | - |
| 57 | `campaign_criterion` | done | `mutate_campaign_criteria` | add_device, add_language, add_location, add_negative_keyword, remove | - |
| 58 | `campaign_customizer` | done | `mutate_campaign_customizers` | create, remove | - |
| 59 | `campaign_draft` | done | `list_campaign_draft_async_errors`, `mutate_campaign_drafts`, `promote_campaign_draft` | create, list, list_errors, promote, remove, update | - |
| 60 | `campaign_goal_config` | **NOT IMPL** | `mutate_campaign_goal_configs` | - | v23-only service |
| 61 | `campaign_group` | **NOT IMPL** | `mutate_campaign_groups` | - | Campaign grouping |
| 62 | `campaign_label` | done | `mutate_campaign_labels` | apply, apply_bulk, list, remove | - |
| 63 | `campaign_lifecycle_goal` | **NOT IMPL** | `configure_campaign_lifecycle_goals` | - | Lifecycle goal config |
| 64 | `campaign_shared_set` | done | `mutate_campaign_shared_sets` | attach, attach_bulk, detach, get_campaigns, list, update_status | - |

### Conversions

| # | Service | Status | v23 RPC methods | Our methods | Gap? |
|---|---------|--------|----------------|-------------|------|
| 65 | `conversion` (=`conversion_action`) | done | `mutate_conversion_actions` | create, update | - |
| 66 | `conversion_adjustment_upload` | done | `upload_conversion_adjustments` | create_restatement, create_retraction, upload | - |
| 67 | `conversion_custom_variable` | done | `mutate_conversion_custom_variables` | create, update | - |
| 68 | `conversion_goal_campaign_config` | done | `mutate_conversion_goal_campaign_configs` | update, mutate | - |
| 69 | `conversion_upload` | done | `upload_call_conversions`, `upload_click_conversions` | upload_call, upload_click | - |
| 70 | `conversion_value_rule` | done | `mutate_conversion_value_rules` | create_basic, list, remove, update_basic | - |
| 71 | `conversion_value_rule_set` | **NOT IMPL** | `mutate_conversion_value_rule_sets` | - | Rule set grouping |
| 72 | `custom_conversion_goal` | done | `mutate_custom_conversion_goals` | create, remove, update, mutate | - |
| 73 | `customer_conversion_goal` | done | `mutate_customer_conversion_goals` | mutate | - |
| 74 | `customer_lifecycle_goal` | **NOT IMPL** | `configure_customer_lifecycle_goals` | - | Lifecycle goals |
| 75 | `customer_sk_ad_network_conversion_value_schema` | **NOT IMPL** | `mutate_customer_sk_ad_network_conversion_value_schema` | - | iOS SKAdNetwork |

### Data Import & Jobs

| # | Service | Status | v23 RPC methods | Our methods | Gap? |
|---|---------|--------|----------------|-------------|------|
| 76 | `batch_job` | done | `add_batch_job_operations`, `list_batch_job_results`, `mutate_batch_job`, `run_batch_job` | create, add_ops, list_results, list, get, run | - |
| 77 | `data_link` | done | `create_data_link`, `remove_data_link`, `update_data_link` | create_basic, list | **Missing**: `remove_data_link`, `update_data_link` |
| 78 | `offline_user_data_job` | done | `add_offline_user_data_job_operations`, `create_offline_user_data_job`, `run_offline_user_data_job` | create_customer_match, add_ops, get, list, run | - |
| 79 | `user_data` | done | `upload_user_data` | upload_customer_match, upload_enhanced_conversions, upload_store_sales | - |

### Experiments

| # | Service | Status | v23 RPC methods | Our methods | Gap? |
|---|---------|--------|----------------|-------------|------|
| 80 | `experiment` | done | `end_experiment`, `graduate_experiment`, `list_experiment_async_errors`, `mutate_experiments`, `promote_experiment`, `schedule_experiment` | create, list, end, promote, schedule | **Missing**: `graduate_experiment`, `list_experiment_async_errors` |
| 81 | `experiment_arm` | done | `mutate_experiment_arms` | create, remove, update, mutate | - |

### Metadata & Search

| # | Service | Status | v23 RPC methods | Our methods | Gap? |
|---|---------|--------|----------------|-------------|------|
| 82 | `google_ads` | done | `mutate`, `search`, `search_stream` | mutate, search, search_stream | - |
| 83 | `google_ads_field` | done | `get_google_ads_field`, `search_google_ads_fields` | get_field, get_resource_fields, search_fields, validate_query | - |
| 84 | `search` (wrapper) | done | (uses `google_ads`) | execute_query, search_campaigns, search_ad_groups, search_keywords | convenience wrapper |

### Labels & Organization

| # | Service | Status | v23 RPC methods | Our methods | Gap? |
|---|---------|--------|----------------|-------------|------|
| 85 | `label` | done | `mutate_labels` | create, list, update, apply_to_campaigns, apply_to_ad_groups | - |
| 86 | `shared_set` | done | `mutate_shared_sets` | create, list, update, attach_to_campaigns | - |
| 87 | `shared_criterion` | done | `mutate_shared_criteria` | add_keywords, add_placements, list, remove | - |
| 88 | `customizer_attribute` | done | `mutate_customizer_attributes` | create, list, remove, update | - |

### Planning & Research

| # | Service | Status | v23 RPC methods | Our methods | Gap? |
|---|---------|--------|----------------|-------------|------|
| 89 | `brand_suggestion` | done | `suggest_brands` | suggest_brands | - |
| 90 | `keyword_plan` | done | `mutate_keyword_plans` | create, create_campaign, add_keywords, get_ideas | - |
| 91 | `keyword_plan_ad_group` | done | `mutate_keyword_plan_ad_groups` | create, remove, update, mutate | - |
| 92 | `keyword_plan_ad_group_keyword` | done | `mutate_keyword_plan_ad_group_keywords` | create, remove, update, mutate | - |
| 93 | `keyword_plan_campaign` | done | `mutate_keyword_plan_campaigns` | create, remove, update, mutate | - |
| 94 | `keyword_plan_campaign_keyword` | done | `mutate_keyword_plan_campaign_keywords` | create, remove, update, mutate | - |
| 95 | `keyword_plan_idea` | done | `generate_ad_group_themes`, `generate_keyword_forecast_metrics`, `generate_keyword_historical_metrics`, `generate_keyword_ideas` | generate_from_keywords, generate_from_url, generate_from_site, generate_from_keywords_and_url | **Missing**: `generate_ad_group_themes`, `generate_keyword_forecast_metrics`, `generate_keyword_historical_metrics` |
| 96 | `keyword_theme_constant` | **NOT IMPL** | `suggest_keyword_theme_constants` | - | Smart campaign themes |
| 97 | `reach_plan` | done | `generate_conversion_rates`, `generate_reach_forecast`, `list_plannable_locations`, `list_plannable_products`, `list_plannable_user_interests`, `list_plannable_user_lists` | generate_basic_forecast, list_locations, list_products | **Missing**: `generate_conversion_rates`, `list_plannable_user_interests`, `list_plannable_user_lists` |
| 98 | `recommendation` | done | `apply_recommendation`, `dismiss_recommendation`, `generate_recommendations` | apply, dismiss, get | **Missing**: `generate_recommendations` |
| 99 | `recommendation_subscription` | **NOT IMPL** | `mutate_recommendation_subscription` | - | Auto-apply recommendations |

### Product Integration

| # | Service | Status | v23 RPC methods | Our methods | Gap? |
|---|---------|--------|----------------|-------------|------|
| 100 | `product_link` | done | `create_product_link`, `remove_product_link` | create (merchant/ads/data_partner), remove | - |
| 101 | `product_link_invitation` | **NOT IMPL** | `create_product_link_invitation`, `remove_product_link_invitation`, `update_product_link_invitation` | - | Link invitations |
| 102 | `content_creator_insights` | **NOT IMPL** | `generate_creator_insights`, `generate_trending_insights` | - | YouTube creator data |
| 103 | `third_party_app_analytics_link` | **NOT IMPL** | `regenerate_shareable_link_id` | - | App analytics links |

### Smart Campaigns

| # | Service | Status | v23 RPC methods | Our methods | Gap? |
|---|---------|--------|----------------|-------------|------|
| 104 | `smart_campaign` (wrapper) | done | (uses `smart_campaign_suggest`) | suggest_ad, suggest_budget, suggest_keywords | Only wraps suggest service |
| 105 | `smart_campaign_setting` | **NOT IMPL** | `get_smart_campaign_status`, `mutate_smart_campaign_settings` | - | Setting management |
| 106 | `smart_campaign_suggest` | covered by wrapper | `suggest_keyword_themes`, `suggest_smart_campaign_ad`, `suggest_smart_campaign_budget_options` | - | Covered by `smart_campaign` |

### Local & Travel

| # | Service | Status | v23 RPC methods | Our methods | Gap? |
|---|---------|--------|----------------|-------------|------|
| 107 | `local_services_lead` | **NOT IMPL** | `append_lead_conversation`, `provide_lead_feedback` | - | Local services |
| 108 | `travel_asset_suggestion` | **NOT IMPL** | `suggest_travel_assets` | - | Travel vertical |

### v23-Only New Services

| # | Service | Status | v23 RPC methods | Our methods | Gap? |
|---|---------|--------|----------------|-------------|------|
| 109 | `benchmarks` | **NOT IMPL** | `generate_benchmarks_metrics`, `list_benchmarks_available_dates`, `list_benchmarks_locations`, `list_benchmarks_products`, `list_benchmarks_sources` | - | v23-only |
| 110 | `goal` | **NOT IMPL** | `mutate_goals` | - | v23-only |
| 111 | `incentive` | **NOT IMPL** | `apply_incentive`, `fetch_incentive` | - | v23-only |
| 112 | `reservation` | **NOT IMPL** | `book_campaigns`, `quote_campaigns` | - | v23-only |
| 113 | `shareable_preview` | **NOT IMPL** | `generate_shareable_previews` | - | Exists since v20 |
| 114 | `you_tube_video_upload` | **NOT IMPL** | `create_you_tube_video_upload`, `remove_you_tube_video_upload`, `update_you_tube_video_upload` | - | v23-only |

---

## Summary of Gaps in Implemented Services

These services are implemented but are missing some v23 RPC methods:

| Service | Missing RPC methods |
|---------|-------------------|
| `ad_group_ad` | `remove_automatically_created_assets` |
| `audience_insights` | `generate_audience_definition`, `generate_audience_overlap_insights`, `generate_targeting_suggestion_metrics`, `list_audience_insights_attributes`, `list_insights_eligible_dates` |
| `campaign` | `enable_p_max_brand_guidelines` (v23-new) |
| `data_link` | `remove_data_link`, `update_data_link` |
| `experiment` | `graduate_experiment`, `list_experiment_async_errors` |
| `keyword_plan_idea` | `generate_ad_group_themes`, `generate_keyword_forecast_metrics`, `generate_keyword_historical_metrics` |
| `reach_plan` | `generate_conversion_rates`, `list_plannable_user_interests`, `list_plannable_user_lists` |
| `recommendation` | `generate_recommendations` |

## Not-Implemented Services (24 total)

### Existed in v20 (should implement) - 16 services
1. `asset_group_listing_group_filter` - PMax listing group filters
2. `asset_set_asset` - Link assets to asset sets
3. `campaign_group` - Campaign grouping
4. `campaign_lifecycle_goal` - Campaign lifecycle goals
5. `content_creator_insights` - YouTube creator insights
6. `conversion_value_rule_set` - Value rule sets
7. `customer_asset_set` - Customer-level asset sets
8. `customer_lifecycle_goal` - Customer lifecycle goals
9. `customer_sk_ad_network_conversion_value_schema` - iOS SKAdNetwork
10. `keyword_theme_constant` - Smart campaign theme constants
11. `local_services_lead` - Local services leads
12. `product_link_invitation` - Product link invitations
13. `recommendation_subscription` - Auto-apply recommendations
14. `shareable_preview` - Shareable ad previews
15. `smart_campaign_setting` - Smart campaign settings
16. `third_party_app_analytics_link` - 3P app analytics
17. `travel_asset_suggestion` - Travel asset suggestions
18. `user_list_customer_type` - User list customer types

### New in v23 only - 8 services
1. `asset_generation` - AI-generated assets
2. `automatically_created_asset_removal` - Remove auto-created assets
3. `benchmarks` - Competitive benchmarking
4. `campaign_goal_config` - Campaign goal configuration
5. `goal` - Goal management
6. `incentive` - Incentive management
7. `reservation` - Reservation campaigns
8. `you_tube_video_upload` - YouTube video uploads

---

## Current Task
Auditing all services for v23 SDK compatibility. All imports are confirmed using v23. Next steps:
1. Fill method gaps in existing services (see table above)
2. Implement missing services that existed in v20
3. Optionally implement new v23-only services
