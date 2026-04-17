"""Reporting, insights, and metadata servers."""

from src.servers import create_server
from src.services.account.invoice_service import register_invoice_tools
from src.services.audiences.audience_insights_service import (
    register_audience_insights_tools,
)
from src.services.audiences.content_creator_insights_service import (
    register_content_creator_insights_tools,
)
from src.services.metadata.google_ads_field_service import (
    register_google_ads_field_tools,
)
from src.services.metadata.search_service import register_search_tools
from src.services.metadata.shareable_preview_service import (
    register_shareable_preview_tools,
)
from src.services.planning.recommendation_service import register_recommendation_tools

search_server = create_server(register_search_tools)
google_ads_field_server = create_server(register_google_ads_field_tools)
recommendation_server = create_server(register_recommendation_tools)
invoice_server = create_server(register_invoice_tools)
audience_insights_server = create_server(register_audience_insights_tools)
shareable_preview_server = create_server(register_shareable_preview_tools)
content_creator_insights_server = create_server(register_content_creator_insights_tools)
