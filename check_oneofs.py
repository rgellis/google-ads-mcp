import os, re, importlib

# Services that use oneof patterns (criterion types, asset types, bidding strategies, etc.)
# Check each service's main proto resource for oneof fields

services_to_check = {
    # Criterion services
    "ad_group_criterion": {
        "proto": "google.ads.googleads.v23.resources.types.ad_group_criterion",
        "class": "AdGroupCriterion",
        "service_file": "src/services/ad_group/ad_group_criterion_service.py",
    },
    "customer_negative_criterion": {
        "proto": "google.ads.googleads.v23.resources.types.customer_negative_criterion",
        "class": "CustomerNegativeCriterion",
        "service_file": "src/services/targeting/customer_negative_criterion_service.py",
    },
    "shared_criterion": {
        "proto": "google.ads.googleads.v23.resources.types.shared_criterion",
        "class": "SharedCriterion",
        "service_file": "src/services/shared/shared_criterion_service.py",
    },
    # Ad types
    "ad": {
        "proto": "google.ads.googleads.v23.resources.types.ad",
        "class": "Ad",
        "service_file": "src/services/ad_group/ad_service.py",
    },
    # Extension/asset types
    "asset": {
        "proto": "google.ads.googleads.v23.resources.types.asset",
        "class": "Asset",
        "service_file": "src/services/assets/asset_service.py",
    },
    # Bidding strategy types
    "campaign_bidding": {
        "proto": "google.ads.googleads.v23.resources.types.campaign",
        "class": "Campaign",
        "service_file": "src/services/campaign/campaign_service.py",
    },
    # Feed/extension types
    "ad_group_bid_modifier": {
        "proto": "google.ads.googleads.v23.resources.types.ad_group_bid_modifier",
        "class": "AdGroupBidModifier",
        "service_file": "src/services/ad_group/ad_group_bid_modifier_service.py",
    },
    "campaign_bid_modifier": {
        "proto": "google.ads.googleads.v23.resources.types.campaign_bid_modifier",
        "class": "CampaignBidModifier",
        "service_file": "src/services/campaign/campaign_bid_modifier_service.py",
    },
}

for name, config in services_to_check.items():
    try:
        mod = importlib.import_module(config["proto"])
        cls = getattr(mod, config["class"])

        # Get all fields
        all_fields = {f.name: f for f in cls._meta.fields.values()}

        # Get oneof groups
        oneofs = {}
        for field_name, field in all_fields.items():
            if hasattr(field, "oneof") and field.oneof:
                oneof_name = field.oneof
                if oneof_name not in oneofs:
                    oneofs[oneof_name] = []
                oneofs[oneof_name].append(field_name)

        # Also check for criterion-like fields (fields that are message types ending in Info)
        info_fields = [
            f
            for f in all_fields.keys()
            if f
            not in (
                "resource_name",
                "status",
                "type_",
                "campaign",
                "ad_group",
                "criterion_id",
                "display_name",
                "bid_modifier",
                "negative",
                "name",
                "id",
                "tracking_url_template",
                "final_urls",
                "final_mobile_urls",
                "url_custom_parameters",
            )
        ]

        # Read service file to see what's implemented
        with open(config["service_file"]) as f:
            svc_content = f.read()

        # Find which fields are referenced in the service
        covered = []
        not_covered = []
        for field in info_fields:
            # Check if the field name appears in the service (criterion.field = or .field = etc.)
            if (
                f".{field}" in svc_content
                or f"'{field}'" in svc_content
                or f'"{field}"' in svc_content
            ):
                covered.append(field)
            else:
                not_covered.append(field)

        if oneofs:
            print(f"\n{'=' * 70}")
            print(f"SERVICE: {name} ({config['class']})")
            print(f"File: {config['service_file']}")
            for oneof_name, fields in oneofs.items():
                covered_in_oneof = [f for f in fields if f in covered]
                missing_in_oneof = [f for f in fields if f in not_covered]
                if missing_in_oneof:
                    print(
                        f"  ONEOF '{oneof_name}': {len(covered_in_oneof)}/{len(fields)} covered"
                    )
                    print(f"    COVERED: {covered_in_oneof}")
                    print(f"    MISSING: {missing_in_oneof}")
                else:
                    print(
                        f"  ONEOF '{oneof_name}': {len(fields)}/{len(fields)} fully covered"
                    )

    except Exception as e:
        print(f"\nERROR checking {name}: {e}")
