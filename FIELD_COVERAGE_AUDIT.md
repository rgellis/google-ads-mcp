# Field Coverage Audit

Comprehensive audit of every request input and response output across all 111 services.

**Completed:** 2026-04-15
**Verified:** 169 request types (665 fields), 160 response types (333 fields)

---

## Summary

- **Services with 100% input coverage**: 111 of 111
- **Input fields resolved**: 94 field-instances across 20 services — 68 added, 21 intentionally skipped (AdditionalApplicationInfo across multiple RPCs), 5 covered by shared params
- **Intentionally skipped**: `AdditionalApplicationInfo` fields (21 RPCs across 4 services)
- **Output field coverage**: 100% — all 160 response types / 333 fields returned via `serialize_proto_message` (no fields dropped)

---

## Output Field Coverage

All 160 response types (333 fields) are returned in full via `serialize_proto_message(response)`, which uses protobuf's `MessageToDict` — no output fields are dropped.

Three RPCs return void (Empty proto) so we provide status dicts instead:
- `StartIdentityVerification` — returns `{"status": "STARTED"}`
- `GraduateExperiment` — returns `{"status": "success"}`
- `RemoveAutomaticallyCreatedAssets` — returns `{"status": "success"}`

One RPC returns more than the API provides:
- `ListAccessibleCustomers` — adds convenience `customer_ids` field alongside raw `resource_names`

---

## Resolved Input Fields (94 fields across 20 services — all complete)

Every field listed below has been added to both the service class method and its MCP tool wrapper, with test coverage.

### Intentionally Skipped Fields

Some API fields are intentionally not exposed through the MCP server because they serve no purpose for MCP callers:

| Field | Services | Reason |
|-------|----------|--------|
| `insights_application_info` / `application_info` / `reach_application_info` (AdditionalApplicationInfo) | audience_insights (8 RPCs), benchmarks (5 RPCs), content_creator_insights (2 RPCs), reach_plan (6 RPCs) | Internal Google application tracking metadata. Used by Google's own tools to identify the calling application. Not relevant for third-party MCP callers. |



### 1. `asset_generation` — `src/services/assets/asset_generation_service.py` | test: `tests/test_asset_generation_service.py`

**GenerateImagesRequest:**
- [x] `freeform_generation` (FreeformImageGenerationInput) — generate images from free-text prompt **DONE**
- [x] `product_recontext_generation` (ProductRecontextGenerationImageInput) — recontextualize product images **DONE**

**GenerateTextRequest:**
- [x] `freeform_prompt` (string) — generate text from free-text prompt instead of URL **DONE**
- [x] `existing_generation_context` (AssetGenerationExistingContext) — reference existing asset group/ad **DONE**

### 2. `audience_insights` — `src/services/audiences/audience_insights_service.py` | test: `tests/test_audience_insights_service.py`

**All 8 requests:**
- [x] `customer_insights_group` (string) — user-defined grouping label **DONE**
- N/A `insights_application_info` (AdditionalApplicationInfo) — internal Google tracking field, not useful for MCP callers

**ListAudienceInsightsAttributesRequest:**
- [x] `location_country_filters` (LocationInfo) — filter SUB_COUNTRY_LOCATION by country **DONE**
- [x] `youtube_reach_location` (LocationInfo) — return YouTube reach for this market **DONE**

**GenerateAudienceCompositionInsightsRequest:**
- [x] `data_month` (string) — specific month for composition data (YYYY-MM) **DONE**

### 3. `batch_job` — `src/services/data_import/batch_job_service.py` | test: `tests/test_batch_job_service.py`

**AddBatchJobOperationsRequest:**
- [x] `sequence_token` (string) — for resumable batch uploads across multiple calls **DONE**

### 4. `benchmarks` — `src/services/planning/benchmarks_service.py` | test: `tests/test_benchmarks_service.py`

**GenerateBenchmarksMetricsRequest:**
- [x] `product_filter` (ProductFilter) — filter which products to benchmark **DONE**
- [x] `breakdown_definition` (BreakdownDefinition) — date granularity for breakdown **DONE**
- [x] `customer_benchmarks_group` (string) — user-defined grouping label **DONE**
- N/A `application_info` (AdditionalApplicationInfo) — intentionally skipped (see above)

**ListBenchmarksSourcesRequest:**
- [x] `benchmarks_sources` (BenchmarksSourceType) — filter by source type **DONE**

**All 4 list requests:**
- N/A `application_info` (AdditionalApplicationInfo) — intentionally skipped (see above)

### 5. `campaign_draft` — `src/services/campaign/campaign_draft_service.py` | test: `tests/test_campaign_draft_service.py`

**ListCampaignDraftAsyncErrorsRequest:**
- [x] `page_token` (string) — pagination token **DONE**
- [x] `page_size` (int32) — results per page **DONE**

### 6. `content_creator_insights` — `src/services/audiences/content_creator_insights_service.py` | test: `tests/test_content_creator_insights_service.py`

**GenerateCreatorInsightsRequest:**
- [x] `customer_insights_group` (string) — user-defined grouping label **DONE**
- N/A `insights_application_info` — intentionally skipped (see above)
- [x] `sub_country_locations` (LocationInfo) — sub-country location filter **DONE**
- [x] `search_attributes` — exposed as `search_audience_interests` (knowledge graph IDs) **DONE**
- [x] `search_brand` — exposed as `search_brand_names` (knowledge graph IDs) **DONE**
- [x] `search_channels` — exposed as `search_channel_ids` (YouTube channel IDs) **DONE**
- NOTE: search_channels, search_brand, search_attributes are mutually exclusive (proto oneof)

**GenerateTrendingInsightsRequest:**
- [x] `customer_insights_group` (string) — user-defined grouping label **DONE**
- N/A `insights_application_info` — intentionally skipped (see above)
- [x] `search_audience` — exposed as `search_audience_interests` (knowledge graph IDs) **DONE**
- [x] `search_topics` — exposed as `search_topic_names` (knowledge graph IDs) **DONE**
- NOTE: search_topics and search_audience are mutually exclusive (proto oneof)

### 7. `conversion_upload` — `src/services/conversions/conversion_upload_service.py` | test: `tests/test_conversion_upload_service.py`

**UploadCallConversionsRequest:**
- [x] `validate_only` (bool) — validate without uploading **DONE**

**UploadClickConversionsRequest:**
- [x] `validate_only` (bool) — validate without uploading **DONE**
- [x] `job_id` (int32) — deduplication job identifier **DONE**

### 8. `customer` — `src/services/account/customer_service.py` | test: `tests/test_customer_service.py`

**CreateCustomerClientRequest:**
- [x] `email_address` (string) — email for new customer account **DONE**
- [x] `access_role` (AccessRole) — access role for the link (ADMIN, STANDARD, READ_ONLY, EMAIL_ONLY) **DONE**

### 9. `customer_sk_ad_network` — `src/services/account/customer_sk_ad_network_service.py` | test: `tests/test_customer_sk_ad_network_service.py`

**MutateCustomerSkAdNetworkConversionValueSchemaRequest:**
- [x] `enable_warnings` (bool) — return warnings in response **DONE**

### 10. `experiment_arm` — `src/services/campaign/experiment_arm_service.py` | test: `tests/test_experiment_arm_service.py`

**MutateExperimentArmsRequest:**
- [x] `response_content_type` (ResponseContentType) — control response verbosity **DONE**

### 11. `experiment` — `src/services/campaign/experiment_service.py` | test: `tests/test_experiment_service.py`

**ListExperimentAsyncErrorsRequest:**
- [x] `page_token` (string) — pagination token **DONE**

### 12. `google_ads_field` — `src/services/metadata/google_ads_field_service.py` | test: `tests/test_google_ads_field_service.py`

**SearchGoogleAdsFieldsRequest:**
- [x] `page_token` (string) — pagination token **DONE**
- [x] `page_size` (int32) — results per page **DONE**

### 13. `incentive` — `src/services/account/incentive_service.py` | test: `tests/test_incentive_service.py`

**FetchIncentiveRequest:**
- [x] `type_` (IncentiveType) — filter by incentive type **DONE**

### 14. `invoice` — `src/services/account/invoice_service.py` | test: `tests/test_invoice_service.py`

**ListInvoicesRequest:**
- [x] `include_granular_level_invoice_details` (bool) — include campaign-level cost breakdowns **DONE**

### 15. `keyword_plan_idea` — `src/services/planning/keyword_plan_idea_service.py` | test: `tests/test_keyword_plan_idea_service.py`

**GenerateKeywordHistoricalMetricsRequest:**
- [x] `aggregate_metrics` (KeywordPlanAggregateMetrics) — aggregate metric types **DONE**
- [x] `historical_metrics_options` (HistoricalMetricsOptions) — date range and competition options **DONE**

**GenerateKeywordIdeasRequest:**
- [x] `page_token` (string) — pagination token **DONE**
- [x] `aggregate_metrics` (KeywordPlanAggregateMetrics) — aggregate metric types **DONE**
- [x] `historical_metrics_options` (HistoricalMetricsOptions) — date range and competition options **DONE**

### 16. `offline_user_data_job` — `src/services/data_import/offline_user_data_job_service.py` | test: `tests/test_offline_user_data_job_service.py`

**AddOfflineUserDataJobOperationsRequest:**
- [x] `enable_warnings` (bool) — return warnings in response **DONE**
- [x] `validate_only` (bool) — validate without executing **DONE**

**CreateOfflineUserDataJobRequest:**
- [x] `validate_only` (bool) — validate without executing **DONE**
- [x] `enable_match_rate_range_preview` (bool) — preview match rate range **DONE**

**RunOfflineUserDataJobRequest:**
- [x] `validate_only` (bool) — validate without executing **DONE**

### 17. `product_link` — `src/services/product_integration/product_link_service.py` | test: `tests/test_product_link_service.py`

**RemoveProductLinkRequest:**
- [x] `validate_only` (bool) — validate without executing **DONE**

### 18. `reach_plan` — `src/services/planning/reach_plan_service.py` | test: `tests/test_reach_plan_service.py`

**GenerateReachForecastRequest:**
- [x] `cookie_frequency_cap_setting` (FrequencyCap) — advanced frequency cap settings **DONE**
- [x] `effective_frequency_limit` (EffectiveFrequencyLimit) — effective frequency bounds **DONE**
- [x] `forecast_metric_options` (ForecastMetricOptions) — which forecast metrics to return **DONE**
- [x] `customer_reach_group` (string) — user-defined grouping label **DONE**
- N/A `reach_application_info` — intentionally skipped (see above)

**GenerateConversionRatesRequest:**
- [x] `customer_reach_group` (string) — user-defined grouping label **DONE**
- N/A `reach_application_info` — intentionally skipped (see above)

**ListPlannableLocationsRequest:**
- N/A `reach_application_info` — intentionally skipped (see above)

**ListPlannableProductsRequest:**
- N/A `reach_application_info` — intentionally skipped (see above)

**ListPlannableUserInterestsRequest:**
- [x] `path_query` (string) — filter by interest path substring **DONE**
- N/A `reach_application_info` — intentionally skipped (see above)

**ListPlannableUserListsRequest:**
- [x] `customer_reach_group` (string) — user-defined grouping label **DONE**
- N/A `reach_application_info` — intentionally skipped (see above)

### 19. `recommendation` — `src/services/planning/recommendation_service.py` | test: `tests/test_recommendation_service.py`

**ApplyRecommendationRequest:**
- [x] `partial_failure` (bool) — allow partial success **DONE**

**DismissRecommendationRequest:**
- [x] `partial_failure` (bool) — allow partial success **DONE**

**GenerateRecommendationsRequest:**
- [x] `campaign_image_asset_count` (int32) — number of image assets in campaign **DONE**
- [x] `campaign_call_asset_count` (int32) — number of call assets **DONE**
- [x] `country_codes` (string) — target country codes **DONE**
- [x] `language_codes` (string) — target language codes **DONE**
- [x] `positive_locations_ids` (int64) — included location IDs **DONE**
- [x] `negative_locations_ids` (int64) — excluded location IDs **DONE**
- [x] `asset_group_info` (AssetGroupInfo) — PMax asset groups with final_url, headline, description **DONE**
- [x] `target_partner_search_network` (bool) — target partner search network **DONE**
- [x] `target_content_network` (bool) — target content network **DONE**
- [x] `merchant_center_account_id` (int64) — linked Merchant Center account **DONE**
- [x] `is_new_customer` (bool) — whether this is a new customer **DONE**

### 20. `reservation` — `src/services/campaign/reservation_service.py` | test: `tests/test_reservation_service.py`

**BookCampaignsRequest:**
- [x] `operation` (BookCampaignsOperation) — booking operation details **DONE**

**QuoteCampaignsRequest:**
- [x] `operation` (QuoteCampaignsOperation) — quote operation details **DONE**
