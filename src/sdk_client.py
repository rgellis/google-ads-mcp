"""Google Ads SDK client for MCP server."""

from typing import Optional, Dict, Any

import yaml
from google.ads.googleads.client import GoogleAdsClient

from src.utils import get_logger

logger = get_logger(__name__)


class GoogleAdsSdkClient:
    """SDK client for Google Ads supporting both service account and OAuth authentication.

    Auth mode is auto-detected from the YAML config:
    - If ``refresh_token`` is present → OAuth (client_id, client_secret, refresh_token)
    - Otherwise → service account (json_key_file_path)
    """

    def __init__(self, config_path: str = "./env/google-ads.yaml"):
        """Initialize the SDK client with configuration."""
        self.config_path = config_path
        self._client: Optional[GoogleAdsClient] = None

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        with open(self.config_path, "r") as f:
            config = yaml.safe_load(f)

        if "developer_token" not in config:
            raise ValueError("Missing required field in config: developer_token")

        has_oauth = "refresh_token" in config
        has_service_account = "json_key_file_path" in config

        if has_oauth:
            for field in ["client_id", "client_secret"]:
                if field not in config:
                    raise ValueError(f"Missing required field for OAuth config: {field}")
        elif has_service_account:
            pass
        else:
            raise ValueError(
                "Config must contain either 'refresh_token' (OAuth) "
                "or 'json_key_file_path' (service account)"
            )

        return config

    @property
    def client(self) -> GoogleAdsClient:
        """Get or create the Google Ads client."""
        if self._client is None:
            config = self._load_config()

            client_config: Dict[str, Any] = {
                "developer_token": config["developer_token"],
                "use_proto_plus": True,
            }

            if "refresh_token" in config:
                client_config["client_id"] = config["client_id"]
                client_config["client_secret"] = config["client_secret"]
                client_config["refresh_token"] = config["refresh_token"]
                logger.info("Using OAuth refresh token authentication")
            else:
                client_config["json_key_file_path"] = config["json_key_file_path"]
                logger.info("Using service account authentication")

            if "login_customer_id" in config:
                login_customer_id = str(config["login_customer_id"]).replace("-", "")
                client_config["login_customer_id"] = login_customer_id

            self._client = GoogleAdsClient.load_from_dict(client_config)
            logger.info("Google Ads SDK client initialized successfully")

        return self._client

    def close(self) -> None:
        """Close the client and clean up resources."""
        if self._client:
            # The SDK client doesn't have an explicit close method
            # but we can clear the reference
            self._client = None
            logger.info("Google Ads SDK client closed")


# Global client instance
_sdk_client: Optional[GoogleAdsSdkClient] = None


def get_sdk_client() -> GoogleAdsSdkClient:
    """Get the global SDK client instance."""
    global _sdk_client
    if _sdk_client is None:
        raise RuntimeError("SDK client not initialized. Call set_sdk_client first.")
    return _sdk_client


def set_sdk_client(client: GoogleAdsSdkClient) -> None:
    """Set the global SDK client instance."""
    global _sdk_client
    _sdk_client = client
