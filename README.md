# Google Ads MCP Server

An unofficial Model Context Protocol (MCP) server that wraps the entire Google Ads API v23, enabling LLMs to manage Google Ads accounts through chat and voice interfaces.

## Overview

This project provides a fully typed MCP server built on the official Google Ads Python SDK (`google-ads==30.0.0`). It exposes every Google Ads API v23 service as MCP tools that LLMs can discover, select, and invoke through natural language.

The server is designed for chat and voice interaction — all tool parameters use simple strings and numbers (not complex proto types), with enum values documented in every tool description so the LLM knows what values to pass.

## Key Numbers

| Metric | Count |
|--------|-------|
| Google Ads API v23 services | 111 |
| Service implementations | 113 (111 official + 2 convenience wrappers) |
| RPC method coverage | 100% — every proto RPC implemented |
| Input field coverage | 100% — 665 fields across 169 request types |
| Output field coverage | 100% — 333 fields across 160 response types |
| Test coverage | 100% — 113 test files covering all 113 services (837 tests) |
| Type errors (pyright) | 0 |

## Architecture

```
main.py                          # Entry point, SERVER_GROUPS, --groups CLI
src/
  servers/                       # 12 domain modules (core, assets, targeting, ...)
    __init__.py                  # create_server() factory
    core.py                      # campaign, budget, ad group, keyword, ad, conversion, search
    assets.py                    # assets, asset groups, asset sets, YouTube upload
    targeting.py                 # criteria, geo targeting, audiences, user lists
    bidding.py                   # strategies, bid modifiers, exclusions
    planning.py                  # keyword plans, reach plans, benchmarks
    experiments.py               # experiments, arms, drafts
    reporting.py                 # search, field metadata, recommendations, insights
    conversion.py                # uploads, value rules, goals, remarketing
    organization.py              # labels, shared sets
    customizers.py               # customizer attributes, ad parameters
    account.py                   # user access, linking, billing, identity
    other.py                     # smart campaigns, batch jobs, reservations
  services/                      # 113 service files, one per API service
    account/                     # 17 services
    ad_group/                    # 14 services
    assets/                      # 11 services
    audiences/                   # 8 services
    bidding/                     # 4 services
    campaign/                    # 19 services
    conversions/                 # 9 services
    data_import/                 # 5 services
    metadata/                    # 4 services
    planning/                    # 13 services
    product_integration/         # 3 services
    shared/                      # 4 services
    targeting/                   # 2 services
  sdk_client.py                  # Google Ads SDK client wrapper
  utils.py                       # format_customer_id, serialize_proto_message, set_request_options
tests/                           # 113 test files, one per service
```

### Service Pattern

Every service follows the same architecture:

```python
class FooService:
    def __init__(self) -> None:
        self._client: Optional[FooServiceClient] = None

    @property
    def client(self) -> FooServiceClient:
        # Lazy initialization — SDK client created on first use
        ...

    async def do_something(self, ctx: Context, customer_id: str, ...) -> Dict[str, Any]:
        try:
            customer_id = format_customer_id(customer_id)
            # Build request using generated proto types
            response = self.client.mutate_foo(request=request)
            await ctx.log(level="info", message="...")
            return serialize_proto_message(response)
        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to ...: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

def create_foo_tools(service: FooService) -> List[Callable]:
    # Thin wrappers that convert string enums to SDK enums
    # Docstrings here are what the LLM sees as tool descriptions
    async def do_something(ctx: Context, customer_id: str, ...) -> Dict[str, Any]:
        """Do something. <-- LLM reads this to decide when to use the tool

        Args:
            customer_id: The customer ID
            status: ENABLED, PAUSED, or REMOVED  <-- LLM reads valid values
        """
        status_enum = getattr(StatusEnum.Status, status)
        return await service.do_something(ctx=ctx, ..., status=status_enum)
    return [do_something]

def register_foo_tools(mcp: FastMCP[Any]) -> FooService:
    service = FooService()
    for tool in create_foo_tools(service):
        mcp.tool(tool)
    return service
```

### Server Groups

Servers are organized into groups that can be selectively mounted at startup:

```bash
uv run main.py                           # Mount core group only (default)
uv run main.py --groups all              # Mount all 113 servers
uv run main.py --groups core,assets      # Mount specific groups
```

Available groups: `core`, `assets`, `targeting`, `bidding`, `planning`, `experiments`, `reporting`, `conversion`, `organization`, `customizers`, `account`, `other`.

## Installation

```bash
git clone https://github.com/rgellis/google-ads-mcp.git
cd google-ads-mcp

# Install dependencies using uv
uv sync

# Set up Google Ads credentials
export GOOGLE_ADS_DEVELOPER_TOKEN="your_developer_token"
export GOOGLE_ADS_CLIENT_ID="your_client_id"
export GOOGLE_ADS_CLIENT_SECRET="your_client_secret"
export GOOGLE_ADS_REFRESH_TOKEN="your_refresh_token"
```

## Service Coverage

All 111 official Google Ads API v23 services are implemented with full RPC coverage. Plus 2 convenience wrappers (`keyword` wrapping `ad_group_criterion`, `search` wrapping `google_ads`) for common operations.

### Account Management (17 services)

| Service | RPCs | Notes |
|---------|------|-------|
| AccountBudgetProposalService | MutateAccountBudgetProposal | Budget proposals for managed accounts |
| AccountLinkService | CreateAccountLink, MutateAccountLink | Third-party account linking |
| BillingSetupService | MutateBillingSetup | Billing configuration, create/remove |
| CustomerService | MutateCustomer, ListAccessibleCustomers, CreateCustomerClient | Account info and sub-account creation |
| CustomerClientLinkService | MutateCustomerClientLink | Manager-client linking |
| CustomerCustomizerService | MutateCustomerCustomizers | Account-level ad customizers |
| CustomerLabelService | MutateCustomerLabels | Account label associations |
| CustomerLifecycleGoalService | ConfigureCustomerLifecycleGoals | Acquisition/retention optimization |
| CustomerManagerLinkService | MutateCustomerManagerLink, MoveManagerLink | Manager link management |
| CustomerSkAdNetworkService | MutateCustomerSkAdNetworkConversionValueSchema | iOS SKAdNetwork schema |
| CustomerUserAccessService | MutateCustomerUserAccess | User access management |
| CustomerUserAccessInvitationService | MutateCustomerUserAccessInvitation | Access invitations |
| GoalService | MutateGoals | Account-level conversion goals |
| IdentityVerificationService | GetIdentityVerification, StartIdentityVerification | Identity verification |
| IncentiveService | FetchIncentive, ApplyIncentive | Promotional ad credits |
| InvoiceService | ListInvoices | Billing invoices |
| PaymentsAccountService | ListPaymentsAccounts | Payments account info |

### Campaign Management (19 services)

| Service | RPCs | Notes |
|---------|------|-------|
| CampaignService | MutateCampaigns, EnablePMaxBrandGuidelines | Campaign CRUD + PMax branding |
| CampaignAssetService | MutateCampaignAssets | Campaign asset linking |
| CampaignAssetSetService | MutateCampaignAssetSets | Campaign asset set linking |
| CampaignBidModifierService | MutateCampaignBidModifiers | Device/interaction bid adjustments |
| CampaignConversionGoalService | MutateCampaignConversionGoals | Campaign conversion goals |
| CampaignCriterionService | MutateCampaignCriteria | Location, language, device targeting |
| CampaignCustomizerService | MutateCampaignCustomizers | Campaign-level customizers |
| CampaignDraftService | MutateCampaignDrafts, PromoteCampaignDraft, ListCampaignDraftAsyncErrors | Draft campaigns |
| CampaignGoalConfigService | MutateCampaignGoalConfigs | Campaign goal configuration |
| CampaignGroupService | MutateCampaignGroups | Campaign grouping |
| CampaignLabelService | MutateCampaignLabels | Campaign label associations |
| CampaignLifecycleGoalService | ConfigureCampaignLifecycleGoals | Acquisition/retention goals |
| CampaignSharedSetService | MutateCampaignSharedSets | Shared negative list linking |
| ExperimentService | MutateExperiments, EndExperiment, GraduateExperiment, ListExperimentAsyncErrors, PromoteExperiment, ScheduleExperiment | A/B testing |
| ExperimentArmService | MutateExperimentArms | Experiment variants |
| ReservationService | QuoteCampaigns, BookCampaigns | Guaranteed reach campaigns |
| SmartCampaignService | SuggestSmartCampaignAd, SuggestSmartCampaignBudgetOptions, SuggestKeywordThemes | AI-powered campaign setup |
| SmartCampaignSettingService | GetSmartCampaignStatus, MutateSmartCampaignSettings | Smart campaign settings |
| AutomaticallyCreatedAssetRemovalService | RemoveCampaignAutomaticallyCreatedAsset | Remove auto-created assets |

### Ad Groups & Ads (14 services)

| Service | RPCs | Notes |
|---------|------|-------|
| AdGroupService | MutateAdGroups | Ad group CRUD |
| AdGroupAdService | MutateAdGroupAds, RemoveAutomaticallyCreatedAssets | Ad-to-group associations |
| AdService | MutateAds | Ad content updates (headlines, descriptions) |
| AdGroupAssetService | MutateAdGroupAssets | Ad group asset linking |
| AdGroupAssetSetService | MutateAdGroupAssetSets | Ad group asset set linking |
| AdGroupBidModifierService | MutateAdGroupBidModifiers | Hotel/device bid adjustments |
| AdGroupCriterionService | MutateAdGroupCriteria | Keywords, audiences, demographics |
| AdGroupCriterionCustomizerService | MutateAdGroupCriterionCustomizers | Criterion-level customizers |
| AdGroupCriterionLabelService | MutateAdGroupCriterionLabels | Criterion label associations |
| AdGroupCustomizerService | MutateAdGroupCustomizers | Ad group customizers |
| AdGroupLabelService | MutateAdGroupLabels | Ad group label associations |
| AdParameterService | MutateAdParameters | Dynamic numeric ad values |
| KeywordService (wrapper) | via AdGroupCriterionService | Keyword-specific convenience |

### Assets (11 services)

| Service | RPCs | Notes |
|---------|------|-------|
| AssetService | MutateAssets | Text, image, video assets |
| AssetGenerationService | GenerateImages, GenerateText | AI-generated assets |
| AssetGroupService | MutateAssetGroups | Performance Max asset groups |
| AssetGroupAssetService | MutateAssetGroupAssets | Asset-to-group linking |
| AssetGroupListingGroupFilterService | MutateAssetGroupListingGroupFilters | PMax product feed filters |
| AssetGroupSignalService | MutateAssetGroupSignals | Audience/search signals |
| AssetSetService | MutateAssetSets | Asset set management |
| AssetSetAssetService | MutateAssetSetAssets | Asset-to-set linking |
| CustomerAssetService | MutateCustomerAssets | Account-level assets |
| CustomerAssetSetService | MutateCustomerAssetSets | Account-level asset sets |
| YouTubeVideoUploadService | CreateYouTubeVideoUpload, UpdateYouTubeVideoUpload, RemoveYouTubeVideoUpload | Video uploads via Ads API |

### Audiences & Targeting (10 services)

| Service | RPCs | Notes |
|---------|------|-------|
| AudienceService | MutateAudiences | Combined audiences |
| AudienceInsightsService | 8 RPCs | Audience analysis and insights |
| ContentCreatorInsightsService | GenerateCreatorInsights, GenerateTrendingInsights | YouTube creator data |
| CustomAudienceService | MutateCustomAudiences | Custom segments |
| CustomInterestService | MutateCustomInterests | Affinity/intent audiences |
| UserListService | MutateUserLists | Remarketing lists |
| UserListCustomerTypeService | MutateUserListCustomerTypes | Customer type classifications |
| RemarketingActionService | MutateRemarketingActions | Remarketing tags |
| CustomerNegativeCriterionService | MutateCustomerNegativeCriteria | Account-level exclusions |
| GeoTargetConstantService | SuggestGeoTargetConstants | Geographic targeting lookup |

### Bidding & Budget (5 services)

| Service | RPCs | Notes |
|---------|------|-------|
| BudgetService (wrapper) | MutateCampaignBudgets | Budget management |
| BiddingStrategyService | MutateBiddingStrategies | Target CPA, ROAS, etc. |
| BiddingDataExclusionService | MutateBiddingDataExclusions | Exclude data from bidding |
| BiddingSeasonalityAdjustmentService | MutateBiddingSeasonalityAdjustments | Seasonal bid adjustments |
| CampaignBidModifierService | MutateCampaignBidModifiers | Campaign-level bid modifiers |
| AdGroupBidModifierService | MutateAdGroupBidModifiers | Ad group-level bid modifiers |

### Conversions (11 services)

| Service | RPCs | Notes |
|---------|------|-------|
| ConversionService (wrapper) | MutateConversionActions | Conversion action CRUD |
| ConversionUploadService | UploadClickConversions, UploadCallConversions | Offline conversion uploads |
| ConversionAdjustmentUploadService | UploadConversionAdjustments | Restate/retract conversions |
| ConversionValueRuleService | MutateConversionValueRules | Value adjustment rules |
| ConversionValueRuleSetService | MutateConversionValueRuleSets | Rule set grouping |
| ConversionCustomVariableService | MutateConversionCustomVariables | Custom conversion variables |
| ConversionGoalCampaignConfigService | MutateConversionGoalCampaignConfigs | Campaign goal config |
| CustomConversionGoalService | MutateCustomConversionGoals | Custom conversion goals |
| CustomerConversionGoalService | MutateCustomerConversionGoals | Account conversion goals |
| CampaignConversionGoalService | MutateCampaignConversionGoals | Campaign conversion goals |

### Planning & Research (13 services)

| Service | RPCs | Notes |
|---------|------|-------|
| KeywordPlanService | MutateKeywordPlans | Keyword plan CRUD |
| KeywordPlanIdeaService | 4 RPCs | Keyword ideas and forecasts |
| KeywordPlanAdGroupService | MutateKeywordPlanAdGroups | Plan ad groups |
| KeywordPlanCampaignService | MutateKeywordPlanCampaigns | Plan campaigns |
| KeywordPlanAdGroupKeywordService | MutateKeywordPlanAdGroupKeywords | Plan keywords |
| KeywordPlanCampaignKeywordService | MutateKeywordPlanCampaignKeywords | Plan negative keywords |
| ReachPlanService | 6 RPCs | Reach and frequency planning |
| BenchmarksService | 5 RPCs | Competitive benchmarking |
| BrandSuggestionService | SuggestBrands | Brand name suggestions |
| KeywordThemeConstantService | SuggestKeywordThemeConstants | Smart campaign themes |
| TravelAssetSuggestionService | SuggestTravelAssets | Travel campaign assets |
| RecommendationService | ApplyRecommendation, DismissRecommendation, GenerateRecommendations | Optimization recommendations |
| RecommendationSubscriptionService | MutateRecommendationSubscription | Auto-apply recommendations |

### Data Import (5 services)

| Service | RPCs | Notes |
|---------|------|-------|
| BatchJobService | MutateBatchJob, AddBatchJobOperations, RunBatchJob, ListBatchJobResults | Bulk operations |
| OfflineUserDataJobService | CreateOfflineUserDataJob, AddOfflineUserDataJobOperations, RunOfflineUserDataJob | Customer match |
| UserDataService | UploadUserData | Enhanced conversions |
| LocalServicesLeadService | AppendLeadConversation, ProvideLeadFeedback | Local Services Ads |
| DataLinkService | CreateDataLink, RemoveDataLink, UpdateDataLink | Third-party data links |

### Metadata & Reporting (7 services)

| Service | RPCs | Notes |
|---------|------|-------|
| GoogleAdsService | Mutate, Search, SearchStream | GAQL queries and multi-resource mutations |
| GoogleAdsFieldService | GetGoogleAdsField, SearchGoogleAdsFields | Field metadata discovery |
| SearchService (wrapper) | via GoogleAdsService | Convenience GAQL search |
| ShareablePreviewService | GenerateShareablePreviews | Ad preview URLs |

### Organization (7 services)

| Service | RPCs | Notes |
|---------|------|-------|
| LabelService | MutateLabels | Label CRUD |
| SharedSetService | MutateSharedSets | Shared negative lists |
| SharedCriterionService | MutateSharedCriteria | Shared list entries |
| CustomizerAttributeService | MutateCustomizerAttributes | Customizer definitions |

### Product Integration (3 services)

| Service | RPCs | Notes |
|---------|------|-------|
| ProductLinkService | CreateProductLink, RemoveProductLink | Merchant Center, Google Ads linking |
| ProductLinkInvitationService | CreateProductLinkInvitation, RemoveProductLinkInvitation, UpdateProductLinkInvitation | Link invitations |
| ThirdPartyAppAnalyticsLinkService | RegenerateShareableLinkId | App analytics links |

## Intentionally Skipped Fields

The following API fields are not exposed because they serve no purpose for MCP callers:

| Field | Services Affected | Reason |
|-------|-------------------|--------|
| `AdditionalApplicationInfo` (`insights_application_info`, `application_info`, `reach_application_info`) | audience_insights (8 RPCs), benchmarks (5 RPCs), content_creator_insights (2 RPCs), reach_plan (6 RPCs) | Internal Google application tracking metadata used to identify the calling application. Not relevant for third-party MCP callers. |

## Development

```bash
# Run the server
uv run main.py

# Run tests
uv run pytest

# Type checking
uv run pyright

# Format code
uv run ruff format .
```

## Contributing

1. All code must have full type annotations (0 pyright errors)
2. Every service needs tests covering all methods
3. Tool wrapper docstrings must document all enum values and parameter formats — the LLM reads these to decide how to use the tool
4. Format with `uv run ruff format .` before committing

## License

MIT - see [LICENSE](LICENSE)

## Acknowledgments

This project was originally forked from [promobase/google-ads-mcp](https://github.com/promobase/google-ads-mcp). It has since been rewritten to support Google Ads API v23 with 100% service coverage, full type safety, and standardized architecture.

## Disclaimer

This is an unofficial implementation and is not affiliated with, endorsed by, or supported by Google.
