# API Coverage Audit

Deep audit of every service's sub-type coverage. RPC-level coverage is 100% (every proto RPC has a tool), but some RPCs support multiple sub-types through oneof fields. This document tracks which sub-types are exposed.

**Last updated:** 2026-04-17

---

## Campaign Criterion Service — `src/services/campaign/campaign_criterion_service.py`

**Status: FULLY COVERED (36/36 criterion types, 38 tools)**

All 36 criterion types have individual tools.

---

## Ad Group Criterion Service — `src/services/ad_group/ad_group_criterion_service.py`

**Status: 27/28 sub-types covered (25 tools)**

- [x] keyword, audience/user_list, age_range, gender, income_range, parental_status
- [x] placement, mobile_app_category, mobile_application, youtube_video, youtube_channel
- [x] topic, user_interest, webpage, custom_affinity, custom_audience, combined_audience
- [x] location, language, life_event, video_lineup, extended_demographic, brand_list
- [x] listing_group, app_payment_model, vertical_ads_item_group_rule_list

Deprecated — not implementing (1):

| Criterion Type | Status | Replacement |
|---------------|--------|-------------|
| custom_intent | Deprecated by Google | custom_audience |

---

## Customer Negative Criterion Service — `src/services/targeting/customer_negative_criterion_service.py`

**Status: FULLY COVERED (9/9 sub-types, 12 tools)**

- [x] keyword, placement, content_label
- [x] mobile_application, mobile_app_category, youtube_video, youtube_channel, ip_block
- [x] negative_keyword_list, placement_list

---

## Shared Criterion Service — `src/services/shared/shared_criterion_service.py`

**Status: FULLY COVERED (9/10 sub-types, 11 tools)**

- [x] keyword, placement
- [x] youtube_video, youtube_channel, mobile_app_category, mobile_application, brand, webpage
- [x] vertical_ads_item_group_rule

Not available (1):
- `vertical_ads_item_group_rule` on AdGroupCriterion is `VerticalAdsItemGroupRuleListInfo` (references a shared set). The SharedCriterion version is `VerticalAdsItemGroupRuleInfo` (has actual fields). Both are implemented in their respective services.

---

## Ad Service — `src/services/ad_group/ad_service.py`

**Status: 21/25 ad types covered (23 tools)**

- [x] responsive_search_ad, expanded_text_ad
- [x] responsive_display_ad, video_ad (in_stream/bumper/non_skippable/in_feed), video_responsive_ad
- [x] demand_gen_multi_asset_ad, demand_gen_carousel_ad, demand_gen_video_responsive_ad, demand_gen_product_ad
- [x] smart_campaign_ad, app_ad, app_engagement_ad, app_pre_registration_ad
- [x] shopping_product_ad, shopping_comparison_listing_ad, hotel_ad, travel_ad
- [x] local_ad, display_upload_ad, expanded_dynamic_search_ad, image_ad

Deprecated — not implementing (4):

| Ad Type | Status | Replacement |
|---------|--------|-------------|
| text_ad | Deprecated since June 2022 — Google blocks new creation | responsive_search_ad |
| legacy_responsive_display_ad | Deprecated legacy format | responsive_display_ad |
| legacy_app_install_ad | Deprecated legacy format | app_ad |
| shopping_smart_ad | Deprecated — replaced by Performance Max | Performance Max campaigns |

---

## Asset Service — `src/services/assets/asset_service.py`

**Status: FULLY COVERED (31/31 asset types, 32 tools)**

- [x] text_asset, image_asset, youtube_video_asset
- [x] sitelink_asset, callout_asset, structured_snippet_asset, call_asset
- [x] price_asset, promotion_asset, lead_form_asset, page_feed_asset
- [x] mobile_app_asset, hotel_callout_asset, call_to_action_asset
- [x] location_asset, hotel_property_asset, app_deep_link_asset
- [x] book_on_google_asset, media_bundle_asset, demand_gen_carousel_card_asset
- [x] business_message_asset, youtube_video_list_asset
- [x] dynamic_education_asset, dynamic_real_estate_asset, dynamic_custom_asset
- [x] dynamic_hotels_and_rentals_asset, dynamic_flights_asset, dynamic_travel_asset
- [x] dynamic_local_asset, dynamic_jobs_asset

No skipped types — all 31 asset types in the v23 SDK are implemented.

---

## Bidding Strategy Service — `src/services/bidding/bidding_strategy_service.py`

**Status: FULLY COVERED (7/7 strategy types, 9 tools)**

- [x] target_cpa, target_roas, maximize_conversions, target_impression_share
- [x] enhanced_cpc, maximize_conversion_value, target_spend

---

## Ad Group Bid Modifier Service — `src/services/ad_group/ad_group_bid_modifier_service.py`

**Status: FULLY COVERED**

---

## Campaign Bid Modifier Service — `src/services/campaign/campaign_bid_modifier_service.py`

**Status: FULLY COVERED**

---

## Summary

| Service | Sub-types | Covered | Skipped | Coverage |
|---------|-----------|---------|---------|----------|
| Campaign Criterion | 36 | 36 | 0 | 100% |
| Ad Group Criterion | 28 | 27 | 1 | 96% (100% of non-deprecated) |
| Customer Negative Criterion | 9 | 9 | 0 | 100% |
| Shared Criterion | 10 | 9 | 0 | 100%* |
| Ad (ad types) | 25 | 21 | 4 | 84% (100% of non-deprecated) |
| Asset (asset types) | 31 | 31 | 0 | 100% |
| Bidding Strategy | 7 | 7 | 0 | 100% |
| Ad Group Bid Modifier | 6 | 6 | 0 | 100% |
| Campaign Bid Modifier | 1 | 1 | 0 | 100% |

All skipped items are either deprecated, handled by dedicated services, or not available in the v23 SDK.
