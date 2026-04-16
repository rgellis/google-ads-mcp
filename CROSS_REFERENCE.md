# Cross-Reference: Google Ads API v23 Coverage Audit

Cross-references three authoritative sources to verify 1:1 coverage of all Google Ads API v23 services:

1. **Google Ads API Reference** — [developers.google.com/google-ads/api/reference/rpc/v23](https://developers.google.com/google-ads/api/reference/rpc/v23/overview)
2. **Proto definitions** — [github.com/googleapis/googleapis/.../v23/services](https://github.com/googleapis/googleapis/blob/master/google/ads/googleads/v23/services/)
3. **Installed Python SDK** — `google-ads==30.0.0` (v23 services at `google.ads.googleads.v23.services`)

**Official service list source**: [googleads_v23.yaml](https://github.com/googleapis/googleapis/blob/master/google/ads/googleads/v23/googleads_v23.yaml)

**Audit date**: 2026-04-15

---

## Summary

| Metric | Count |
|--------|-------|
| Official v23 services (from YAML) | 111 |
| Services in installed SDK | 111 |
| Our service implementations | 113 (111 official + 2 convenience wrappers) |
| Registered in main.py | 113 |
| Services with full RPC coverage | 111 |
| Services with RPC gaps | 0 |
| Convenience wrappers (not official services) | 5 |

---

## Full Service Cross-Reference

### Legend
- **Proto RPCs**: Methods defined in the `.proto` service definition (from googleapis GitHub)
- **SDK RPCs**: Methods available on the Python SDK client class
- **Our impl**: Whether we have a service file implementing these RPCs
- **Coverage**: FULL = all RPCs implemented, PARTIAL = some missing, WRAPPER = convenience alias

### Account Management

| # | Official Service | Proto RPCs | Our file | Coverage |
|---|-----------------|------------|----------|----------|
| 1 | AccountBudgetProposalService | MutateAccountBudgetProposal | `account/account_budget_proposal_service.py` | FULL |
| 2 | AccountLinkService | CreateAccountLink, MutateAccountLink | `account/account_link_service.py` | FULL |
| 3 | BillingSetupService | MutateBillingSetup | `account/billing_setup_service.py` | FULL |
| 4 | CustomerService | MutateCustomer, ListAccessibleCustomers, CreateCustomerClient | `account/customer_service.py` | FULL |
| 5 | CustomerClientLinkService | MutateCustomerClientLink | `account/customer_client_link_service.py` | FULL |
| 6 | CustomerCustomizerService | MutateCustomerCustomizers | `account/customer_customizer_service.py` | FULL |
| 7 | CustomerLabelService | MutateCustomerLabels | `account/customer_label_service.py` | FULL |
| 8 | CustomerLifecycleGoalService | ConfigureCustomerLifecycleGoals | `account/customer_lifecycle_goal_service.py` | FULL |
| 9 | CustomerManagerLinkService | MutateCustomerManagerLink, MoveManagerLink | `account/customer_manager_link_service.py` | FULL |
| 10 | CustomerSkAdNetworkConversionValueSchemaService | MutateCustomerSkAdNetworkConversionValueSchema | `account/customer_sk_ad_network_service.py` | FULL |
| 11 | CustomerUserAccessService | MutateCustomerUserAccess | `account/customer_user_access_service.py` | FULL |
| 12 | CustomerUserAccessInvitationService | MutateCustomerUserAccessInvitation | `account/customer_user_access_invitation_service.py` | FULL |
| 13 | GoalService | MutateGoals | `account/goal_service.py` | FULL |
| 14 | IdentityVerificationService | StartIdentityVerification, GetIdentityVerification | `account/identity_verification_service.py` | FULL |
| 15 | IncentiveService | FetchIncentive, ApplyIncentive | `account/incentive_service.py` | FULL |
| 16 | InvoiceService | ListInvoices | `account/invoice_service.py` | FULL |
| 17 | PaymentsAccountService | ListPaymentsAccounts | `account/payments_account_service.py` | FULL |

### Ads & Ad Groups

| # | Official Service | Proto RPCs | Our file | Coverage |
|---|-----------------|------------|----------|----------|
| 18 | AdService | MutateAds | `ad_group/ad_service.py` | FULL — uses AdGroupAdServiceClient for create/status + AdServiceClient for update_ad |
| 19 | AdGroupService | MutateAdGroups | `ad_group/ad_group_service.py` | FULL |
| 20 | AdGroupAdService | MutateAdGroupAds, RemoveAutomaticallyCreatedAssets | `ad_group/ad_group_ad_service.py` | FULL |
| 21 | AdGroupAdLabelService | MutateAdGroupAdLabels | `ad_group/ad_group_ad_label_service.py` | FULL |
| 22 | AdGroupAssetService | MutateAdGroupAssets | `ad_group/ad_group_asset_service.py` | FULL |
| 23 | AdGroupAssetSetService | MutateAdGroupAssetSets | `ad_group/ad_group_asset_set_service.py` | FULL |
| 24 | AdGroupBidModifierService | MutateAdGroupBidModifiers | `ad_group/ad_group_bid_modifier_service.py` | FULL |
| 25 | AdGroupCriterionService | MutateAdGroupCriteria | `ad_group/ad_group_criterion_service.py` | FULL |
| 26 | AdGroupCriterionCustomizerService | MutateAdGroupCriterionCustomizers | `ad_group/ad_group_criterion_customizer_service.py` | FULL |
| 27 | AdGroupCriterionLabelService | MutateAdGroupCriterionLabels | `ad_group/ad_group_criterion_label_service.py` | FULL |
| 28 | AdGroupCustomizerService | MutateAdGroupCustomizers | `ad_group/ad_group_customizer_service.py` | FULL |
| 29 | AdGroupLabelService | MutateAdGroupLabels | `ad_group/ad_group_label_service.py` | FULL |
| 30 | AdParameterService | MutateAdParameters | `ad_group/ad_parameter_service.py` | FULL |

### Assets

| # | Official Service | Proto RPCs | Our file | Coverage |
|---|-----------------|------------|----------|----------|
| 31 | AssetService | MutateAssets | `assets/asset_service.py` | FULL |
| 32 | AssetGenerationService | GenerateText, GenerateImages | `assets/asset_generation_service.py` | FULL |
| 33 | AssetGroupService | MutateAssetGroups | `assets/asset_group_service.py` | FULL |
| 34 | AssetGroupAssetService | MutateAssetGroupAssets | `assets/asset_group_asset_service.py` | FULL |
| 35 | AssetGroupListingGroupFilterService | MutateAssetGroupListingGroupFilters | `assets/asset_group_listing_group_filter_service.py` | FULL |
| 36 | AssetGroupSignalService | MutateAssetGroupSignals | `assets/asset_group_signal_service.py` | FULL |
| 37 | AssetSetService | MutateAssetSets | `assets/asset_set_service.py` | FULL |
| 38 | AssetSetAssetService | MutateAssetSetAssets | `assets/asset_set_asset_service.py` | FULL |
| 39 | AutomaticallyCreatedAssetRemovalService | RemoveCampaignAutomaticallyCreatedAsset | `campaign/automatically_created_asset_removal_service.py` | FULL |
| 40 | CustomerAssetService | MutateCustomerAssets | `assets/customer_asset_service.py` | FULL |
| 41 | CustomerAssetSetService | MutateCustomerAssetSets | `assets/customer_asset_set_service.py` | FULL |
| 42 | YouTubeVideoUploadService | CreateYouTubeVideoUpload, UpdateYouTubeVideoUpload, RemoveYouTubeVideoUpload | `assets/youtube_video_upload_service.py` | FULL |

### Audiences & Targeting

| # | Official Service | Proto RPCs | Our file | Coverage |
|---|-----------------|------------|----------|----------|
| 43 | AudienceService | MutateAudiences | `audiences/audience_service.py` | FULL |
| 44 | AudienceInsightsService | GenerateInsightsFinderReport, ListAudienceInsightsAttributes, ListInsightsEligibleDates, GenerateAudienceCompositionInsights, GenerateAudienceDefinition, GenerateSuggestedTargetingInsights, GenerateAudienceOverlapInsights, GenerateTargetingSuggestionMetrics | `audiences/audience_insights_service.py` | FULL |
| 45 | ContentCreatorInsightsService | GenerateCreatorInsights, GenerateTrendingInsights | `audiences/content_creator_insights_service.py` | FULL |
| 46 | CustomAudienceService | MutateCustomAudiences | `audiences/custom_audience_service.py` | FULL |
| 47 | CustomInterestService | MutateCustomInterests | `audiences/custom_interest_service.py` | FULL |
| 48 | CustomerNegativeCriterionService | MutateCustomerNegativeCriteria | `targeting/customer_negative_criterion_service.py` | FULL |
| 49 | GeoTargetConstantService | SuggestGeoTargetConstants | `targeting/geo_target_constant_service.py` | FULL |
| 50 | RemarketingActionService | MutateRemarketingActions | `audiences/remarketing_action_service.py` | FULL |
| 51 | UserListService | MutateUserLists | `audiences/user_list_service.py` | FULL |
| 52 | UserListCustomerTypeService | MutateUserListCustomerTypes | `audiences/user_list_customer_type_service.py` | FULL |

### Bidding & Budgets

| # | Official Service | Proto RPCs | Our file | Coverage |
|---|-----------------|------------|----------|----------|
| 53 | BiddingDataExclusionService | MutateBiddingDataExclusions | `bidding/bidding_data_exclusion_service.py` | FULL |
| 54 | BiddingSeasonalityAdjustmentService | MutateBiddingSeasonalityAdjustments | `bidding/bidding_seasonality_adjustment_service.py` | FULL |
| 55 | BiddingStrategyService | MutateBiddingStrategies | `bidding/bidding_strategy_service.py` | FULL |
| 56 | CampaignBudgetService | MutateCampaignBudgets | `bidding/budget_service.py` (wrapper name) | FULL |

### Campaigns

| # | Official Service | Proto RPCs | Our file | Coverage |
|---|-----------------|------------|----------|----------|
| 57 | CampaignService | MutateCampaigns, EnablePMaxBrandGuidelines | `campaign/campaign_service.py` | FULL |
| 58 | CampaignAssetService | MutateCampaignAssets | `campaign/campaign_asset_service.py` | FULL |
| 59 | CampaignAssetSetService | MutateCampaignAssetSets | `campaign/campaign_asset_set_service.py` | FULL |
| 60 | CampaignBidModifierService | MutateCampaignBidModifiers | `campaign/campaign_bid_modifier_service.py` | FULL |
| 61 | CampaignConversionGoalService | MutateCampaignConversionGoals | `campaign/campaign_conversion_goal_service.py` | FULL |
| 62 | CampaignCriterionService | MutateCampaignCriteria | `campaign/campaign_criterion_service.py` | FULL |
| 63 | CampaignCustomizerService | MutateCampaignCustomizers | `campaign/campaign_customizer_service.py` | FULL |
| 64 | CampaignDraftService | MutateCampaignDrafts, PromoteCampaignDraft, ListCampaignDraftAsyncErrors | `campaign/campaign_draft_service.py` | FULL |
| 65 | CampaignGoalConfigService | MutateCampaignGoalConfigs | `campaign/campaign_goal_config_service.py` | FULL |
| 66 | CampaignGroupService | MutateCampaignGroups | `campaign/campaign_group_service.py` | FULL |
| 67 | CampaignLabelService | MutateCampaignLabels | `campaign/campaign_label_service.py` | FULL |
| 68 | CampaignLifecycleGoalService | ConfigureCampaignLifecycleGoals | `campaign/campaign_lifecycle_goal_service.py` | FULL |
| 69 | CampaignSharedSetService | MutateCampaignSharedSets | `campaign/campaign_shared_set_service.py` | FULL |
| 70 | ReservationService | QuoteCampaigns, BookCampaigns | `campaign/reservation_service.py` | FULL |
| 71 | SmartCampaignSettingService | GetSmartCampaignStatus, MutateSmartCampaignSettings | `campaign/smart_campaign_setting_service.py` | FULL |
| 72 | SmartCampaignSuggestService | SuggestSmartCampaignBudgetOptions, SuggestSmartCampaignAd, SuggestKeywordThemes | `campaign/smart_campaign_service.py` (wrapper name) | FULL |

### Conversions

| # | Official Service | Proto RPCs | Our file | Coverage |
|---|-----------------|------------|----------|----------|
| 73 | ConversionActionService | MutateConversionActions | `conversions/conversion_service.py` (wrapper name) | FULL |
| 74 | ConversionAdjustmentUploadService | UploadConversionAdjustments | `conversions/conversion_adjustment_upload_service.py` | FULL |
| 75 | ConversionCustomVariableService | MutateConversionCustomVariables | `conversions/conversion_custom_variable_service.py` | FULL |
| 76 | ConversionGoalCampaignConfigService | MutateConversionGoalCampaignConfigs | `conversions/conversion_goal_campaign_config_service.py` | FULL |
| 77 | ConversionUploadService | UploadClickConversions, UploadCallConversions | `conversions/conversion_upload_service.py` | FULL |
| 78 | ConversionValueRuleService | MutateConversionValueRules | `conversions/conversion_value_rule_service.py` | FULL |
| 79 | ConversionValueRuleSetService | MutateConversionValueRuleSets | `conversions/conversion_value_rule_set_service.py` | FULL |
| 80 | CustomConversionGoalService | MutateCustomConversionGoals | `conversions/custom_conversion_goal_service.py` | FULL |
| 81 | CustomerConversionGoalService | MutateCustomerConversionGoals | `conversions/customer_conversion_goal_service.py` | FULL |

### Data Import & Jobs

| # | Official Service | Proto RPCs | Our file | Coverage |
|---|-----------------|------------|----------|----------|
| 82 | BatchJobService | MutateBatchJob, ListBatchJobResults, RunBatchJob, AddBatchJobOperations | `data_import/batch_job_service.py` | FULL |
| 83 | DataLinkService | CreateDataLink, RemoveDataLink, UpdateDataLink | `data_import/data_link_service.py` | FULL |
| 84 | LocalServicesLeadService | AppendLeadConversation, ProvideLeadFeedback | `data_import/local_services_lead_service.py` | FULL |
| 85 | OfflineUserDataJobService | CreateOfflineUserDataJob, AddOfflineUserDataJobOperations, RunOfflineUserDataJob | `data_import/offline_user_data_job_service.py` | FULL |
| 86 | UserDataService | UploadUserData | `data_import/user_data_service.py` | FULL |

### Experiments

| # | Official Service | Proto RPCs | Our file | Coverage |
|---|-----------------|------------|----------|----------|
| 87 | ExperimentService | MutateExperiments, EndExperiment, ListExperimentAsyncErrors, GraduateExperiment, ScheduleExperiment, PromoteExperiment | `campaign/experiment_service.py` | FULL |
| 88 | ExperimentArmService | MutateExperimentArms | `campaign/experiment_arm_service.py` | FULL |

### Metadata & Search

| # | Official Service | Proto RPCs | Our file | Coverage |
|---|-----------------|------------|----------|----------|
| 89 | GoogleAdsService | Search, SearchStream, Mutate | `metadata/google_ads_service.py` | FULL |
| 90 | GoogleAdsFieldService | GetGoogleAdsField, SearchGoogleAdsFields | `metadata/google_ads_field_service.py` | FULL |
| 91 | ShareablePreviewService | GenerateShareablePreviews | `metadata/shareable_preview_service.py` | FULL |

### Labels & Organization

| # | Official Service | Proto RPCs | Our file | Coverage |
|---|-----------------|------------|----------|----------|
| 92 | LabelService | MutateLabels | `shared/label_service.py` | FULL |
| 93 | SharedSetService | MutateSharedSets | `shared/shared_set_service.py` | FULL |
| 94 | SharedCriterionService | MutateSharedCriteria | `shared/shared_criterion_service.py` | FULL |
| 95 | CustomizerAttributeService | MutateCustomizerAttributes | `shared/customizer_attribute_service.py` | FULL |

### Planning & Research

| # | Official Service | Proto RPCs | Our file | Coverage |
|---|-----------------|------------|----------|----------|
| 96 | BenchmarksService | GenerateBenchmarksMetrics, ListBenchmarksAvailableDates, ListBenchmarksLocations, ListBenchmarksProducts, ListBenchmarksSources | `planning/benchmarks_service.py` | FULL |
| 97 | BrandSuggestionService | SuggestBrands | `planning/brand_suggestion_service.py` | FULL |
| 98 | KeywordPlanService | MutateKeywordPlans | `planning/keyword_plan_service.py` | FULL |
| 99 | KeywordPlanAdGroupService | MutateKeywordPlanAdGroups | `planning/keyword_plan_ad_group_service.py` | FULL |
| 100 | KeywordPlanAdGroupKeywordService | MutateKeywordPlanAdGroupKeywords | `planning/keyword_plan_ad_group_keyword_service.py` | FULL |
| 101 | KeywordPlanCampaignService | MutateKeywordPlanCampaigns | `planning/keyword_plan_campaign_service.py` | FULL |
| 102 | KeywordPlanCampaignKeywordService | MutateKeywordPlanCampaignKeywords | `planning/keyword_plan_campaign_keyword_service.py` | FULL |
| 103 | KeywordPlanIdeaService | GenerateKeywordIdeas, GenerateKeywordHistoricalMetrics, GenerateAdGroupThemes, GenerateKeywordForecastMetrics | `planning/keyword_plan_idea_service.py` | FULL |
| 104 | KeywordThemeConstantService | SuggestKeywordThemeConstants | `planning/keyword_theme_constant_service.py` | FULL |
| 105 | ReachPlanService | GenerateConversionRates, ListPlannableLocations, ListPlannableProducts, GenerateReachForecast, ListPlannableUserLists, ListPlannableUserInterests | `planning/reach_plan_service.py` | FULL |
| 106 | RecommendationService | ApplyRecommendation, DismissRecommendation, GenerateRecommendations | `planning/recommendation_service.py` | FULL |
| 107 | RecommendationSubscriptionService | MutateRecommendationSubscription | `planning/recommendation_subscription_service.py` | FULL |
| 108 | TravelAssetSuggestionService | SuggestTravelAssets | `planning/travel_asset_suggestion_service.py` | FULL |

### Product Integration

| # | Official Service | Proto RPCs | Our file | Coverage |
|---|-----------------|------------|----------|----------|
| 109 | ProductLinkService | CreateProductLink, RemoveProductLink | `product_integration/product_link_service.py` | FULL |
| 110 | ProductLinkInvitationService | CreateProductLinkInvitation, UpdateProductLinkInvitation, RemoveProductLinkInvitation | `product_integration/product_link_invitation_service.py` | FULL |
| 111 | ThirdPartyAppAnalyticsLinkService | RegenerateShareableLinkId | `product_integration/third_party_app_analytics_link_service.py` | FULL |

---

## Convenience Wrappers (not official services)

These files provide user-friendly wrappers around existing SDK services:

| Our file | Wraps | Purpose |
|----------|-------|---------|
| `bidding/budget_service.py` | CampaignBudgetService | Friendlier name |
| `conversions/conversion_service.py` | ConversionActionService | Friendlier name |
| `ad_group/keyword_service.py` | AdGroupCriterionService | Keyword-specific subset |
| `metadata/search_service.py` | GoogleAdsService | Convenience GAQL queries |
| `campaign/smart_campaign_service.py` | SmartCampaignSuggestService | Wrapper for suggest RPCs |

---

## Name Mapping (our file name differs from official)

| Official SDK service name | Our file name | Reason |
|--------------------------|---------------|--------|
| `campaign_budget_service` | `budget_service.py` | Shorter name |
| `conversion_action_service` | `conversion_service.py` | Shorter name |
| `customer_sk_ad_network_conversion_value_schema_service` | `customer_sk_ad_network_service.py` | Name too long |
| `smart_campaign_suggest_service` | `smart_campaign_service.py` | Groups suggest operations |
| `you_tube_video_upload_service` | `youtube_video_upload_service.py` | Normalized naming |

---

## Gaps & Checklist

### RPC Coverage Gaps

None. All 111 services have full RPC coverage.

The `AdService` uses both `AdGroupAdServiceClient` (for create/remove/status — ads must be
associated with an ad group) and `AdServiceClient.mutate_ads` (for updating ad content like
headlines, descriptions, URLs). This is the correct architecture per Google's API design.

### Verified: No Missing Services

All 111 official Google Ads API v23 services from the [googleads_v23.yaml](https://github.com/googleapis/googleapis/blob/master/google/ads/googleads/v23/googleads_v23.yaml) have corresponding implementation files. Every RPC method defined in the proto service definitions is covered (except the AdService gap noted above).

### Sources Verified

| Source | URL | Services Found |
|--------|-----|---------------|
| Official YAML | `googleapis/googleapis/.../googleads_v23.yaml` | 111 |
| Proto definitions | `googleapis/googleapis/.../v23/services/*.proto` | 111 (each with RPC definitions) |
| Installed SDK | `google-ads==30.0.0` (`v23/services/services/`) | 111 |
| Our implementation | `src/services/**/*_service.py` | 113 (111 + 2 extra wrappers) |
| Registered in main.py | `SERVER_GROUPS` entries | 113 |
