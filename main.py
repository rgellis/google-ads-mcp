"""Main entry point for Google Ads MCP server."""

import argparse
import asyncio
import signal
import sys
from contextlib import asynccontextmanager
from types import FrameType
from typing import Any, AsyncGenerator, Optional, Set

from fastmcp import Context, FastMCP

from src.sdk_client import GoogleAdsSdkClient, get_sdk_client, set_sdk_client
from src.servers.account import (
    account_budget_proposal_server,
    account_link_server,
    billing_setup_server,
    customer_client_link_server,
    customer_lifecycle_goal_server,
    customer_manager_link_server,
    customer_sk_ad_network_server,
    customer_user_access_invitation_server,
    customer_user_access_server,
    data_link_server,
    goal_server,
    identity_verification_server,
    incentive_server,
    payments_account_server,
    product_link_invitation_server,
    product_link_server,
    third_party_app_analytics_link_server,
)
from src.servers.assets import (
    ad_group_asset_server,
    ad_group_asset_set_server,
    asset_generation_server,
    asset_group_asset_server,
    asset_group_listing_group_filter_server,
    asset_group_server,
    asset_group_signal_server,
    asset_server,
    asset_set_asset_server,
    asset_set_server,
    automatically_created_asset_removal_server,
    campaign_asset_server,
    campaign_asset_set_server,
    customer_asset_server,
    customer_asset_set_server,
    youtube_video_upload_server,
)
from src.servers.bidding import (
    ad_group_bid_modifier_server,
    bidding_data_exclusion_server,
    bidding_seasonality_adjustment_server,
    bidding_strategy_server,
    campaign_bid_modifier_server,
)
from src.servers.conversion import (
    campaign_conversion_goal_server,
    conversion_adjustment_upload_server,
    conversion_custom_variable_server,
    conversion_goal_campaign_config_server,
    conversion_upload_server,
    conversion_value_rule_server,
    conversion_value_rule_set_server,
    custom_conversion_goal_server,
    customer_conversion_goal_server,
    offline_user_data_job_server,
    remarketing_action_server,
)
from src.servers.core import (
    ad_group_ad_server,
    ad_group_server,
    ad_server,
    budget_server,
    campaign_server,
    conversion_server,
    customer_service_server,
    google_ads_server,
    keyword_server,
)
from src.servers.customizers import (
    ad_group_criterion_customizer_server,
    ad_group_customizer_server,
    ad_parameter_server,
    campaign_customizer_server,
    customer_customizer_server,
    customizer_sdk_server,
)
from src.servers.experiments import (
    campaign_draft_server,
    experiment_arm_server,
    experiment_server,
)
from src.servers.organization import (
    ad_group_ad_label_server,
    ad_group_criterion_label_server,
    ad_group_label_server,
    campaign_label_server,
    campaign_shared_set_server,
    customer_label_server,
    label_server,
    shared_criterion_server,
    shared_set_server,
)
from src.servers.other import (
    batch_job_server,
    campaign_goal_config_server,
    campaign_group_server,
    campaign_lifecycle_goal_server,
    local_services_lead_server,
    reservation_server,
    smart_campaign_server,
    smart_campaign_setting_server,
    user_data_server,
)
from src.servers.planning import (
    benchmarks_server,
    brand_suggestion_server,
    keyword_plan_ad_group_keyword_server,
    keyword_plan_ad_group_server,
    keyword_plan_campaign_keyword_server,
    keyword_plan_campaign_server,
    keyword_plan_idea_server,
    keyword_plan_server,
    keyword_theme_constant_server,
    reach_plan_server,
    recommendation_subscription_server,
    travel_asset_suggestion_server,
)
from src.servers.reporting import (
    audience_insights_server,
    content_creator_insights_server,
    google_ads_field_server,
    invoice_server,
    recommendation_server,
    search_server,
    shareable_preview_server,
)
from src.servers.targeting import (
    ad_group_criterion_server,
    audience_server,
    campaign_criterion_server,
    custom_audience_server,
    custom_interest_server,
    customer_negative_criterion_server,
    geo_target_constant_server,
    user_list_customer_type_server,
    user_list_server,
)
from src.utils import get_logger, load_dotenv

logger = get_logger(__name__)

load_dotenv()


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Google Ads MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available server groups:
  core        - Essential services (customer, campaign, budget, ad groups, keywords, ads)
  assets      - Asset management services
  targeting   - Targeting and audience services
  bidding     - Bidding strategies and modifiers
  planning    - Keyword planning and reach planning
  experiments - Campaign experiments and drafts
  reporting   - Reporting and field metadata
  conversion  - Conversion tracking and uploads
  organization - Labels and shared sets
  customizers - Customizer attributes and parameters
  account     - Account management and linking
  other       - Smart campaigns, batch jobs, user data

Examples:
  uv run main.py                    # Mount all servers
  uv run main.py --groups all       # Mount all servers
  uv run main.py --groups core      # Mount only core services
  uv run main.py --groups core,assets,targeting  # Mount specific groups
""",
    )

    parser.add_argument(
        "--groups",
        type=str,
        default="core",
        help="Comma-separated list of server groups to mount (default: core)",
    )

    return parser.parse_args()


@asynccontextmanager
async def lifespan(app: Any) -> AsyncGenerator[None, None]:  # noqa: ARG001
    """Manage Google Ads SDK client lifecycle."""
    logger.info("Starting Google Ads SDK API MCP server...")
    client = None
    try:
        client = GoogleAdsSdkClient()
        set_sdk_client(client)
        logger.info("Google Ads SDK client initialized successfully")
        yield
    finally:
        logger.info("Shutting down Google Ads SDK API MCP server...")
        if client:
            client.close()


# Initialize main MCP server with lifespan
mcp = FastMCP(
    name="google-ads-mcp",
    instructions="""This is a Google Ads MCP server that provides API tools for managing Google Ads accounts.

    It includes tools for:
    - Customer management (create customers, list accessible customers)
    - Campaign management (create and update campaigns)
    - Budget management (create and update campaign budgets)
    - Ad group management (create and update ad groups)
    - Keyword management (add, update, and remove keywords)
    - Ad management (create responsive search ads and expanded text ads)
    - Conversion tracking (create and update conversion actions)
    - Search and reporting (search campaigns, ad groups, keywords, and execute GAQL queries)
    - Asset management (create text, image, and video assets)
    - Bidding strategies (create Target CPA, Target ROAS, and other automated bidding strategies)
    - Ad extensions (create sitelinks, callouts, call extensions, and structured snippets)
    - User lists (create remarketing lists, customer match lists, and similar audiences)
    - Geo targeting (search and suggest locations for targeting)
    - Recommendations (get and apply optimization recommendations)
    - Campaign criteria (manage campaign-level targeting and exclusions)
    - Ad group criteria (manage keywords, audiences, and demographics at ad group level)
    - Account-level exclusions (negative keywords, placements, and content labels)
    - Shared sets (create and manage shared negative keyword/placement lists)
    - Labels (organize campaigns, ad groups, and ads with color-coded labels)
    - Field metadata (discover available fields and validate queries)
    - Custom interests (create custom affinity and intent audiences)
    - Custom audiences (create custom segments with keywords, URLs, apps, and places)
    - Keyword planning (research keywords and get search volume data)
    - Experiments (A/B test campaign changes)
    - Offline conversion uploads (track offline sales from clicks and calls)
    - Smart campaigns (simplified campaign management with AI suggestions)
    - Remarketing actions (create and manage remarketing tags)
    - Conversion adjustments (restate or retract conversions)
    - Campaign bid modifiers (adjust bids by device, location, schedule, demographics)
    - Ad group bid modifiers (ad group-level bid adjustments)
    - Campaign shared sets (link campaigns to shared negative lists)
    - Billing setup (configure billing and payments accounts)

    The Google Ads SDK client is initialized automatically when the server starts.
    All customer IDs can be provided with or without hyphens.

    This implementation uses the Google Ads Python SDK for all operations with full type safety.

    Key targeting rules:
    - Search campaigns: Demographic bid adjustments (age, gender, income) must be done at the AD GROUP level, not campaign level. Campaign-level demographics on Search are exclusion-only.
    - Custom audience and custom affinity criteria only work on Display, Demand Gen, and Video campaigns. For Search campaigns, use user_list or user_interest criteria instead.
    - Campaign-level keywords are negative (exclusion) only. For positive keyword targeting, use ad group criterion tools.
    - Ad schedules, devices, carriers, and proximity targeting are campaign-level only.
    - bid_modifier is a multiplier: 1.0 = no change, 1.5 = +50%, 0.5 = -50%, 0.0 = exclude.""",
    lifespan=lifespan,
)


# Define server groups with shortened prefixes to stay under Claude's 64-char tool name limit.
# Tool names are "{prefix}_{server_tool_name}", so prefixes must be short.
SERVER_GROUPS = {
    "core": [
        ("customer", customer_service_server),
        ("campaign", campaign_server),
        ("budget", budget_server),
        ("ad_group", ad_group_server),
        ("keyword", keyword_server),
        ("ad", ad_server),
        ("ag_ad", ad_group_ad_server),
        ("conversion", conversion_server),
        ("gads", google_ads_server),
    ],
    "assets": [
        ("asset", asset_server),
        ("asset_group", asset_group_server),
        ("assetgrp_asset", asset_group_asset_server),
        ("assetgrp_signal", asset_group_signal_server),
        ("assetgrp_lgf", asset_group_listing_group_filter_server),
        ("asset_set", asset_set_server),
        ("asset_set_asset", asset_set_asset_server),
        ("ag_asset", ad_group_asset_server),
        ("ag_asset_set", ad_group_asset_set_server),
        ("camp_asset", campaign_asset_server),
        ("camp_asset_set", campaign_asset_set_server),
        ("cust_asset", customer_asset_server),
        ("cust_asset_set", customer_asset_set_server),
        ("asset_gen", asset_generation_server),
        ("auto_asset_rm", automatically_created_asset_removal_server),
        ("yt_upload", youtube_video_upload_server),
    ],
    "targeting": [
        ("camp_criterion", campaign_criterion_server),
        ("ag_criterion", ad_group_criterion_server),
        ("cust_neg_crit", customer_negative_criterion_server),
        ("geo_target", geo_target_constant_server),
        ("audience", audience_server),
        ("custom_interest", custom_interest_server),
        ("custom_audience", custom_audience_server),
        ("user_list", user_list_server),
        ("ul_cust_type", user_list_customer_type_server),
    ],
    "bidding": [
        ("bid_strategy", bidding_strategy_server),
        ("camp_bid_mod", campaign_bid_modifier_server),
        ("ag_bid_mod", ad_group_bid_modifier_server),
        ("bid_exclusion", bidding_data_exclusion_server),
        ("bid_season_adj", bidding_seasonality_adjustment_server),
    ],
    "planning": [
        ("kw_plan", keyword_plan_server),
        ("kw_plan_idea", keyword_plan_idea_server),
        ("kw_plan_ag", keyword_plan_ad_group_server),
        ("kw_plan_camp", keyword_plan_campaign_server),
        ("kw_plan_ag_kw", keyword_plan_ad_group_keyword_server),
        ("kw_plan_camp_kw", keyword_plan_campaign_keyword_server),
        ("reach_plan", reach_plan_server),
        ("brand_suggest", brand_suggestion_server),
        ("kw_theme", keyword_theme_constant_server),
        ("travel_suggest", travel_asset_suggestion_server),
        ("rec_sub", recommendation_subscription_server),
        ("benchmarks", benchmarks_server),
    ],
    "experiments": [
        ("experiment", experiment_server),
        ("exp_arm", experiment_arm_server),
        ("camp_draft", campaign_draft_server),
    ],
    "reporting": [
        ("search", search_server),
        ("gads_field", google_ads_field_server),
        ("recommend", recommendation_server),
        ("invoice", invoice_server),
        ("aud_insights", audience_insights_server),
        ("share_preview", shareable_preview_server),
        ("creator_ins", content_creator_insights_server),
    ],
    "conversion": [
        ("conv_upload", conversion_upload_server),
        ("conv_adj_upload", conversion_adjustment_upload_server),
        ("conv_value_rule", conversion_value_rule_server),
        ("conv_rule_set", conversion_value_rule_set_server),
        ("conv_custom_var", conversion_custom_variable_server),
        ("conv_goal_config", conversion_goal_campaign_config_server),
        ("custom_conv_goal", custom_conversion_goal_server),
        ("cust_conv_goal", customer_conversion_goal_server),
        ("camp_conv_goal", campaign_conversion_goal_server),
        ("offline_data_job", offline_user_data_job_server),
        ("remarket", remarketing_action_server),
    ],
    "organization": [
        ("label", label_server),
        ("camp_label", campaign_label_server),
        ("ag_label", ad_group_label_server),
        ("ag_ad_label", ad_group_ad_label_server),
        ("ag_crit_label", ad_group_criterion_label_server),
        ("cust_label", customer_label_server),
        ("shared_set", shared_set_server),
        ("shared_crit", shared_criterion_server),
        ("camp_shared_set", campaign_shared_set_server),
    ],
    "customizers": [
        ("customizer_attr", customizer_sdk_server),
        ("cust_customizer", customer_customizer_server),
        ("camp_customizer", campaign_customizer_server),
        ("ag_customizer", ad_group_customizer_server),
        ("ag_crit_custom", ad_group_criterion_customizer_server),
        ("ad_param", ad_parameter_server),
    ],
    "account": [
        ("user_access", customer_user_access_server),
        ("user_invite", customer_user_access_invitation_server),
        ("client_link", customer_client_link_server),
        ("manager_link", customer_manager_link_server),
        ("acct_link", account_link_server),
        ("budget_proposal", account_budget_proposal_server),
        ("billing", billing_setup_server),
        ("payments", payments_account_server),
        ("id_verify", identity_verification_server),
        ("product_link", product_link_server),
        ("prod_link_inv", product_link_invitation_server),
        ("data_link", data_link_server),
        ("goal", goal_server),
        ("incentive", incentive_server),
        ("cust_lifecycle", customer_lifecycle_goal_server),
        ("sk_ad_network", customer_sk_ad_network_server),
        ("app_analytics", third_party_app_analytics_link_server),
    ],
    "other": [
        ("smart_camp", smart_campaign_server),
        ("smart_setting", smart_campaign_setting_server),
        ("batch_job", batch_job_server),
        ("user_data", user_data_server),
        ("local_lead", local_services_lead_server),
        ("camp_group", campaign_group_server),
        ("camp_goal_cfg", campaign_goal_config_server),
        ("camp_lifecycle", campaign_lifecycle_goal_server),
        ("reservation", reservation_server),
    ],
}


def get_servers_to_mount(groups_arg: str) -> Set[tuple[str, Any]]:
    """Get the set of servers to mount based on the groups argument."""
    if groups_arg == "all":
        # Return all servers from all groups
        all_servers = set()
        for servers in SERVER_GROUPS.values():
            all_servers.update(servers)
        return all_servers

    # Parse requested groups
    requested_groups = [g.strip() for g in groups_arg.split(",")]
    servers_to_mount = set()

    for group in requested_groups:
        if group in SERVER_GROUPS:
            servers_to_mount.update(SERVER_GROUPS[group])
        else:
            logger.warning(f"Unknown server group: {group}")

    return servers_to_mount


# Parse command line arguments
args = parse_arguments()
servers_to_mount = get_servers_to_mount(args.groups)

# Log which groups are being mounted
if args.groups == "all":
    logger.info("Mounting all server groups")
else:
    logger.info(f"Mounting server groups: {args.groups}")

# Mount the selected servers
for prefix, server in servers_to_mount:
    mcp.mount(server, prefix=prefix)


@mcp.tool
async def check_sdk_client_status(ctx: Context) -> str:  # noqa: ARG001
    """Check if the Google Ads SDK client is initialized."""
    try:
        client = get_sdk_client()
        if client:
            return "Google Ads SDK client is initialized and ready"
    except Exception:
        pass
    return "Google Ads SDK client is not initialized"


shutdown_event = asyncio.Event()


def signal_handler(signum: int, frame: Optional[FrameType]) -> None:
    """Handle shutdown signals gracefully."""
    logger.info(f"Received signal {signum}, shutting down...")
    # Set the shutdown event instead of sys.exit
    shutdown_event.set()

    # Force exit after a timeout if graceful shutdown fails
    def force_exit():
        logger.warning("Force exiting after timeout...")
        os._exit(0)

    import threading

    threading.Timer(2.0, force_exit).start()


async def run_with_shutdown():
    """Run the MCP server with graceful shutdown support."""
    tools = await mcp.get_tools()
    logger.info(
        f"Registered tools: {len(tools)} tools from {len(servers_to_mount)} servers"
    )
    # Create a task for the server
    server_task = asyncio.create_task(mcp.run_async(transport="stdio"))

    # Wait for either the server to complete or shutdown signal
    shutdown_task = asyncio.create_task(shutdown_event.wait())

    _, pending = await asyncio.wait(
        [server_task, shutdown_task], return_when=asyncio.FIRST_COMPLETED
    )

    # Cancel any pending tasks
    for task in pending:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    logger.info("Server stopped gracefully")


if __name__ == "__main__":
    import os

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        asyncio.run(run_with_shutdown())
    except KeyboardInterrupt:
        logger.info("Received KeyboardInterrupt during startup")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
