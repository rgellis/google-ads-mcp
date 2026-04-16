"""Keyword theme constant service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.services.services.keyword_theme_constant_service import (
    KeywordThemeConstantServiceClient,
)
from google.ads.googleads.v23.services.types.keyword_theme_constant_service import (
    SuggestKeywordThemeConstantsRequest,
    SuggestKeywordThemeConstantsResponse,
)

from src.sdk_client import get_sdk_client
from src.utils import get_logger, serialize_proto_message

logger = get_logger(__name__)


class KeywordThemeConstantService:
    """Service for suggesting keyword theme constants for Smart campaigns."""

    def __init__(self) -> None:
        self._client: Optional[KeywordThemeConstantServiceClient] = None

    @property
    def client(self) -> KeywordThemeConstantServiceClient:
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("KeywordThemeConstantService")
        assert self._client is not None
        return self._client

    async def suggest_keyword_theme_constants(
        self,
        ctx: Context,
        query_text: str,
        country_code: Optional[str] = None,
        language_code: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Suggest keyword theme constants based on a query.

        Args:
            ctx: FastMCP context
            query_text: Text to get theme suggestions for
            country_code: Optional two-letter country code
            language_code: Optional language code

        Returns:
            Suggested keyword theme constants
        """
        try:
            request = SuggestKeywordThemeConstantsRequest()
            request.query_text = query_text
            if country_code:
                request.country_code = country_code
            if language_code:
                request.language_code = language_code

            response: SuggestKeywordThemeConstantsResponse = (
                self.client.suggest_keyword_theme_constants(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Got keyword theme suggestions for: {query_text}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to suggest keyword themes: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_keyword_theme_constant_tools(
    service: KeywordThemeConstantService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the keyword theme constant service."""
    tools: List[Callable[..., Awaitable[Any]]] = []

    async def suggest_keyword_theme_constants(
        ctx: Context,
        query_text: str,
        country_code: Optional[str] = None,
        language_code: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Suggest keyword theme constants for Smart campaigns.

        Args:
            query_text: Text to get theme suggestions for
            country_code: Optional two-letter country code (e.g. "US")
            language_code: Optional language code (e.g. "en")

        Returns:
            Suggested keyword theme constants with display names
        """
        return await service.suggest_keyword_theme_constants(
            ctx=ctx,
            query_text=query_text,
            country_code=country_code,
            language_code=language_code,
        )

    tools.append(suggest_keyword_theme_constants)
    return tools


def register_keyword_theme_constant_tools(
    mcp: FastMCP[Any],
) -> KeywordThemeConstantService:
    """Register keyword theme constant tools with the MCP server."""
    service = KeywordThemeConstantService()
    tools = create_keyword_theme_constant_tools(service)
    for tool in tools:
        mcp.tool(tool)
    return service
